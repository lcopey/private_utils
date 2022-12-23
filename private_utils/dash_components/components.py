from typing import Optional

import dash_bootstrap_components as dbc
from bootstrap_utils import ClassName, Color, Shadow
from dash import Dash, Input, Output
from dash.html import Div

from base import BaseComponent, ComponentFactory

CenteredButton = ComponentFactory(dbc.Button,
                                  className=(ClassName()
                                             .center()
                                             .border_color(Color.light)
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
