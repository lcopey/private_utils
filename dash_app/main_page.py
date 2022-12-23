from typing import TYPE_CHECKING

from dash.dash_table import DataTable
from dash.html import Div

from private_utils.dash_components import BaseComponent, Style

if TYPE_CHECKING:
    from dash import Dash


class Table(BaseComponent):
    def __init__(self, id: str, app: 'Dash' = None):
        super().__init__(id, app)
        self.table = DataTable()

    def layout(self):
        return self.table

    def register_callbacks(self, app: 'Dash'):
        pass


class MainPage(BaseComponent):
    def __init__(self, id: str, app: 'Dash' = None):
        super().__init__(id, app)
        self.table = Table(id=self.generate_id('main_table'))

    def layout(self):
        style = Style().margin(left='18rem', right='2rem').pad(left='2rem', right='1rem')
        return Div([self.table], style=style)
