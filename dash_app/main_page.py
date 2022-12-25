from typing import TYPE_CHECKING, Any, Dict, List

import dash_bootstrap_components as dbc
import pandas as pd
from components import Button, Modal, hstack, vstack
from dash import Input, Output, State
from dash.dash_table import DataTable
from dash.dcc import Store
from dash.exceptions import PreventUpdate
from dash.html import Div

from private_utils.dash_components import (BaseComponent, LayoutComponent,
                                           Style, generate_uiid)

if TYPE_CHECKING:
    from dash import Dash


class Table(BaseComponent):
    def __init__(self, app: 'Dash', component_id: str,
                 data: List[Dict[str, Any]],
                 columns_id=Dict[str, Any],
                 include_total: bool = False, ):
        super().__init__(component_id=component_id, app=app)

        self.data_store = Store(id=self.generate_id('data'), data=data)
        self.columns_store = Store(id=self.generate_id('columns'), data=columns_id)
        self.include_total = include_total
        columns = self.to_datatable_columns(columns_id)

        # style_data_conditional = []
        # if include_total:
        #     total_condition = (Style({'if': {'filter_query': f"{{{self.data.index_id}}} = Total"}})
        #                        .font_weight(FontWeight.bold))
        #     style_data_conditional.append(total_condition)

        self.table = DataTable(id=self.generate_id('table'),
                               data=data,
                               columns=columns)
        self.add_column_button = Button('Add new', id=self.generate_id('new'), n_clicks=0)
        self.duplicate_button = Button('Duplicate', id=self.generate_id('duplicate'), n_clicks=0)
        self.modal = Modal(component_id='modal')

    @classmethod
    def from_file_path(cls, app: 'Dash', component_id: str,
                       file_path: str, include_total: bool = False, ):
        dataframe = pd.read_csv(file_path)
        columns_id = {generate_uiid(): column for column in dataframe.columns}
        dataframe.columns = columns_id.keys()
        instance = cls(app=app, component_id=component_id,
                       data=cls.to_records(dataframe), columns_id=columns_id,
                       include_total=include_total)
        return instance

    @staticmethod
    def to_datatable_columns(columns_id: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [{'name': value, 'id': key} for key, value in columns_id.items()]

    @staticmethod
    def to_records(dataframe: pd.DataFrame):
        return dataframe.to_dict('records')

    def layout(self):
        """Returns layout."""
        return Div([
            dbc.Row(
                hstack(vstack(self.add_column_button, self.duplicate_button),
                       self.table)
            ),
            self.modal, self.data_store, self.columns_store],
            style=Style().margin('1rem'))

    def register_callbacks(self, ):
        """Register callbacks."""

        @self.app.callback(Output(self.columns_store, 'data'),
                           Input(self.add_column_button, 'n_clicks'),
                           State(self.columns_store, 'data'))
        def _add_column_to_stores(clicks: int, columns_id: Dict[str, Any]):
            if clicks:
                new_column_name = f'column_{clicks}'
                new_id = generate_uiid()
                columns_id[new_id] = new_column_name
                return columns_id

            raise PreventUpdate

        @self.app.callback(Output(self.table, 'columns'),
                           Input(self.columns_store, 'data'), )
        def _update_table_columns(columns_id: Dict[str, Any]):
            return self.to_datatable_columns(columns_id)

        # @self.app.callback(Output(self.modal.modal, 'is_open'),
        #                    Input(self.duplicate_button, 'n_clicks'),
        #                    Input(self.modal.close, 'n_clicks'),
        #                    State(self.modal.modal, 'is_open'))
        # def display_modal(open_click: int, close_click: int, is_open: bool):
        #     if open_click or close_click:
        #         return not is_open
        pass


class MainPage(LayoutComponent):
    """Main component."""

    def __init__(self, app, file_path: str, component_id: str = None):
        super().__init__(component_id=component_id)
        self.table = Table.from_file_path(component_id=self.generate_id('main_table'),
                                          file_path=file_path, include_total=True,
                                          app=app)

    def layout(self):
        """Register layout."""
        style = Style().margin(left='18rem', right='2rem').pad(left='2rem', right='1rem')
        return Div(self.table, style=style)

    def register_callbacks(self):
        """Register callbacks."""
        pass
