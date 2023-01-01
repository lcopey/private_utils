from collections import defaultdict
from typing import (TYPE_CHECKING, Any, Callable, Dict, List, Optional,
                    Sequence, Tuple, Union)

import dash_bootstrap_components as dbc
import pandas as pd
import requests
from dash import Input, Output, State, ctx, dcc
from dash.dash_table import DataTable
from dash.exceptions import PreventUpdate
from dash.html import Div

from private_utils.dash_components import (BaseComponent, CallbackDispatcher,
                                           ClassName, ComponentFactory,
                                           FontWeight, LayoutComponent,
                                           Spacing, Style, generate_uuid)

if TYPE_CHECKING:
    from private_utils.dash_components import DashApp

Button = ComponentFactory(dbc.Button, className=ClassName().margin(Spacing.extra_small))
Dropdown = ComponentFactory(dcc.Dropdown, className=ClassName().margin(Spacing.extra_small))
DropdownMenu = ComponentFactory(dbc.DropdownMenu, className=ClassName().margin(Spacing.extra_small))

# type definition for hinting
_RecordType = List[Dict[str, Any]]
_ColumnsType = List[Dict[str, str]]
_DropdownOptionType = List[Dict[str, str]]


def hstack(iterable: Sequence, widths: Optional[Sequence] = None) -> Sequence:
    """Wraps the collection of controls with dbc.Col"""
    if widths is None:
        return [dbc.Col(arg) for arg in iterable]

    assert len(iterable) == len(widths), f"iterable and widths should have the same length, " \
                                         f"got {len(iterable)} and {len(widths)}"
    return [dbc.Col(arg, width=width) for arg, width in zip(iterable, widths)]


def vstack(iterable) -> Sequence:
    """Wraps the collection of controls with dbc.Row"""
    return [dbc.Row(arg) for arg in iterable]


class Modal(LayoutComponent):
    def __init__(self, component_id: Optional[str] = None):
        super().__init__(component_id=component_id)
        self.close = dbc.Button("CLOSE BUTTON", id=self.generate_id("close_btn"), className="ml-auto")
        self.modal = dbc.Modal(id=self.generate_id('window'))

    def layout(self):
        """Layout of modal control."""
        self.modal.children = [
            dbc.ModalHeader("HEADER"),
            dbc.ModalBody("BODY OF MODAL"),
            dbc.ModalFooter(self.close),
        ],
        return self.modal


