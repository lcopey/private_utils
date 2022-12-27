from functools import update_wrapper
from typing import Iterable, Optional
from uuid import uuid4

from dash import Dash
from structlog import getLogger

logger = getLogger(__name__)

__all__ = ['LayoutComponent', 'BaseComponent', 'DashApp', 'ComponentFactory', 'generate_uuid']


def generate_uuid() -> str:
    """Generate unique id."""
    return str(uuid4())


class DashApp(Dash):
    """Subclass of Dash application. It mainly allows to use BaseComponent as if it was a component from Dash."""

    @Dash.layout.setter
    def layout(self, layout):
        # subclass the property setter of Dash.
        layout = _walk_layout(layout)
        Dash.layout.fset(self, layout)


class MetaBaseComponent(type):
    """Metaclass for the BaseComponent. It defines the instance and call register callbacks after the __init__."""

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        instance.register_callbacks()
        return instance


class LayoutComponent:
    """Base component to use when one want to apply oriented-object framework to Dash. It must implement the layout
    method. This method is called when parsing the global layout of the application."""

    def __init__(self, component_id: Optional[str] = None):
        self.component_id = component_id or generate_uuid()

    def layout(self):
        raise NotImplementedError

    def generate_id(self, name: str):
        component_id = self.component_id
        if not isinstance(component_id, str):
            component_id = str(component_id)
        return '_'.join((component_id, name))


class BaseComponent(LayoutComponent, metaclass=MetaBaseComponent):
    """Base component to use when one want to apply oriented-object framework to Dash. It must implement the layout
    method and register_callbacks method."""

    def __init__(self, app: DashApp, component_id: Optional[str] = None):
        super().__init__(component_id=component_id)
        self.app = app

    def register_callbacks(self):
        """Callbacks are registered here using the Dash instance stored in self.app.

        Example :
        @self.app.callback(Output(...), Input(...)
        def some_callback():
            ....
        """
        raise NotImplementedError

    def layout(self):
        raise NotImplementedError


def _walk_component(layout):
    children = getattr(layout, 'children', None)
    if children and (isinstance(children, (list, tuple))):
        layout.children = [_walk_layout(child) for child in children]

    elif children:
        layout.children = _walk_layout(children)

    return layout


def _walk_custom_component(item: LayoutComponent):
    return _walk_layout(item.layout())


def _walk_iterable_layout(layout: Iterable):
    return [_walk_layout(child) for child in layout]


def _walk_layout(layout):
    func = _walk_component
    if isinstance(layout, LayoutComponent):
        func = _walk_custom_component

    elif isinstance(layout, (list, tuple)):
        func = _walk_iterable_layout

    return func(layout)


class ComponentFactory:
    """Utility class that wraps an existing Component and apply default keywords.

    Examples :
    ButtonWithMargin = ComponentFactory(html.Button, style={'margin': '1rem'})

    from dash_components import Style

    CenteredButton = ComponentFactory(html.Button, style=Style().center()).
    button = CenteredButton(id=...)"""

    def __init__(self, base_class, **base_class_kwwargs):
        self.base_class = base_class
        self.keywords = base_class_kwwargs
        update_wrapper(self, base_class)

    def __call__(self, *args, **kwargs):
        return self.base_class(*args, **kwargs, **self.keywords)
