import dash_bootstrap_components as dbc
from dash.dcc import Location
from main_page import MainPage
from sidebar import SideBar

from private_utils.dash_components import DashApp

dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.2/dbc.min.css")
app = DashApp(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css])
nav_bar = SideBar(component_id='side_bar')
main_page = MainPage(component_id='main_page', file_path='./dummy.csv', app=app)

app.layout = dbc.Container([Location(id="url"), nav_bar, main_page], fluid=True, className='dbc')

if __name__ == '__main__':
    app.run_server(debug=True)
