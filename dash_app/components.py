from typing import (TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Tuple,
                    Union)

import dash_bootstrap_components as dbc
import pandas as pd
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
                 columns_type: _dict_of_str,
                 index_name: str,
                 new_col_format: str = 'col_{}',
                 editable: bool = False,
                 include_total: bool = False,
                 total_label: str = 'Total'):
        super().__init__(component_id=component_id, app=app)

        columns_order = list(columns_id.keys())
        self.columns_order = dcc.Store(id=self.generate_id('columns_order'), data=columns_order)
        columns = self.to_datatable_columns(columns_id, columns_type, columns_order)

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

        # Defines options for the table.
        self.add_column_button = Button('Add new', id=self.generate_id('new_col_button'), n_clicks=0)
        self.duplicate_button = Button('Duplicate', id=self.generate_id('duplicate_button'), n_clicks=0)

        options = self.to_dropdown_options(self.table.columns)
        self.duplicate_dropdown = Dropdown(id=self.generate_id('duplicated_dropdown'),
                                           options=options,
                                           clearable=False)

        # self.options_button = Button('\u2630', id=self.generate_id('table_options_button'), n_clicks=0)
        self.options_button = Button(id=self.generate_id('table_options_button'), n_clicks=0)
        self.collapse_options = dbc.Collapse(
            id=self.generate_id('collapse_options'),
            is_open=False)

    @classmethod
    def from_file_path(cls, app: 'DashApp', component_id: str,
                       file_path: str, index_col: int = 0,
                       editable: bool = False, include_total: bool = False, ):
        """Instantiate the Table from an initial csv file."""
        dataframe = pd.read_csv(file_path).apply(pd.to_numeric, errors='ignore')
        columns_id = {generate_uuid(): column for column in dataframe.columns}

        dataframe.columns = pd.Index(columns_id.keys())
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
    def to_datatable_columns(columns_id: _dict_of_str, columns_type: _dict_of_str, columns_order: _list_of_str):
        """Returns columns values in the format expected by Dash DataTable."""
        return [{'name': columns_id[key], 'id': key, 'type': columns_type[key]}
                for key in columns_order]

    def to_dropdown_options(self, columns: List[_dict_of_str]) -> List[_dict_of_str]:
        """Format the columns in a list suitable for a dropdown control."""
        return [{'label': column['name'], 'value': column['id']} for column in columns
                if column['id'] != self.index_name]

    @staticmethod
    def to_records(dataframe: pd.DataFrame) -> List[_dict_of_str]:
        """Returns the dataframe as a list of records."""
        return dataframe.to_dict('records')

    def add_new_column(self, n: int, columns: List[_dict_of_str], columns_order: _list_of_str) \
            -> Tuple[List[_dict_of_str], _list_of_str]:
        """Append a new column to the existing table."""
        new_column_name = self.new_col_format.format(n)
        new_id = generate_uuid()
        columns.append({'id': new_id, 'name': new_column_name, 'type': 'numeric'})
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
        self.collapse_options.children = Div([self.add_column_button, self.duplicate_dropdown, self.duplicate_button],
                                             style=Style().row_flex())
        self.options_button.style = Style().height('0.4rem')
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
                columns_id = {column['id']: column['name'] for column in columns}
                columns_type = {column['id']: column['type'] for column in columns}

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
                options = self.to_dropdown_options(columns)
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
