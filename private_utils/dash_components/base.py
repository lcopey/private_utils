from functools import update_wrapper
from typing import Iterable, Optional
from uuid import uuid4

from dash import Dash


class BaseComponent:
    def __init__(self, id: Optional[str] = None, app: Optional[Dash] = None):
        if not id:
            id = uuid4()
        self.id = id
        if app is not None:
            self.register_callbacks(app)

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


class DashApp(Dash):
    @Dash.layout.setter
    def layout(self, layout):
        # subclass the property setter of Dash.
        layout = _parse_layout(layout)
        Dash.layout.fset(self, layout)


class ComponentFactory:
    def __init__(self, base_class, **base_class_kwwargs):
        self.base_class = base_class
        self.keywords = base_class_kwwargs
        update_wrapper(self, base_class)

    def __call__(self, *args, **kwargs):
        return self.base_class(*args, **kwargs, **self.keywords)
