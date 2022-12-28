from collections import defaultdict
from typing import (TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Tuple,
                    Union)

import dash_bootstrap_components as dbc
import pandas as pd
import requests
from dash import Input, Output, State, dcc
from dash.dash_table import DataTable
from dash.exceptions import PreventUpdate
from dash.html import Div

from private_utils.dash_components import (BaseComponent, ClassName,
                                           ComponentFactory, FontWeight,
                                           LayoutComponent, Spacing, Style,
                                           generate_uuid)

if TYPE_CHECKING:
    from private_utils.dash_components import DashApp

Button = ComponentFactory(dbc.Button, className=ClassName().margin(Spacing.extra_small))
Dropdown = ComponentFactory(dcc.Dropdown, className=ClassName().margin(Spacing.extra_small))

# type definition for hinting
_dict_of_str = Dict[str, str]
_list_of_str = List[str]
_column_store = Dict[str, Union[_dict_of_str, _list_of_str]]


def hstack(iterable: Sequence, widths: Optional[Sequence] = None) -> Sequence:
    if widths is None:
        return [dbc.Col(arg) for arg in iterable]

    assert len(iterable) == len(widths), f"iterable and widths should have the same length, " \
                                         f"got {len(iterable)} and {len(widths)}"
    return [dbc.Col(arg, width=width) for arg, width in zip(iterable, widths)]


def vstack(iterable) -> Sequence:
    return [dbc.Row(arg) for arg in iterable]


class Modal(LayoutComponent):
    def __init__(self, component_id: Optional[str] = None):
        super().__init__(component_id=component_id)
        self.close = dbc.Button("CLOSE BUTTON", id=self.generate_id("close_btn"), className="ml-auto")
        self.modal = dbc.Modal(
            [
                dbc.ModalHeader("HEADER"),
                dbc.ModalBody("BODY OF MODAL"),
                dbc.ModalFooter(self.close),
            ],
            id=self.generate_id('window')
        )

    def layout(self):
        return self.modal


