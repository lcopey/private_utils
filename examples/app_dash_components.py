from typing import TYPE_CHECKING, Optional

import dash_bootstrap_components as dbc
from dash import Input, Output
from dash.html import Div

from private_utils.dash_components import (BaseComponent, BootstrapColor,
                                           ClassName, ComponentFactory,
                                           DashApp, Shadow)

if TYPE_CHECKING:
    from dash import Dash

CenteredButton = ComponentFactory(dbc.Button,
                                  className=(ClassName()
                                             .center()
                                             .border_color(BootstrapColor.light)
                                             .apply(Shadow.large)))
CenteredLabel = ComponentFactory(dbc.Label, className=ClassName().center(), style={'color': 'blue'})


class CustomButton(BaseComponent):
    def __init__(self, id, label: str, app: Optional[Dash] = None):
        self.label = label
        self.id = id

        self.button_control = CenteredButton('Click me', id=self.generate_id('button'), n_clicks=0)
        self.label_control = CenteredLabel(self.label, id=self.generate_id('label_control'))
        if app is not None:
            self.register_callbacks(app)

    def register_callbacks(self, app: Dash):
        @app.callback(Output(self.label_control, 'children'),
                      Input(self.button_control, 'n_clicks'))
        def on_click(click):
            if click is not None:
                return self.label.format(click)

    def layout(self):
        return Div([self.button_control, self.label_control])


app = DashApp(name=__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

custom_button_1 = CustomButton(1, label='Clicked {}', app=app)
custom_button_2 = CustomButton(2, label='Clicked {}', app=app)
app.layout = Div([custom_button_1, custom_button_2])

if __name__ == '__main__':
    app.run(debug=True)