class TableWithControls(BaseComponent):
    """Table implementing some controls, such as add column, duplicate column..."""

    def __init__(self, app: 'DashApp',
                 component_id: str,
                 records: _RecordType,
                 columns_names: Dict[str, str],
                 index_id: str,
                 new_col_format: str = 'col_{}',
                 editable: bool = False,
                 include_total: bool = False,
                 total_label: str = 'Total',
                 style_as_list_view=True,
                 is_open: bool = True):
        """Instantiates a new table implementing additional controls such as :
         - Column addition
         - Column duplication

        Parameters
        ----------
        app :
            Instance of Dash application, it is used to register the callbacks
        component_id :
            Base unique id to use for all controls defined in that component.
        records :
            Data to display in the record (list of dictionary) format.
        columns_names :
            Columns definition in the format accepted by Dash.data_table.
            Example :
                [{'id': some_id, 'name': some_column_name, 'type': 'text'}, ...]
        index_id :
            Identifier of the index column. It musts exists in column_names.
        new_col_format :
            String format to use when creating a new column.
        editable :
            All other column than the index are defined as editable.
        include_total :
            Compute the sum of each column except the index.
        total_label :
            Label to use in the index column for the total row.
        style_as_list_view :
            Remove vertical lines from the table.
        is_open :
            Collapsable options are open by default.
        """
        super().__init__(component_id=component_id, app=app)

        self.include_total = include_total
        self.total_label = total_label
        self.index_id = index_id
        self.new_col_format = new_col_format
        self.editable = editable
        self._default_columns_options = {'type': 'numeric', 'editable': editable}
        self.converter = TableFormatConverter(index_id=index_id,
                                              total_label=total_label,
                                              default_columns_options=self._default_columns_options)

        columns_order = list(columns_names.keys())
        columns = self.converter.columns_names_to_datatable_columns(columns_names, columns_order)
        self.columns_order = dcc.Store(id=self.generate_id('columns_order'), data=columns_order)
        records = self.validate_table_records(records, columns)

        style_data_conditional = []
        if include_total:
            total_condition = (Style({'if': {'filter_query': f"{{{self.index_id}}} = {total_label}"}})
                               .font_weight(FontWeight.bold))
            style_data_conditional.append(total_condition)

        style_cell_conditional = [Style({'if': {'column_id': f'{self.index_id}'}}).text_align('left')]

        self.table = DataTable(id=self.generate_id('table'),
                               data=records, columns=columns,
                               style_header=Style().background('whitesmoke').font_weight(FontWeight.bold),
                               style_data_conditional=style_data_conditional,
                               style_cell_conditional=style_cell_conditional,
                               style_as_list_view=style_as_list_view)

        # Defines options for the table.
        self.add_column_button = Button('Add new', id=self.generate_id('add_column_button'), n_clicks=0)
        self.columns_created = dcc.Store(id=self.generate_id('columns_created'), data=3)

        options = self.converter.datatable_columns_to_dropdown_options(columns, index=False)
        self.duplicate_dropdown = Dropdown(id=self.generate_id('duplicate_dropdown'),
                                           options=options, clearable=False, placeholder='Duplicate')

        self.rename_columns = Button('Rename', id=self.generate_id('rename_columns'), n_clicks=0, disabled=True)
        self.import_column = Button('Import', id=self.generate_id('import'), n_clicks=0, disabled=True)

        self.collapse_button = Button(id=self.generate_id('collapse_button'), n_clicks=0)
        self.collapse_options = dbc.Collapse(
            id=self.generate_id('collapse_options'),
            is_open=is_open)

    @classmethod
    def from_file_path(cls, app: 'DashApp',
                       component_id: str,
                       file_path: str,
                       index_col: int = 0,
                       editable: bool = False,
                       include_total: bool = False,
                       total_label: str = 'Total',
                       style_as_list_view: bool = True,
                       is_open: bool = True) -> 'TableWithControls':
        """Instantiate the Table from an initial csv file.

        Parameters
        ----------
        app :
            Instance of Dash application, it is used to register the callbacks
        component_id :
            Base unique id to use for all controls defined in that component.
        file_path :
            Initial file path to load the table from.
        index_col :
            Column index to use as index.
        editable :
            All other column than the index are defined as editable.
        include_total :
            Compute the sum of each column except the index.
        total_label :
            Label to use in the index column for the total row.
        style_as_list_view :
            Remove vertical lines from the table.
        is_open :
            Collapsable options are opened by default.

        Returns
        -------
        TableWithControls

        """
        dataframe = pd.read_csv(file_path).apply(pd.to_numeric, errors='ignore')
        columns_names = {generate_uuid(): column for column in dataframe.columns}

        dataframe.columns = pd.Index(columns_names.keys())
        index_id = dataframe.columns[index_col]

        instance = cls(app=app, component_id=component_id,
                       records=TableFormatConverter.dataframe_to_records(dataframe),
                       columns_names=columns_names,
                       index_id=index_id,
                       editable=editable,
                       include_total=include_total,
                       total_label=total_label,
                       style_as_list_view=style_as_list_view)
        return instance

    def _filter_records(self, records) -> _RecordType:
        """Remove total label from the records."""
        return [record for record in records if record[self.index_id] != self.total_label]

    def _add_new_column_to_table(self, n: int, columns: _ColumnsType, columns_order: List[str]) \
            -> Tuple[str, _ColumnsType, List[str]]:
        """Append a new empty column to the existing table control."""
        new_column_name = self.new_col_format.format(n)
        new_id = generate_uuid()
        columns.append({'id': new_id, 'name': new_column_name, **self._default_columns_options})
        columns_order.append(new_id)
        return new_id, columns, columns_order

    def _duplicate_records_table(self, source_id: str, new_id: str,
                                 records: _RecordType, ) -> _RecordType:
        """Duplicate the source_id in the new_id"""
        records = self._filter_records(records)
        for record in records:
            value = record.get(source_id)
            if value:
                record[new_id] = value
        return records

    def add_new_column(self, n: int, columns: _ColumnsType, columns_order: List[str]) \
            -> Tuple[_ColumnsType, List[str], _DropdownOptionType]:
        """Add a new column to the control.

        Parameters
        ----------
        n :
            Current iteration of column creation.
        columns :
            Values of the columns as given by Dash DataTable
        columns_order :
            List of column identifiers.

        Returns
        -------
        columns, columns_order, options corresponding respectively to the new definitions of the columns,
        their new order and the new options available in the dupicate dropdown control.

        """
        _, columns, columns_order = self._add_new_column_to_table(n, columns, columns_order)
        options = self.converter.datatable_columns_to_dropdown_options(columns, index=False)
        return columns, columns_order, options

    def duplicate_column(self, n: int, columns: _ColumnsType, columns_order: List[str],
                         source_id: str, records: _RecordType) \
            -> Tuple[_ColumnsType, List[str], _DropdownOptionType, _RecordType]:
        """

        Parameters
        ----------
        n :
            Current iteration of column creation.
        columns :
            Values of the columns as given by Dash DataTable
        columns_order :
            List of column identifiers.
        source_id :
            Identifier to copy the column from.
        records :
            Current records in the table.

        Returns
        -------
        columns, columns_order, options, records corresponding respectively to new columns definitions,
        their new order, the new options available in the duplicate dropdown control and the new values for the records.

        """
        new_id, columns, columns_order = self._add_new_column_to_table(n, columns, columns_order)
        options = self.converter.datatable_columns_to_dropdown_options(columns, index=False)
        records = self._duplicate_records_table(source_id, new_id, records)
        return columns, columns_order, options, records

    def validate_table_records(self, records: _RecordType, columns: _ColumnsType) -> _RecordType:
        """Validate records from the table.

        If include_total is ```True``` then the sum of each column is computed.
        Parameters
        ----------
        records :
            Current values in the table.
        columns :
            Current definitions of the columns.

        Returns
        -------
        Validated records.

        """
        """ """
        if self.include_total:
            columns_names, columns_type = dict(), dict()
            for column in columns:
                col_id, col_name, col_type = column['id'], column['name'], column['type']
                columns_names[col_id], columns_type[col_id] = col_name, col_type

            # remove total from records
            records = self._filter_records(records)
            # compute sum
            total = {key: sum([self._get_value_from_record(record, key)
                               for record in records if columns_type[key] == 'numeric'])
                     for key in columns_names.keys()}
            total[self.index_id] = self.total_label
            records.append(total)
        return records

    @staticmethod
    def _get_value_from_record(record, key) -> Union[float, int]:
        value = record.get(key, 0)
        if value is None or value == '':
            return 0
        return value

    def layout(self) -> Div:
        """Defines the layout."""
        self.duplicate_dropdown.style = Style().width('7rem')
        options_control = [self.add_column_button, self.duplicate_dropdown, self.rename_columns, self.import_column]
        stores = [self.columns_order, self.columns_created]
        self.collapse_options.children = dbc.Card(
            dbc.CardBody(options_control, style=Style().row_flex().background('whitesmoke'))
        )
        self.collapse_button.style = Style().height('0.8rem')
        table_options = Div(
            vstack([self.collapse_button, self.collapse_options])
        )

        stack = vstack([table_options, self.table, *stores])
        return Div(stack, style=Style().margin('1rem'))

    def register_callbacks(self, ):
        """Register callbacks."""

        @self.app.callback(Output(self.collapse_options, 'is_open'),
                           Input(self.collapse_button, 'n_clicks'),
                           State(self.collapse_options, 'is_open'))
        def _trigger_collapse(clicks: int, is_open: bool):
            """Collapse the option toolbar."""
            if clicks > 0:
                return not is_open
            raise PreventUpdate

        # @self.app.callback(Output(self.table, 'columns'),
        #                    Output(self.columns_order, 'data'),
        #                    Output(self.duplicate_dropdown, 'options'),
        #                    Output(self.columns_created, 'data'),
        #                    Output(self.table, 'data'),
        #                    Output(self.duplicate_dropdown, 'value'),
        #                    Input(self.add_column_button, 'n_clicks'),
        #                    Input(self.duplicate_dropdown, 'value'),
        #                    Input(self.table, 'data'),
        #                    State(self.table, 'columns'),
        #                    State(self.columns_order, 'data'),
        #                    State(self.columns_created, 'data'))
        # def _update(_,
        #             duplicate_choice_id: str,
        #             records: _RecordType,
        #             current_columns: _ColumnsType,
        #             current_columns_order: List[str],
        #             columns_created: int, ):
        #     """Append a column to the table. Also update the dropdown selection."""
        #     # for convenience, create a return type
        #     output_names = ('columns', 'columns_order', 'options', 'columns_created', 'records', 'duplicate_value')
        #     Result = namedtuple('result', output_names, defaults=(no_update,) * len(output_names))
        #
        #     context_id = ctx.triggered_id
        #     if context_id == self.add_column_button.id:
        #         columns, columns_order, options = \
        #             self.add_new_column(columns_created, current_columns, current_columns_order)
        #         records = self.validate_table_records(records, columns)
        #         return Result(columns=columns, columns_order=columns_order, options=options,
        #                       columns_created=columns_created + 1, records=records)
        #
        #     elif context_id == self.duplicate_dropdown.id:
        #         columns, columns_order, options, records = \
        #             self.duplicate_column(columns_created, current_columns, current_columns_order,
        #                                   duplicate_choice_id, records)
        #         records = self.validate_table_records(records, columns)
        #         return Result(columns=columns, columns_order=columns_order, options=options,
        #                       columns_created=columns_created + 1, records=records, duplicate_value=None)
        #
        #     elif context_id == self.table.id:
        #         records = self.validate_table_records(records, current_columns)
        #         return Result(records=records)
        #
        #     raise PreventUpdate
        with CallbackDispatcher(self.app) as dispatcher:
            @dispatcher.callback(Output(self.table, 'columns'),
                                 Output(self.columns_order, 'data'),
                                 Output(self.duplicate_dropdown, 'options'),
                                 Output(self.columns_created, 'data'),
                                 Input(self.add_column_button, 'n_clicks'),
                                 State(self.table, 'columns'),
                                 State(self.columns_order, 'data'),
                                 State(self.columns_created, 'data'))
            def _add_column(add_column_click: int, current_columns: _ColumnsType, current_columns_order: List[str],
                            columns_created: int):
                if add_column_click:
                    columns, columns_order, options = \
                        self.add_new_column(columns_created, current_columns, current_columns_order)
                    # records = self.validate_table_records(records, columns)
                    return columns, columns_order, options, columns_created + 1
                raise PreventUpdate

            @dispatcher.callback(Output(self.table, 'columns'),
                                 Output(self.columns_order, 'data'),
                                 Output(self.duplicate_dropdown, 'options'),
                                 Output(self.columns_created, 'data'),
                                 Output(self.table, 'data'),
                                 Output(self.duplicate_dropdown, 'value'),
                                 Input(self.duplicate_dropdown, 'value'),
                                 State(self.table, 'data'),
                                 State(self.table, 'columns'),
                                 State(self.columns_order, 'data'),
                                 State(self.columns_created, 'data'))
            def _duplicate_column(duplicate_choice_id: str,
                                  records: _RecordType,
                                  current_columns: _ColumnsType,
                                  current_columns_order: List[str],
                                  columns_created: int, ):
                columns, columns_order, options, records = \
                    self.duplicate_column(columns_created, current_columns, current_columns_order,
                                          duplicate_choice_id, records)
                records = self.validate_table_records(records, columns)
                return columns, columns_order, options, columns_created + 1, records, None

            @dispatcher.callback(Output(self.table, 'data'),
                                 Input(self.table, 'data'),
                                 State(self.table, 'columns'))
            def _update_data(records: _RecordType, current_columns: _ColumnsType):
                records = self.validate_table_records(records, current_columns)
                return records