class TableWithControls(BaseComponent):
    """Table implementing some controls, such as add column, duplicate column..."""

    def __init__(self, app: 'DashApp', component_id: str,
                 data: List[Dict[str, Any]],
                 columns_id: _dict_of_str,
                 index_name: str,
                 new_col_format: str = 'col_{}',
                 editable: bool = False,
                 include_total: bool = False,
                 total_label: str = 'Total',
                 style_as_list_view=True, ):
        super().__init__(component_id=component_id, app=app)

        self.include_total = include_total
        self.total_label = total_label
        self.index_name = index_name
        self.new_col_format = new_col_format
        self.editable = editable
        self._default_columns_options = {'type': 'numeric', 'editable': editable}
        self.converter = TableFormatConverter(index_name=index_name,
                                              total_label=total_label,
                                              default_columns_options=self._default_columns_options)

        columns_order = list(columns_id.keys())
        self.columns_order = dcc.Store(id=self.generate_id('columns_order'), data=columns_order)
        columns = self.converter.columns_id_to_datatable_columns(columns_id, columns_order)

        style_data_conditional = []
        if include_total:
            total_condition = (Style({'if': {'filter_query': f"{{{self.index_name}}} = {total_label}"}})
                               .font_weight(FontWeight.bold))
            style_data_conditional.append(total_condition)

        style_cell_conditional = [Style({'if': {'column_id': f'{self.index_name}'}}).text_align('left')]

        self.table = DataTable(id=self.generate_id('table'),
                               data=data, columns=columns,
                               style_header=Style().background('whitesmoke').font_weight(FontWeight.bold),
                               style_data_conditional=style_data_conditional,
                               style_cell_conditional=style_cell_conditional,
                               style_as_list_view=style_as_list_view)

        # Defines options for the table.
        self.add_column_button = Button('Add new', id=self.generate_id('new_col_button'), n_clicks=0)
        self.duplicate_button = Button('Duplicate', id=self.generate_id('duplicate_button'), n_clicks=0)

        options = self.converter.datatable_columns_to_dropdown_options(self.table.columns)
        self.duplicate_dropdown = Dropdown(id=self.generate_id('duplicate_dropdown'),
                                           options=options,
                                           clearable=False)

        self.options_button = Button(id=self.generate_id('collapse_button'), n_clicks=0)
        self.collapse_options = dbc.Collapse(
            id=self.generate_id('collapse_options'),
            is_open=False)

    @classmethod
    def from_file_path(cls, app: 'DashApp', component_id: str,
                       file_path: str, index_col: int = 0,
                       editable: bool = False, include_total: bool = False,
                       total_label: str = 'Total',
                       style_as_list_view=True, ):
        """Instantiate the Table from an initial csv file."""
        dataframe = pd.read_csv(file_path).apply(pd.to_numeric, errors='ignore')
        columns_id = {generate_uuid(): column for column in dataframe.columns}

        dataframe.columns = pd.Index(columns_id.keys())
        index_name = dataframe.columns[index_col]

        instance = cls(app=app, component_id=component_id,
                       data=TableFormatConverter.dataframe_to_records(dataframe),
                       columns_id=columns_id,
                       index_name=index_name,
                       editable=editable,
                       include_total=include_total,
                       total_label=total_label,
                       style_as_list_view=style_as_list_view)
        return instance

    def add_new_column(self, n: int, columns: List[_dict_of_str], columns_order: _list_of_str) \
            -> Tuple[List[_dict_of_str], _list_of_str]:
        """Append a new column to the existing table."""
        new_column_name = self.new_col_format.format(n)
        new_id = generate_uuid()
        columns.append({'id': new_id, 'name': new_column_name, **self._default_columns_options})
        columns_order.append(new_id)
        return columns, columns_order

    @staticmethod
    def _get_value_from_record(record, key) -> Union[float, int]:
        value = record.get(key, 0)
        if value is None or value == '':
            return 0
        return value

    def layout(self):
        """Returns layout."""
        options_control = [self.add_column_button, self.duplicate_dropdown, self.duplicate_button]
        self.collapse_options.children = dbc.Card(
            dbc.CardBody(options_control, style=Style().row_flex().background('whitesmoke'))
        )
        self.options_button.style = Style().height('0.8rem')
        table_options = Div(
            vstack([self.options_button, self.collapse_options])
        )

        first_module = vstack([table_options, self.table, self.columns_order])
        return Div(first_module, style=Style().margin('1rem'))

    def register_callbacks(self, ):
        """Register callbacks."""

        @self.app.callback(Output(self.table, 'data'),
                           Input(self.table, 'data'),
                           State(self.table, 'columns'))
        def _update_table_data(records: List[_dict_of_str], columns: List[_dict_of_str]):
            """Update the table values when some has been edited."""
            if self.include_total:
                columns_id, columns_type = dict(), dict()
                for column in columns:
                    col_id, col_name, col_type = column['id'], column['name'], column['type']
                    columns_id[col_id], columns_type[col_id] = col_name, col_type

                # remove total from records
                records = [record for record in records if record[self.index_name] != self.total_label]
                # compute sum
                total = {key: sum([self._get_value_from_record(record, key)
                                   for record in records if columns_type[key] == 'numeric'])
                         for key in columns_id.keys()}
                total[self.index_name] = self.total_label
                records.append(total)
            return records

        @self.app.callback(Output(self.table, 'columns'),
                           Output(self.columns_order, 'data'),
                           Output(self.duplicate_dropdown, 'options'),
                           Input(self.add_column_button, 'n_clicks'),
                           State(self.table, 'columns'),
                           State(self.columns_order, 'data'))
        def _add_column_to_table(clicks: int, columns: List[_dict_of_str], columns_order: _list_of_str):
            """Append a column to the table. Also update the dropdown selection."""
            if clicks > 0:
                columns, columns_order = self.add_new_column(clicks, columns, columns_order)
                options = self.converter.datatable_columns_to_dropdown_options(columns)
                return columns, columns_order, options

            raise PreventUpdate

        @self.app.callback(Output(self.collapse_options, 'is_open'),
                           Input(self.options_button, 'n_clicks'),
                           State(self.collapse_options, 'is_open'))
        def _trigger_collapse(clicks: int, is_open: bool):
            """Collapse the option toolbar."""
            if clicks > 0:
                return not is_open
            raise PreventUpdate


