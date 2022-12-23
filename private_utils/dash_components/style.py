from enum import Enum
from typing import Union

__all__ = ['Spacing', 'Sizing', 'Shadow', 'Color', 'TextColor', 'ClassName', 'Display', 'Style']


class Spacing(str, Enum):
    auto = 'auto'
    no = '0'
    extra_small = '1'
    small = '2'
    medium = '3'
    large = '4'
    extra_large = '5'


class Sizing(str, Enum):
    auto = 'auto'
    quarter = '25'
    half = '50'
    three_quarter = '75'
    full = '100'


class Shadow(str, Enum):
    no = 'shadow-none'
    small = 'shadow-sm'
    regular = ''
    large = 'shadow-lg'


class Color(str, Enum):
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
    primary = f'text-{Color.primary}'
    secondary = f'text-{Color.secondary}'
    success = f'text-{Color.success}'
    danger = f'text-{Color.danger}'
    warning = f'text-{Color.warning} bg-dark'
    info = f'text-{Color.info}'
    light = f'text-{Color.light}'
    dark = f'text-{Color.dark}'
    white = f'text-{Color.primary} bg-dark'
    body = f'text-body'
    muted = f'text-muted'
    black_50 = f'text-black-50'
    white_50 = f'text-{Color.white} bg-dark'


class ClassName(str):
    """Wrapper for main bootstrap class names"""

    def apply(self, *args) -> 'ClassName':
        return ClassName(' '.join((self, *args)).strip())

    def center(self) -> 'ClassName':
        return self.apply("start-50", "translate-middle-x", "position-relative")

    def pad(self, pad_size: Union[int, str, Spacing] = Spacing.extra_small) -> 'ClassName':
        """Pad a component."""
        return self.apply(f"p-{pad_size}")

    def margin(self, margin_size: Union[int, str, Spacing] = Spacing.extra_small) -> 'ClassName':
        """Add a margin to the component."""
        return self.apply(f"m-{margin_size}")

    def height(self, height: Union[str, int, Sizing] = Sizing.auto) -> 'ClassName':
        """Define the height of the component. Height should be one of 25, 50, 75, 100, auto"""
        return self.apply(f"h-{height}")

    def border_size(self, border_size: Union[str, int, Spacing]) -> 'ClassName':
        """Define the border-size to the component."""
        allowed_spacing = Spacing.extra_small, Spacing.small, Spacing.medium, Spacing.large, Spacing.extra_large
        assert border_size in allowed_spacing, f"border_size should be one of {allowed_spacing}, got {border_size}."
        return self.apply(f"border-{border_size}")

    def background_color(self, background_color: str) -> 'ClassName':
        """Add a background to the component."""
        return self.apply(f"bg-{background_color}")

    def border_color(self, border_color: Union[str, Color]) -> 'ClassName':
        """Define the border-color to the component."""
        return self.apply(f"border-{border_color}")


def _to_camel_case(key: str):
    split = key.split('-')
    camel_cased = (''.join(
        [item if n == 0 else item.capitalize()
         for n, item in enumerate(split)])
    )
    return camel_cased


class Display(str, Enum):
    flex = 'flex'


class Style(dict):
    def apply(self, key, value):
        key = _to_camel_case(key)
        self[key] = value
        return self

    def color(self, color: str):
        return self.apply('color', color)

    def text_align(self, value: str):
        return self.apply('textAlign', value)

    def pad(self, value):
        return self.apply('padding', value)

    def row_flex(self):
        return self.apply('display', 'flex').apply('flex-direction', 'row')
