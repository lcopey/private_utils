from dash import Dash, html
from dash.html import Div, Button
from base import DashApp
from components import CustomButton

app = DashApp(name=__name__)

custom_button_1 = CustomButton(1, label='Clicked {}', app=app)
custom_button_2 = CustomButton(2, label='Clicked {}', app=app)
app.layout = Div([custom_button_1, custom_button_2])

if __name__ == '__main__':
    app.run(debug=True)
