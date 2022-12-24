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
    def __init__(self, id: Optional[str] = None):
        super().__init__(id=id)
        self.close = dbc.Button("CLOSE BUTTON", id=self.generate_id("close"), className="ml-auto")
        self.modal = dbc.Modal(
            [
                dbc.ModalHeader("HEADER"),
                dbc.ModalBody("BODY OF MODAL"),
                dbc.ModalFooter(self.close),
            ],
            id=self.generate_id('modal')
        )

    def layout(self):
        return self.modal
