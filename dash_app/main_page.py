from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Union

import dash_bootstrap_components as dbc
import pandas as pd
from components import Button, Dropdown, Modal, vstack
from dash import Input, Output, State
from dash.dash_table import DataTable
from dash.dcc import Store
from dash.exceptions import PreventUpdate
from dash.html import Div

from private_utils.dash_components import (BaseComponent, FontWeight, Style,
                                           generate_uuid)

if TYPE_CHECKING:
    from dash import Dash

# type definition for hinting
_dict_of_str = Dict[str, str]
_list_of_str = List[str]
_column_store = Dict[str, Union[_dict_of_str, _list_of_str]]


class Table(BaseComponent):
    # TODO make using table only and no store ?
    def __init__(self, app: 'Dash', component_id: str,
                 data: List[Dict[str, Any]],
                 columns_id: _dict_of_str,
                 columns_type: _dict_of_str,
                 index_name: str,
                 new_col_format: str = 'col_{}',
                 editable: bool = False,
                 include_total: bool = False,
                 total_label: str = 'Total'):
        super().__init__(component_id=component_id, app=app)

        self.data_store = Store(id=self.generate_id('data_store'), data=data)

        columns_order = list(columns_id.keys())
        columns_store_values = Table.to_columns_store(columns_id, columns_type, columns_order)
        self.columns_store = Store(id=self.generate_id('columns_store'), data=columns_store_values)
        columns = self.to_datatable_columns(columns_store_values)

        self.include_total = include_total
        self.total_label = total_label
        self.index_name = index_name
        self.new_col_format = new_col_format
        self.editable = editable

        style_data_conditional = []
        if include_total:
            total_condition = (Style({'if': {'filter_query': f"{{{self.index_name}}} = {total_label}"}})
                               .font_weight(FontWeight.bold))
            style_data_conditional.append(total_condition)

        self.table = DataTable(id=self.generate_id('table'),
                               data=data, columns=columns,
                               editable=editable,
                               style_data_conditional=style_data_conditional)

    @classmethod
    def from_file_path(cls, app: 'Dash', component_id: str,
                       file_path: str, index_col: int = 0,
                       editable: bool = False, include_total: bool = False, ):
        """Instantiate the Table from an initial csv file."""
        dataframe = pd.read_csv(file_path).apply(pd.to_numeric, errors='ignore')
        columns_id = {generate_uuid(): column for column in dataframe.columns}

        dataframe.columns = columns_id.keys()
        index_name = dataframe.columns[index_col]
        columns_type = {key: 'text' if value == object else 'numeric'
                        for key, value in dataframe.dtypes.to_dict().items()}

        instance = cls(app=app, component_id=component_id,
                       data=cls.to_records(dataframe),
                       columns_id=columns_id,
                       columns_type=columns_type,
                       index_name=index_name,
                       editable=editable,
                       include_total=include_total)
        return instance

    @staticmethod
    def to_columns_store(columns_id: _dict_of_str, columns_type: _dict_of_str,
                         columns_order: _list_of_str) -> _column_store:
        """Returns columns values in the suitable format to be stored."""
        return {'id': columns_id, 'type': columns_type, 'order': columns_order}

    @staticmethod
    def from_columns_store(columns_store: _column_store) -> Tuple[_dict_of_str, _dict_of_str, _list_of_str]:
        """Extract columns values from the store format."""
        return columns_store['id'], columns_store['type'], columns_store['order']

    @staticmethod
    def to_datatable_columns(columns_store: _column_store) -> List[_dict_of_str]:
        """Returns columns values in the format expected by Dash DataTable."""
        columns_id, columns_type, columns_order = Table.from_columns_store(columns_store)
        return [{'name': columns_id[key], 'id': key, 'type': columns_type[key]}
                for key in columns_order]

    def to_dropdown_options(self, columns_store: _column_store) -> List[_dict_of_str]:
        columns_id, _, columns_order = self.from_columns_store(columns_store)
        return [{'label': columns_id[key], 'value': key} for key in columns_order if key != self.index_name]

    @staticmethod
    def to_records(dataframe: pd.DataFrame) -> List[_dict_of_str]:
        """Returns the dataframe as a list of records."""
        return dataframe.to_dict('records')

    def add_new_column(self, columns_store: _column_store, n: int) -> _column_store:
        """Append a new column to the existing table."""
        columns_id, columns_type, columns_order = Table.from_columns_store(columns_store)
        new_column_name = self.new_col_format.format(n)
        new_id = generate_uuid()

        columns_id[new_id] = new_column_name
        columns_type[new_id] = 'numeric'
        columns_order.append(new_id)
        return Table.to_columns_store(columns_id, columns_type, columns_order)

    @staticmethod
    def _get_value_from_record(record, key):
        value = record.get(key, 0)
        if value is None or value == '':
            return 0
        return value

    def layout(self):
        """Returns layout."""
        return Div([self.table, self.data_store, self.columns_store],
                   style=Style().margin('1rem'))

    def register_callbacks(self, ):
        """Register callbacks."""

        @self.app.callback(Output(self.table, 'columns'),
                           Input(self.columns_store, 'data'))
        def _update_table_columns(columns_store: Dict[str, Dict[str, Any]]):
            return self.to_datatable_columns(columns_store)

        @self.app.callback(Output(self.table, 'data'),
                           Input(self.data_store, 'data'),
                           State(self.columns_store, 'data'))
        def _update_table_data_from_store(records: List[_dict_of_str], columns_store: _column_store):
            if self.include_total:
                # compute sum
                columns_id, columns_type, columns_order = Table.from_columns_store(columns_store)

                total = {key: sum([self._get_value_from_record(record, key)
                                   for record in records if columns_type[key] == 'numeric'])
                         for key in columns_id.keys()}
                total[self.index_name] = self.total_label
                records.append(total)
            return records

        @self.app.callback(Output(self.data_store, 'data'),
                           Input(self.table, 'data'))
        def _update_data_store_from_table(records: List[_dict_of_str]):
            if self.include_total:
                # remove total from records
                records = [record for record in records if record[self.index_name] != self.total_label]
            return records

        # @self.app.callback(Output(self.modal.modal, 'is_open'),
        #                    Input(self.duplicate_button, 'n_clicks'),
        #                    Input(self.modal.close, 'n_clicks'),
        #                    State(self.modal.modal, 'is_open'))
        # def display_modal(open_click: int, close_click: int, is_open: bool):
        #     if open_click or close_click:
        #         return not is_open
        pass


