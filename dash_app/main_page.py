from typing import TYPE_CHECKING
from uuid import uuid4

import dash_bootstrap_components as dbc
import pandas as pd
from components import Button, Modal, hstack, vstack
from dash import Input, Output, State
from dash.dash_table import DataTable
from dash.exceptions import PreventUpdate
from dash.html import Div

from private_utils.dash_components import (BaseComponent, FontWeight,
                                           LayoutComponent, Style)

if TYPE_CHECKING:
    from dash import Dash


class DataTableModel:
    def __init__(self, dataframe: pd.DataFrame, columns_id: dict,
                 index_col: int = 0,
                 include_total: bool = False):
        self._dataframe: pd.DataFrame = dataframe
        self._index_col: str = dataframe.columns[index_col]
        self._columns_id: dict[str, str] = columns_id
        self.include_total: bool = include_total

    @classmethod
    def from_dataframe(cls, dataframe: pd.DataFrame, index_col: int = 0, include_total: bool = False):
        columns_id = {str(uuid4()): column for column in dataframe.columns}
        dataframe.columns = columns_id.keys()
        return cls(dataframe, columns_id, index_col=index_col, include_total=include_total)

    @classmethod
    def from_file(cls, file_path: str, index_col: int = 0, include_total: bool = False):
        return cls.from_dataframe(pd.read_csv(file_path), index_col=index_col, include_total=include_total)

    def update_from_records(self, records):
        self._dataframe = pd.DataFrame(records)

    @property
    def records(self):
        records = self._dataframe.to_dict('records')
        if self.include_total:
            total = self._dataframe.sum(numeric_only=True).to_dict()
            total[self._index_col] = 'Total'
            records.append(total)

        return records

    @property
    def index_id(self):
        return self._index_col

    @property
    def columns(self):
        # TODO to dataclass ?
        return [{'name': value, 'id': key} for key, value in self._columns_id.items()]

    def append_column(self, new_column_name: str):
        new_id = str(uuid4())
        self._columns_id[new_id] = new_column_name
        self._dataframe[new_id] = None


class Table(BaseComponent):
    def __init__(self, app: 'Dash', id: str,
                 source_table: str, include_total: bool = False, ):
        super().__init__(id=id, app=app)

        self.data = DataTableModel.from_file(source_table, include_total=include_total)

        style_data_conditional = []
        if include_total:
            total_condition = (Style({'if': {'filter_query': f"{{{self.data.index_id}}} = Total"}})
                               .font_weight(FontWeight.bold))
            style_data_conditional.append(total_condition)

        self.table = DataTable(id=self.generate_id('table'),
                               data=self.data.records,
                               columns=self.data.columns,
                               style_data_conditional=style_data_conditional)
        self.add_column_button = Button('Add new', id=self.generate_id('new'), n_clicks=0)
        self.duplicate_button = Button('Duplicate', id=self.generate_id('duplicate'), n_clicks=0)
        self.modal = Modal(id='modal')
        # self.add_column_dropdown = dbc.DropdownMenu(id=self.generate_id('add_column_dropdown'))

    def layout(self):

        return Div([
            dbc.Row(
                hstack(vstack(self.add_column_button, self.duplicate_button),
                       self.table)
            ),
            self.modal],
            style=Style().margin('1rem'))

    def register_callbacks(self, ):
        @self.app.callback(Output(self.table, 'data'),
                           Output(self.table, 'columns'),
                           Input(self.add_column_button, 'n_clicks'))
        def _add_column(clicks: int):
            if clicks:
                new_column_name = f'column_{clicks}'
                self.data.append_column(new_column_name)
                return self.data.records, self.data.columns
            raise PreventUpdate

        @self.app.callback(Output(self.modal.modal, 'is_open'),
                           Input(self.duplicate_button, 'n_clicks'),
                           Input(self.modal.close, 'n_clicks'),
                           State(self.modal.modal, 'is_open'))
        def display_modal(open_click: int, close_click: int, is_open: bool):
            if open_click or close_click:
                return not is_open


class MainPage(LayoutComponent):
    def __init__(self, app, source_table: str, id: str = None):
        super().__init__(id=id)
        self.table = Table(id=self.generate_id('main_table'), source_table=source_table, include_total=True,
                           app=app)

    def layout(self):
        style = Style().margin(left='18rem', right='2rem').pad(left='2rem', right='1rem')
        return Div(self.table, style=style)

    def register_callbacks(self):
        pass
