from typing import TYPE_CHECKING, Any, Dict, List

import dash_bootstrap_components as dbc
import pandas as pd
from components import Button, Modal, hstack, vstack
from dash import Input, Output, State
from dash.dash_table import DataTable
from dash.dcc import Store
from dash.exceptions import PreventUpdate
from dash.html import Div

from private_utils.dash_components import (BaseComponent, FontWeight, Style,
                                           generate_uuid)

if TYPE_CHECKING:
    from dash import Dash


class Table(BaseComponent):
    def __init__(self, app: 'Dash', component_id: str,
                 data: List[Dict[str, Any]],
                 columns_id: Dict[str, Any],
                 index_name: str,
                 include_total: bool = False, ):
        super().__init__(component_id=component_id, app=app)

        self.data_store = Store(id=self.generate_id('data'), data=data)
        self.columns_store = Store(id=self.generate_id('columns'), data=columns_id)
        self.include_total = include_total
        self.index_name = index_name
        columns = self.to_datatable_columns(columns_id)

        style_data_conditional = []
        if include_total:
            total_condition = (Style({'if': {'filter_query': f"{{{self.index_name}}} = Total"}})
                               .font_weight(FontWeight.bold))
            style_data_conditional.append(total_condition)

        self.table = DataTable(id=self.generate_id('table'),
                               data=data, columns=columns,
                               style_data_conditional=style_data_conditional)

    @classmethod
    def from_file_path(cls, app: 'Dash', component_id: str,
                       file_path: str, index_col: int = 0, include_total: bool = False, ):
        dataframe = pd.read_csv(file_path).apply(pd.to_numeric, errors='ignore')

        columns_id = {generate_uuid(): column for column in dataframe.columns}
        dataframe.columns = columns_id.keys()
        index_name = dataframe.columns[index_col]

        instance = cls(app=app, component_id=component_id,
                       data=cls.to_records(dataframe),
                       columns_id=columns_id,
                       index_name=index_name,
                       include_total=include_total)
        return instance

    @staticmethod
    def to_datatable_columns(columns_id: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [{'name': value, 'id': key} for key, value in columns_id.items()]

    @staticmethod
    def to_records(dataframe: pd.DataFrame) -> List[Dict[str, Any]]:
        """Returns the dataframe as a list of records."""
        return dataframe.to_dict('records')

    def layout(self):
        """Returns layout."""
        return Div([self.table, self.data_store, self.columns_store],
                   style=Style().margin('1rem'))

    def register_callbacks(self, ):
        """Register callbacks."""

        @self.app.callback(Output(self.table, 'columns'),
                           Input(self.columns_store, 'data'), )
        def _update_table_columns(columns_id: Dict[str, Any]):
            return self.to_datatable_columns(columns_id)

        @self.app.callback(Output(self.table, 'data'),
                           Input(self.data_store, 'data'),
                           State(self.columns_store, 'data'))
        def _update_table_data(records: List[Dict[str, Any]], columns_id: Dict[str, Any]):
            if self.include_total:
                # compute sum
                total = {key: sum([record[key] for record in records if isinstance(record[key], (float, int))])
                         for key in columns_id.keys()}
                total[self.index_name] = 'Total'
                records.append(total)
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
        self.table = Table.from_file_path(component_id=self.generate_id('main_table'),
                                          file_path=file_path, include_total=True,
                                          app=app)

        self.add_column_button = Button('Add new', id=self.generate_id('new'), n_clicks=0)
        self.duplicate_button = Button('Duplicate', id=self.generate_id('duplicate'), n_clicks=0)
        self.modal = Modal(component_id='modal')

    def layout(self):
        """Register layout."""
        style = Style().margin(left='18rem', right='2rem').pad(left='2rem', right='1rem')
        # return Div(self.table, style=style)

        return Div([
            dbc.Row(
                hstack(vstack(self.add_column_button, self.duplicate_button),
                       self.table)
            ),
            self.modal],
            style=style)

    def register_callbacks(self):
        """Register callbacks."""

        @self.app.callback(Output(self.table.columns_store, 'data'),
                           Input(self.add_column_button, 'n_clicks'),
                           State(self.table.columns_store, 'data'))
        def _add_column_to_stores(clicks: int, columns_id: Dict[str, Any]):
            if clicks:
                new_column_name = f'column_{clicks}'
                new_id = generate_uuid()
                columns_id[new_id] = new_column_name
                return columns_id

            raise PreventUpdate