class ApiResultsStore(BaseComponent):
    def __init__(self, app: 'DashApp', component_id: str,
                 source_control, source_property,
                 preprocess: Callable, postprocess: Callable):
        super().__init__(app=app, component_id=component_id)
        self.source_control = source_control
        self.source_property = source_property
        self.store = dcc.Store(id=self.generate_id('store'))
        self.status_store = dcc.Store(id=self.generate_id('status'), data=False)
        self.preprocess = preprocess
        self.postprocess = postprocess

    def layout(self) -> Div:
        return Div([self.store, self.status_store])

    def register_callbacks(self):
        @self.app.callback(Output(self.store, 'data'),
                           Input(self.source_control, self.source_property))
        def _api_call(data):
            url = 'http://localhost:8000/compute'
            data = self.preprocess(data)
            response = requests.post(url, json=data)
            if response.status_code == 200:
                data = self.postprocess(response.json())
                print('api call successful')
                return data
            raise PreventUpdate

        @self.app.callback(Output(self.status_store, 'data'),
                           Input(self.source_control, self.source_property),
                           Input(self.store, 'data'))
        def _update_status(*_):
            print(ctx.triggered_id)
            if ctx.triggered_id == self.store.id:
                print('Changing status to True')
                return True

            if ctx.triggered_id == self.source_control.id:
                print('Changing status to False')
                return False

            raise PreventUpdate


