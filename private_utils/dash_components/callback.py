from collections import namedtuple
from typing import Dict, Iterable, List, Mapping, Union

from dash import Input, Output, State, ctx, no_update
from dash.exceptions import PreventUpdate

__all__ = ['CallbackDispatcher']


def _generate_id(arg) -> str:
    prefix = ''
    if isinstance(arg, Output):
        prefix = 'output'
    elif isinstance(arg, Input):
        prefix = 'input'
    elif isinstance(arg, State):
        prefix = 'state'

    base_id = str(arg).replace('.', '_')
    return '_'.join((prefix, base_id))


def _filter(iterable, class_or_tuple):
    if isinstance(iterable, Iterable) and not isinstance(iterable, Mapping):
        return (item for item in iterable if isinstance(item, class_or_tuple))
    elif isinstance(iterable, Mapping):
        return {key: value for key, value in iterable.items() if isinstance(value, class_or_tuple)}


class ProxyCallback:
    def __init__(self, args, fun):
        if not all([isinstance(arg, (Output, Input, State)) for arg in args]):
            raise ValueError(f"Expected one of Output, Input or State, got {args}")

        self.function = fun
        self.input_prop_ids = [_generate_id(arg) for arg in args if isinstance(arg, (Input, State))]
        self.outputs_ids = [_generate_id(arg) for arg in args if isinstance(arg, Output)]
        self.trigger_ids = {str(arg).split('.')[0] for arg in args if isinstance(arg, Input)}


class CallbackDispatcher:
    def __init__(self, app):
        self._callbacks: List[ProxyCallback] = []
        self._prop_ids: Dict[str, Union[Output, Input, State]] = dict()
        self.app = app

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.compile(self.app)

    def callback(self, *args):
        def wrapper(fun):
            item = ProxyCallback(args, fun)
            self._callbacks.append(item)
            for arg in args:
                self._prop_ids[_generate_id(arg)] = arg

            return fun

        return wrapper

    def compile(self, app):
        # in the example, all callback targets partially or all the same outputs
        # one big callback
        # it takes every inputs, states as inputs and all outputs

        outputs = _filter(self._prop_ids, Output)
        inputs = _filter(self._prop_ids, (Input, State))

        Result = namedtuple('result', outputs.keys(), defaults=(no_update,) * len(outputs.keys()))

        @app.callback(*outputs.values(), *inputs.values())
        def dispatch(*args):
            # argument are mapped as dict
            arg_as_dict = {key: arg for arg, key in zip(args, inputs.keys())}
            context = ctx.triggered_id
            if context is not None:
                for callback in self._callbacks:
                    # Trigger the callback according to context
                    if context in callback.trigger_ids:
                        input_args = [arg_as_dict[input_id] for input_id in callback.input_prop_ids]
                        outputs_args = callback.function(*input_args)
                        if len(callback.outputs_ids) == 1:  # output is not a tuple
                            outputs_args = (outputs_args,)
                        outputs_args = dict(zip(callback.outputs_ids, outputs_args))

                        result = Result(**outputs_args)
                        return result
            raise PreventUpdate
