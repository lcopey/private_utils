from typing import Optional

import dash_bootstrap_components as dbc

from private_utils.dash_components import (ComponentFactory, LayoutComponent,
                                           Style)

Button = ComponentFactory(dbc.Button, style=Style().margin('0.2rem'))


def vstack(*args):
    return [dbc.Row(arg) for arg in args]


def hstack(*args):
    return [dbc.Col(arg) for arg in args]


class Modal(LayoutComponent):
    def __init__(self, component_id: Optional[str] = None):
        super().__init__(component_id=component_id)
        self.close = dbc.Button("CLOSE BUTTON", id=self.generate_id("close_btn"), className="ml-auto")
        self.modal = dbc.Modal(
            [
                dbc.ModalHeader("HEADER"),
                dbc.ModalBody("BODY OF MODAL"),
                dbc.ModalFooter(self.close),
            ],
            id=self.generate_id('window')
        )

    def layout(self):
        return self.modal
