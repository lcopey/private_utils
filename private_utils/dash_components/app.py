# app = DashApp(name=__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
#
# custom_button_1 = CustomButton(1, label='Clicked {}', app=app)
# custom_button_2 = CustomButton(2, label='Clicked {}', app=app)
# app.layout = Div([custom_button_1, custom_button_2])

# if __name__ == '__main__':
#     app.run(debug=True)

from bootstrap_utils import Style
from dash import Dash, html, dcc

app = Dash(__name__)

app.layout = html.Div([
    html.Div(children=[
        html.Label('Dropdown'),
        dcc.Dropdown(['New York City', 'Montréal', 'San Francisco'], 'Montréal'),

        html.Br(),
        html.Label('Multi-Select Dropdown'),
        dcc.Dropdown(['New York City', 'Montréal', 'San Francisco'],
                     ['Montréal', 'San Francisco'],
                     multi=True),

        html.Br(),
        html.Label('Radio Items'),
        dcc.RadioItems(['New York City', 'Montréal', 'San Francisco'], 'Montréal'),
    ], style={'padding': 10, 'flex': 1}),

    html.Div(children=[
        html.Label('Checkboxes'),
        dcc.Checklist(['New York City', 'Montréal', 'San Francisco'],
                      ['Montréal', 'San Francisco']
                      ),

        html.Br(),
        html.Label('Text Input'),
        dcc.Input(value='MTL', type='text'),

        html.Br(),
        html.Label('Slider'),
        dcc.Slider(
            min=0,
            max=9,
            marks={i: f'Label {i}' if i == 1 else str(i) for i in range(1, 6)},
            value=5,
        ),
    ], style=Style().pad(10).apply('flex', 1))
], style=Style().row_flex())

if __name__ == '__main__':
    app.run_server(debug=True)
