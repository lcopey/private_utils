from enum import Enum
from typing import Union

__all__ = ['Spacing', 'Sizing', 'Shadow', 'Color', 'TextColor', 'ClassName', 'Style']


class Spacing(str, Enum):
    """Spacing enum for bootstrap class names."""
    auto = 'auto'
    no = '0'
    extra_small = '1'
    small = '2'
    medium = '3'
    large = '4'
    extra_large = '5'


class Sizing(str, Enum):
    """Sizing enum for bootstrap class names."""
    auto = 'auto'
    quarter = '25'
    half = '50'
    three_quarter = '75'
    full = '100'


class Shadow(str, Enum):
    """Shadow class names"""
    no = 'shadow-none'
    small = 'shadow-sm'
    regular = ''
    large = 'shadow-lg'


class Color(str, Enum):
    """Color class names for bootstrapped controls."""
    primary = 'primary'
    secondary = 'secondary'
    success = 'success'
    danger = 'danger'
    warning = 'warning'
    info = 'info'
    light = 'light'
    dark = 'dark'
    white = 'white'


class TextColor(str, Enum):
    """Color class names for text controls."""
    primary = f'text-{Color.primary}'
    secondary = f'text-{Color.secondary}'
    success = f'text-{Color.success}'
    danger = f'text-{Color.danger}'
    warning = f'text-{Color.warning} bg-dark'
    info = f'text-{Color.info}'
    light = f'text-{Color.light}'
    dark = f'text-{Color.dark}'
    white = f'text-{Color.primary} bg-dark'
    body = 'text-body'
    muted = 'text-muted'
    black_50 = 'text-black-50'
    white_50 = f'text-{Color.white} bg-dark'


class ClassName(str):
    """Wrapper for main bootstrap class names"""

    def apply(self, *args) -> 'ClassName':
        """Apply args to the class name under construction."""
        return ClassName(' '.join((self, *args)).strip())

    def center(self) -> 'ClassName':
        """Center most of the controls."""
        return self.apply("start-50", "translate-middle-x", "position-relative")

    def pad(self, pad_size: Union[int, str, Spacing] = Spacing.extra_small) -> 'ClassName':
        """Pad a control."""
        return self.apply(f"p-{pad_size}")

    def margin(self, margin_size: Union[int, str, Spacing] = Spacing.extra_small) -> 'ClassName':
        """Add a margin to the control."""
        return self.apply(f"m-{margin_size}")

    def height(self, height: Union[str, int, Sizing] = Sizing.auto) -> 'ClassName':
        """Define the height of the control. Height should be one of 25, 50, 75, 100, auto"""
        return self.apply(f"h-{height}")

    def border_size(self, border_size: Union[str, int, Spacing] = Spacing.extra_small) -> 'ClassName':
        """Define the border-size to the control."""
        allowed_spacing = Spacing.extra_small, Spacing.small, Spacing.medium, Spacing.large, Spacing.extra_large
        assert border_size in allowed_spacing, f"border_size should be one of {allowed_spacing}, got {border_size}."
        return self.apply(f"border-{border_size}")

    def background_color(self, background_color: str) -> 'ClassName':
        """Add a background to the control."""
        return self.apply(f"bg-{background_color}")

    def border_color(self, border_color: Union[str, Color]) -> 'ClassName':
        """Define the border-color to the control."""
        return self.apply(f"border-{border_color}")


# class Display(str, Enum):
#     flex = 'flex'

def _to_camel_case(key: str):
    """Transform css keywords  with dash between words into camel cased words."""
    split = key.split('-')
    camel_cased = (''.join(
        [item if n == 0 else item.capitalize()
         for n, item in enumerate(split)])
    )
    return camel_cased


class Style(dict):
    def apply(self, key, value):
        """Add the key value to the dictionary."""
        key = _to_camel_case(key)
        self[key] = value
        return self

    def color(self, color: str):
        """Apply color key."""
        return self.apply('color', color)

    def background(self, background_color: str):
        """Apply background color."""
        return self.apply('background-color', background_color)

    def text_align(self, value: str):
        """Apply text align."""
        return self.apply('textAlign', value)

    def pad(self, pad=None, top=None, left=None, right=None, bottom=None):
        """Apply padding. `pad` keyword takes priority over the other keywords."""
        if pad:
            return self.apply('padding', pad)
        else:
            value = self
            if top:
                value = value.apply('padding-top', top)
            if left:
                value = value.apply('padding-left', left)
            if right:
                value = value.apply('padding-right', right)
            if bottom:
                value = value.appy('padding-bottom', bottom)
            return value

    def margin(self, margin=None, top=None, left=None, right=None, bottom=None):
        """Apply margin. `margin` keywords takes priority over the other keywords."""
        if margin:
            return self.apply('padding', margin)
        else:
            value = self
            if top:
                value = value.apply('margin-top', top)
            if left:
                value = value.apply('margin-left', left)
            if right:
                value = value.apply('margin-right', right)
            if bottom:
                value = value.appy('margin-bottom', bottom)
            return value

    def row_flex(self):
        """Apply flex display with the row direction."""
        return self.apply('display', 'flex').apply('flex-direction', 'row')

    def position(self, value):
        """Value is one of `absolue`, `fixed`, `relative`, `sticky`"""
        return self.apply('position', value)

    def positioned(self, top: str = None, left: str = None, right: str = None, bottom: str = None):
        """Apply one or multiple of the following keywords `top`, `left`, `right` and `bottom`"""
        value = self
        if top:
            value = value.apply('top', top)
        if left:
            value = value.apply('left', left)
        if right:
            value = value.apply('top', right)
        if bottom:
            value = value.apply('top', bottom)
        return value

    def top(self, value):
        """Apply top keyword"""
        return self.apply('top', value)

    def left(self, value):
        """Apply left keyword."""
        return self.apply('left', value)

    def right(self, value):
        """Apply right keyword."""
        return self.apply('right', value)

    def bottom(self, value):
        """Apply bottom keyword."""
        return self.apply('bottom', value)

    def width(self, value):
        """Apply width keyword."""
        return self.apply('width', value)

    def height(self, value):
        """Apply height keyword."""
        return self.apply('height', value)

    def box_shadow(self, width=None, top=None, left=None, right=None, bottom=None, color=None):
        """Apply shadow"""
        if width is not None:
            value = width
        else:
            value = ' '.join((top, left, right, bottom))

        if color is not None:
            value = f'{value} {color}'

        return self.apply('box-shadow', value)
