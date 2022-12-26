from typing import Optional, Sequence

import dash_bootstrap_components as dbc
from dash.dcc import Dropdown

from private_utils.dash_components import (ClassName, ComponentFactory,
                                           LayoutComponent, Spacing)

# Button = ComponentFactory(dbc.Button, style=Style().margin('0.2rem'))
# Dropdown = ComponentFactory(Dropdown, style=Style().margin('0.2rem'))
Button = ComponentFactory(dbc.Button, className=ClassName().margin(Spacing.extra_small))
Dropdown = ComponentFactory(Dropdown, className=ClassName().margin(Spacing.extra_small))


def hstack(iterable: Sequence, widths: Optional[Sequence] = None) -> Sequence:
    if widths is None:
        return [dbc.Col(arg) for arg in iterable]

    assert len(iterable) == len(widths), f"iterable and widths should have the same length, " \
                                         f"got {len(iterable)} and {len(widths)}"
    return [dbc.Col(arg, width=width) for arg, width in zip(iterable, widths)]


def vstack(iterable) -> Sequence:
    return [dbc.Row(arg) for arg in iterable]


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