class LinkedTable(BaseComponent):
    """Table with content linked to another Table."""

    def __init__(self, app: 'DashApp', component_id: str,
                 column_source_control, column_source_property,
                 data_source_control, data_source_property,
                 style_cell_conditional):
        """Instantiates a new LinkedTable control.

        Parameters
        ----------
        app :
            Instance of Dash application, it is used to register the callbacks
        component_id :
            Base unique id to use for all controls defined in that component.
        linked :
            Reference to the table to link
        """
        super().__init__(app=app, component_id=component_id)

        self.column_source_control = column_source_control
        self.column_source_property = column_source_property
        self.data_source_control = data_source_control
        self.data_source_property = data_source_property
        # self.linked = linked
        # self.converter = linked.converter
        # table_component = linked.table
        # style_cell_conditional=table_component.style_cell_conditional
        columns = getattr(column_source_control, column_source_property)
        self.table = DataTable(columns=columns,
                               style_header=Style().background('whitesmoke').font_weight(FontWeight.bold),
                               style_cell_conditional=style_cell_conditional)

    def layout(self) -> Div:
        """Defines the layout."""
        return Div(self.table, style=Style().margin('1rem'))

    def register_callbacks(self):
        """Register callbacks."""

        @self.app.callback(Output(self.table, 'columns'),
                           Input(self.column_source_control, self.column_source_property))
        def _synchronize_columns(columns: _ColumnsType) -> _ColumnsType:
            return columns

        @self.app.callback(Output(self.table, 'data'),
                           Input(self.data_source_control, self.data_source_property))
        def _synchronize_data(records):
            return records

        # @self.app.callback(Output(self.table, 'data'),
        #                    Input(self.linked.table, 'data'))
        # def _synchronize_data(records: _RecordType) -> Optional[_RecordType]:
        #     url = 'http://localhost:8000/compute'
        #     records = self.converter.records_to_dict_of_dict(records)
        #     response = requests.post(url, json=records)
        #     if response.status_code == 200:
        #         return self.converter.dict_of_dict_to_records(response.json())
        #     raise PreventUpdate