class LinkedTable(BaseComponent):
    def __init__(self, app: 'DashApp', component_id: str, linked: TableWithControls):
        super().__init__(app=app, component_id=component_id)

        self.linked = linked
        self.converter = linked.converter
        table_component = linked.table
        self.table = DataTable(columns=table_component.columns,
                               style_header=Style().background('whitesmoke').font_weight(FontWeight.bold),
                               style_cell_conditional=table_component.style_cell_conditional)

    def layout(self):
        """Layout consists mostly of the table."""
        return Div(self.table, style=Style().margin('1rem'))

    def register_callbacks(self):
        @self.app.callback(Output(self.table, 'columns'),
                           Input(self.linked.table, 'columns'))
        def _synchronize_columns(columns: List[_dict_of_str]):
            return columns

        @self.app.callback(Output(self.table, 'data'),
                           Input(self.linked.table, 'data'))
        def _synchronize_data(data: List[_dict_of_str]):
            url = 'http://localhost:8000/compute'
            data = self.converter.records_to_dict_of_dict(data)
            response = requests.post(url, json=data)
            if response.status_code == 200:
                return self.converter.dict_of_dict_to_records(response.json())
            raise PreventUpdate


class TableFormatConverter:
    """Object converting the columns or data from one format to another."""

    def __init__(self, index_name, total_label, default_columns_options):
        self.total_label = total_label
        self.index_name = index_name
        self._default_columns_options = default_columns_options

    def columns_id_to_datatable_columns(self, columns_id: _dict_of_str, columns_order: _list_of_str):
        """Returns columns values in the format expected by Dash DataTable."""
        columns = [{'name': columns_id[self.index_name], 'id': self.index_name, 'type': 'text'}]

        columns.extend(
            [{'name': columns_id[key], 'id': key, **self._default_columns_options}
             for key in columns_order if key != self.index_name]
        )
        return columns

    def datatable_columns_to_dropdown_options(self, columns: List[_dict_of_str]) -> List[_dict_of_str]:
        """Format the columns in a list suitable for a dropdown control."""
        return [{'label': column['name'], 'value': column['id']} for column in columns
                if column['id'] != self.index_name]

    @staticmethod
    def dataframe_to_records(dataframe: pd.DataFrame) -> List[_dict_of_str]:
        """Returns the dataframe as a list of records."""
        # TODO remove nan ?
        return dataframe.to_dict('records')

    def records_to_dict_of_dict(self, records: List[_dict_of_str]) -> Dict[Any, Dict]:
        """From records (list of dictionary with column names as key) to nested dictionaries."""
        results = defaultdict(dict)
        for row in records:
            for key, value in row.items():
                index_value = row[self.index_name]
                if key != self.index_name and value != self.total_label:
                    results[key][index_value] = value

        return results

    def dict_of_dict_to_records(self, dict_of_dict: Dict[Any, Dict]) -> List[Dict[str, Any]]:
        """From nested dictionary to record format."""
        columns = dict_of_dict.keys()
        # implement row order feature ?
        rows = {key for inner_dict in dict_of_dict.values() for key in inner_dict.keys()}

        return [{self.index_name: row,  # add index name and iterate on column values
                 **{column: dict_of_dict[column][row] for column in columns if row in dict_of_dict[column]}}
                for row in rows]