class MainPage(BaseComponent):
    """Main component."""

    def __init__(self, app, file_path: str, component_id: str = None):
        super().__init__(component_id=component_id, app=app)
        self.table = Table.from_file_path(component_id=self.generate_id('main_table'), app=app,
                                          file_path=file_path,
                                          include_total=True, editable=True)

        self.add_column_button = Button('Add new', id=self.generate_id('new_col_button'), n_clicks=0)
        self.duplicate_button = Button('Duplicate', id=self.generate_id('duplicate_button'), n_clicks=0)

        options = self.table.to_dropdown_options(self.table.columns_store.data)
        self.duplicate_dropdown = Dropdown(id=self.generate_id('duplicated_dropdown'),
                                           options=options,
                                           clearable=False)

        self.options_button = Button('\u2630', id=self.generate_id('table_options_button'), n_clicks=0)
        self.collapse_options = dbc.Collapse(
            Div([self.add_column_button, self.duplicate_dropdown, self.duplicate_button],
                style=Style().row_flex()),
            is_open=True)

        self.modal = Modal(component_id='modal')

    def layout(self):
        """Register layout."""

        first_table_options = Div(
            vstack([
                Div([dbc.Label('Table'), self.options_button], style=Style().row_flex()),
                self.collapse_options,
            ])
        )

        first_module = vstack([first_table_options, self.table, self.modal])
        return Div(first_module, style=Style().margin(left='18rem', right='2rem').pad(left='2rem', right='1rem'))

    def register_callbacks(self):
        """Register callbacks."""

        @self.app.callback(Output(self.table.columns_store, 'data'),
                           Input(self.add_column_button, 'n_clicks'),
                           State(self.table.columns_store, 'data'))
        def _add_column_to_stores(clicks: int, columns_store: Dict[str, Dict[str, Any]]):
            if clicks:
                return self.table.add_new_column(columns_store, clicks)

            raise PreventUpdate

        @self.app.callback(Output(self.duplicate_dropdown, 'options'),
                           Input(self.table.columns_store, 'data'))
        def _update_dropdown(columns_store: _column_store):
            return self.table.to_dropdown_options(columns_store)

        @self.app.callback(Output(self.collapse_options, 'is_open'),
                           Input(self.options_button, 'n_clicks'),
                           State(self.collapse_options, 'is_open'))
        def _trigger_collapse(clicks: int, is_open: bool):
            if clicks > 0:
                return not is_open
            raise PreventUpdate
