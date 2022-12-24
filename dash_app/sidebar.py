from typing import TYPE_CHECKING

import dash_bootstrap_components as dbc
from dash.html import H2, Div, Hr, P

from private_utils.dash_components import BaseComponent, Style

if TYPE_CHECKING:
    from dash import Dash


class SideBar(BaseComponent):
    def layout(self):
        sidebar_style = (Style()
                         .position('fixed')
                         .positioned(top=0, left=0, bottom=0)
                         .width('16rem')
                         .pad(left="2rem", right="1rem")
                         .background("#f8f9fa"))
        sidebar = Div(
            [
                H2("Sidebar", className="display-4"),
                Hr(),
                P(
                    "A simple sidebar layout with navigation links", className="lead"
                ),
                dbc.Nav(
                    [
                        dbc.NavLink("Home", href="/", active="exact"),
                        dbc.NavLink("Page 1", href="/page-1", active="exact"),
                        dbc.NavLink("Page 2", href="/page-2", active="exact"),
                    ],
                    vertical=True,
                    pills=True,
                ),
            ],
            style=sidebar_style,
        )
        return sidebar

    def register_callbacks(self, app: 'Dash'):
        pass