class TableFormatConverter:
    """Object converting the columns or data from one format to another."""

    def __init__(self, index_id: str, total_label: str, default_columns_options: dict):
        """Instantiates an object able to convert the values from table properties into other format. Such format
        are required by dropdown controls.

        Parameters
        ----------
        index_id :
            Identifier of the index column. It musts exists in column_names.
        total_label :
            Label to use in the index column for the total row.
        default_columns_options :
            Options to use when creating a new column.
        """
        self.total_label = total_label
        self.index_id = index_id
        self._default_columns_options = default_columns_options

    def columns_names_to_datatable_columns(self,
                                           columns_names: Dict[str, str],
                                           columns_order: List[str],
                                           index: bool = True) -> _ColumnsType:
        """Returns columns values in the format expected by Dash DataTable."""
        if index:
            columns = [{'name': columns_names[self.index_id], 'id': self.index_id, 'type': 'text'}]
        else:
            columns = []

        columns.extend(
            [{'name': columns_names[key], 'id': key, **self._default_columns_options}
             for key in columns_order if key != self.index_id]
        )
        return columns

    def datatable_columns_to_columns_names(self, columns: _ColumnsType, index: bool = True) -> Dict[str, str]:
        """Returns a list of dictionary from Dash DataTable as a dictionary."""
        if index:
            return {column['id']: column['name'] for column in columns}
        else:
            return {column['id']: column['name'] for column in columns if column['id'] != self.index_id}

    def datatable_columns_to_dropdown_options(self, columns: _RecordType, index: bool = True) -> _DropdownOptionType:
        """Format the columns in a list suitable for a dropdown control."""
        if index:
            return [{'label': column['name'], 'value': column['id']} for column in columns]
        else:
            return [{'label': column['name'], 'value': column['id']} for column in columns
                    if column['id'] != self.index_id]

    @staticmethod
    def dataframe_to_records(dataframe: pd.DataFrame) -> _RecordType:
        """Returns the dataframe as a list of records."""
        records = dataframe.to_dict('records')
        return [{key: value for key, value in record.items() if not pd.isna(value)}
                for record in records]

    def records_to_dict_of_dict(self, records: _RecordType) -> Dict[str, Dict]:
        """From records (list of dictionary with column names as key) to nested dictionaries."""
        results = defaultdict(dict)
        for row in records:
            for key, value in row.items():
                index_value = row[self.index_id]
                if key != self.index_id and row[self.index_id] != self.total_label:
                    results[key][index_value] = value

        return results

    def dict_of_dict_to_records(self, dict_of_dict: Dict[Any, Dict]) -> _RecordType:
        """From nested dictionary to record format."""
        columns = dict_of_dict.keys()
        # implement row order feature ?
        rows = {key for inner_dict in dict_of_dict.values() for key in inner_dict.keys()}

        return [{self.index_id: row,  # add index name and iterate on column values
                 **{column: dict_of_dict[column][row] for column in columns if row in dict_of_dict[column]}}
                for row in rows]
