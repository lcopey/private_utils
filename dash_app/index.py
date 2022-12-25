import dash_bootstrap_components as dbc
from dash.dcc import Location
from dash.html import Div
from main_page import MainPage
from sidebar import SideBar

from private_utils.dash_components import DashApp

app = DashApp(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
nav_bar = SideBar(component_id='side_bar')
main_page = MainPage(component_id='main_page', file_path='./table.csv', app=app)
app.layout = Div([Location(id="url"), nav_bar, main_page])

if __name__ == '__main__':
    app.run_server(debug=True)
