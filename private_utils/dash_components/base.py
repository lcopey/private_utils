from dash import Dash
from typing import Iterable, Optional


class BaseComponent:
    def register_callbacks(self, app: Dash):
        raise NotImplementedError

    def layout(self):
        raise NotImplementedError

    def generate_id(self, name: str):
        id = self.id
        if not isinstance(id, str):
            id = str(id)
        return '_'.join((id, name))


def _parse_component(item):
    children = getattr(item, 'children', None)
    if children and (isinstance(children, Iterable) and not isinstance(children, str)):
        item.children = [_parse_layout(child) for child in children]
        return item

    return item


def _parse_custom_component(item: BaseComponent):
    return _parse_layout(item.layout())


def _parse_layout_iterable(items: Iterable):
    return [_parse_layout(child) for child in items]


def _parse_layout(layout):
    if isinstance(layout, BaseComponent):
        func = _parse_custom_component
    elif isinstance(layout, (list, tuple)):
        func = _parse_layout_iterable
    else:
        func = _parse_component

    return func(layout)


# class DashApp:
#     def __init__(self, app: Optional[Dash] = None, **kwargs):
#         if app is None:
#             self.app = Dash(**kwargs)
#         else:
#             self.app = app
#
#     @property
#     def layout(self):
#         return self.app.layout
#
#     @layout.setter
#     def layout(self, value):
#         value = _parse_layout(value)
#         self.app.layout = value
#
#     def run(self, debug: bool = False):
#         self.app.run(debug=debug)
#
#     def callback(self, *args, **kwargs):
#         return self.app.callback(*args, **kwargs)

class DashApp(Dash):
    @Dash.layout.setter
    def layout(self, layout):
        #
        layout = _parse_layout(layout)
        Dash.layout.fset(self, layout)
