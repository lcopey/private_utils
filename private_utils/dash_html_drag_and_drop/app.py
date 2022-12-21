from dash import Dash, html
from components import CustomButton

app = Dash(__name__)

custom_button_1 = CustomButton(1, label='Clicked {}', app=app)
custom_button_2 = CustomButton(2, label='Clicked {}', app=app)
app.layout = html.Div([custom_button_1.layout(),
                       custom_button_2.layout()])

if __name__ == '__main__':
    app.run_server(debug=True)
