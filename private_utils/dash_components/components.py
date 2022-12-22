from typing import Optional
from base import BaseComponent
from dash import Input, Output, Dash
from dash.html import Div, Button


class CustomButton(BaseComponent):
    def __init__(self, id, label: str, app: Optional[Dash] = None):
        self.label = label
        self.id = id

        self.button_control = Button('Click me', id=self.generate_id('button'), n_clicks=0)
        self.label_control = Div(self.label, id=self.generate_id('label_control'))
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
