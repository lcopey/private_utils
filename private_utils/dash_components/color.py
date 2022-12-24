import re
from colorsys import hls_to_rgb, rgb_to_hls
from difflib import get_close_matches
from functools import lru_cache
from operator import itemgetter
from typing import Callable, NamedTuple, Optional, Sequence, Tuple, Union

__all__ = ['COLOR_NAME_TO_RGB', 'HSL', 'Color']

COLOR_NAME_TO_RGB: dict[str, Union[Tuple[int, int, int], Tuple[int, int, int, float]]] = {
    # Let's start with a specific pseudo-color::
    "transparent": (0, 0, 0, 0),
    # Then, the 16 common ANSI colors:
    "ansi_black": (0, 0, 0),
    "ansi_red": (128, 0, 0),
    "ansi_green": (0, 128, 0),
    "ansi_yellow": (128, 128, 0),
    "ansi_blue": (0, 0, 128),
    "ansi_magenta": (128, 0, 128),
    "ansi_cyan": (0, 128, 128),
    "ansi_white": (192, 192, 192),
    "ansi_bright_black": (128, 128, 128),
    "ansi_bright_red": (255, 0, 0),
    "ansi_bright_green": (0, 255, 0),
    "ansi_bright_yellow": (255, 255, 0),
    "ansi_bright_blue": (0, 0, 255),
    "ansi_bright_magenta": (255, 0, 255),
    "ansi_bright_cyan": (0, 255, 255),
    "ansi_bright_white": (255, 255, 255),
    # And then, Web color keywords: (up to CSS Color Module Level 4)
    "black": (0, 0, 0),
    "silver": (192, 192, 192),
    "gray": (128, 128, 128),
    "white": (255, 255, 255),
    "maroon": (128, 0, 0),
    "red": (255, 0, 0),
    "purple": (128, 0, 128),
    "fuchsia": (255, 0, 255),
    "green": (0, 128, 0),
    "lime": (0, 255, 0),
    "olive": (128, 128, 0),
    "yellow": (255, 255, 0),
    "navy": (0, 0, 128),
    "blue": (0, 0, 255),
    "teal": (0, 128, 128),
    "aqua": (0, 255, 255),
    "orange": (255, 165, 0),
    "aliceblue": (240, 248, 255),
    "antiquewhite": (250, 235, 215),
    "aquamarine": (127, 255, 212),
    "azure": (240, 255, 255),
    "beige": (245, 245, 220),
    "bisque": (255, 228, 196),
    "blanchedalmond": (255, 235, 205),
    "blueviolet": (138, 43, 226),
    "brown": (165, 42, 42),
    "burlywood": (222, 184, 135),
    "cadetblue": (95, 158, 160),
    "chartreuse": (127, 255, 0),
    "chocolate": (210, 105, 30),
    "coral": (255, 127, 80),
    "cornflowerblue": (100, 149, 237),
    "cornsilk": (255, 248, 220),
    "crimson": (220, 20, 60),
    "cyan": (0, 255, 255),
    "darkblue": (0, 0, 139),
    "darkcyan": (0, 139, 139),
    "darkgoldenrod": (184, 134, 11),
    "darkgray": (169, 169, 169),
    "darkgreen": (0, 100, 0),
    "darkgrey": (169, 169, 169),
    "darkkhaki": (189, 183, 107),
    "darkmagenta": (139, 0, 139),
    "darkolivegreen": (85, 107, 47),
    "darkorange": (255, 140, 0),
    "darkorchid": (153, 50, 204),
    "darkred": (139, 0, 0),
    "darksalmon": (233, 150, 122),
    "darkseagreen": (143, 188, 143),
    "darkslateblue": (72, 61, 139),
    "darkslategray": (47, 79, 79),
    "darkslategrey": (47, 79, 79),
    "darkturquoise": (0, 206, 209),
    "darkviolet": (148, 0, 211),
    "deeppink": (255, 20, 147),
    "deepskyblue": (0, 191, 255),
    "dimgray": (105, 105, 105),
    "dimgrey": (105, 105, 105),
    "dodgerblue": (30, 144, 255),
    "firebrick": (178, 34, 34),
    "floralwhite": (255, 250, 240),
    "forestgreen": (34, 139, 34),
    "gainsboro": (220, 220, 220),
    "ghostwhite": (248, 248, 255),
    "gold": (255, 215, 0),
    "goldenrod": (218, 165, 32),
    "greenyellow": (173, 255, 47),
    "grey": (128, 128, 128),
    "honeydew": (240, 255, 240),
    "hotpink": (255, 105, 180),
    "indianred": (205, 92, 92),
    "indigo": (75, 0, 130),
    "ivory": (255, 255, 240),
    "khaki": (240, 230, 140),
    "lavender": (230, 230, 250),
    "lavenderblush": (255, 240, 245),
    "lawngreen": (124, 252, 0),
    "lemonchiffon": (255, 250, 205),
    "lightblue": (173, 216, 230),
    "lightcoral": (240, 128, 128),
    "lightcyan": (224, 255, 255),
    "lightgoldenrodyellow": (250, 250, 210),
    "lightgray": (211, 211, 211),
    "lightgreen": (144, 238, 144),
    "lightgrey": (211, 211, 211),
    "lightpink": (255, 182, 193),
    "lightsalmon": (255, 160, 122),
    "lightseagreen": (32, 178, 170),
    "lightskyblue": (135, 206, 250),
    "lightslategray": (119, 136, 153),
    "lightslategrey": (119, 136, 153),
    "lightsteelblue": (176, 196, 222),
    "lightyellow": (255, 255, 224),
    "limegreen": (50, 205, 50),
    "linen": (250, 240, 230),
    "magenta": (255, 0, 255),
    "mediumaquamarine": (102, 205, 170),
    "mediumblue": (0, 0, 205),
    "mediumorchid": (186, 85, 211),
    "mediumpurple": (147, 112, 219),
    "mediumseagreen": (60, 179, 113),
    "mediumslateblue": (123, 104, 238),
    "mediumspringgreen": (0, 250, 154),
    "mediumturquoise": (72, 209, 204),
    "mediumvioletred": (199, 21, 133),
    "midnightblue": (25, 25, 112),
    "mintcream": (245, 255, 250),
    "mistyrose": (255, 228, 225),
    "moccasin": (255, 228, 181),
    "navajowhite": (255, 222, 173),
    "oldlace": (253, 245, 230),
    "olivedrab": (107, 142, 35),
    "orangered": (255, 69, 0),
    "orchid": (218, 112, 214),
    "palegoldenrod": (238, 232, 170),
    "palegreen": (152, 251, 152),
    "paleturquoise": (175, 238, 238),
    "palevioletred": (219, 112, 147),
    "papayawhip": (255, 239, 213),
    "peachpuff": (255, 218, 185),
    "peru": (205, 133, 63),
    "pink": (255, 192, 203),
    "plum": (221, 160, 221),
    "powderblue": (176, 224, 230),
    "rosybrown": (188, 143, 143),
    "royalblue": (65, 105, 225),
    "saddlebrown": (139, 69, 19),
    "salmon": (250, 128, 114),
    "sandybrown": (244, 164, 96),
    "seagreen": (46, 139, 87),
    "seashell": (255, 245, 238),
    "sienna": (160, 82, 45),
    "skyblue": (135, 206, 235),
    "slateblue": (106, 90, 205),
    "slategray": (112, 128, 144),
    "slategrey": (112, 128, 144),
    "snow": (255, 250, 250),
    "springgreen": (0, 255, 127),
    "steelblue": (70, 130, 180),
    "tan": (210, 180, 140),
    "thistle": (216, 191, 216),
    "tomato": (255, 99, 71),
    "turquoise": (64, 224, 208),
    "violet": (238, 130, 238),
    "wheat": (245, 222, 179),
    "whitesmoke": (245, 245, 245),
    "yellowgreen": (154, 205, 50),
    "rebeccapurple": (102, 51, 153),
}

PERCENT = r"-?\d+\.?\d*%"
DECIMAL = r"-?\d+\.?\d*"
COMMA = r"\s*,\s*"
OPEN_BRACE = r"\(\s*"
CLOSE_BRACE = r"\s*\)"

RE_COLOR = re.compile(
    rf"""^
\#([0-9a-fA-F]{{3}})$|
\#([0-9a-fA-F]{{4}})$|
\#([0-9a-fA-F]{{6}})$|
\#([0-9a-fA-F]{{8}})$|
rgb{OPEN_BRACE}({DECIMAL}{COMMA}{DECIMAL}{COMMA}{DECIMAL}){CLOSE_BRACE}$|
rgba{OPEN_BRACE}({DECIMAL}{COMMA}{DECIMAL}{COMMA}{DECIMAL}{COMMA}{DECIMAL}){CLOSE_BRACE}$|
hsl{OPEN_BRACE}({DECIMAL}{COMMA}{PERCENT}{COMMA}{PERCENT}){CLOSE_BRACE}$|
hsla{OPEN_BRACE}({DECIMAL}{COMMA}{PERCENT}{COMMA}{PERCENT}{COMMA}{DECIMAL}){CLOSE_BRACE}$
""",
    re.VERBOSE,
)


def _clamp(value, minimum, maximum):
    if minimum > maximum:
        minimum, maximum = maximum, minimum
    if value > maximum:
        return maximum
    elif value < minimum:
        return minimum
    else:
        return value


# Fast way to split a string of 6 characters in to 3 pairs of 2 characters
_split_pairs3: Callable[[str], Tuple[str, str, str]] = itemgetter(
    slice(0, 2), slice(2, 4), slice(4, 6)
)
# Fast way to split a string of 8 characters in to 4 pairs of 2 characters
_split_pairs4: Callable[[str], tuple[str, str, str, str]] = itemgetter(
    slice(0, 2), slice(2, 4), slice(4, 6), slice(6, 8)
)


def get_suggestion(word: str, possible_words: Sequence[str]) -> Optional[str]:
    """
    Returns a close match of `word` amongst `possible_words`.
    Args:
        word (str): The word we want to find a close match for
        possible_words (Sequence[str]): The words amongst which we want to find a close match
    Returns:
        Optional[str]: The closest match amongst the `possible_words`. Returns `None` if no close matches
        could be found.
    Example: returns "red" for word "redu" and possible words ("yellow", "red")
    """
    possible_matches = get_close_matches(word, possible_words, n=1)
    return None if not possible_matches else possible_matches[0]


def rgb_to_lab(rgb: 'Color') -> 'Lab':
    """Convert an RGB color to the CIE-L*ab format.
    Uses the standard RGB color space with a D65/2⁰ standard illuminant.
    Conversion passes through the XYZ color space.
    Cf. http://www.easyrgb.com/en/math.php.
    """

    r, g, b = rgb.red / 255, rgb.green / 255, rgb.blue / 255

    r = pow((r + 0.055) / 1.055, 2.4) if r > 0.04045 else r / 12.92
    g = pow((g + 0.055) / 1.055, 2.4) if g > 0.04045 else g / 12.92
    b = pow((b + 0.055) / 1.055, 2.4) if b > 0.04045 else b / 12.92

    x = (r * 41.24 + g * 35.76 + b * 18.05) / 95.047
    y = (r * 21.26 + g * 71.52 + b * 7.22) / 100
    z = (r * 1.93 + g * 11.92 + b * 95.05) / 108.883

    off = 16 / 116
    x = pow(x, 1 / 3) if x > 0.008856 else 7.787 * x + off
    y = pow(y, 1 / 3) if y > 0.008856 else 7.787 * y + off
    z = pow(z, 1 / 3) if z > 0.008856 else 7.787 * z + off

    return Lab(116 * y - 16, 500 * (x - y), 200 * (y - z))


def lab_to_rgb(lab: 'Lab', alpha: float = 1.0) -> 'Color':
    """Convert a CIE-L*ab color to RGB.
    Uses the standard RGB color space with a D65/2⁰ standard illuminant.
    Conversion passes through the XYZ color space.
    Cf. http://www.easyrgb.com/en/math.php.
    """

    y = (lab.L + 16) / 116
    x = lab.a / 500 + y
    z = y - lab.b / 200

    off = 16 / 116
    y = pow(y, 3) if y > 0.2068930344 else (y - off) / 7.787
    x = 0.95047 * pow(x, 3) if x > 0.2068930344 else 0.122059 * (x - off)
    z = 1.08883 * pow(z, 3) if z > 0.2068930344 else 0.139827 * (z - off)

    r = x * 3.2406 + y * -1.5372 + z * -0.4986
    g = x * -0.9689 + y * 1.8758 + z * 0.0415
    b = x * 0.0557 + y * -0.2040 + z * 1.0570

    r = 1.055 * pow(r, 1 / 2.4) - 0.055 if r > 0.0031308 else 12.92 * r
    g = 1.055 * pow(g, 1 / 2.4) - 0.055 if g > 0.0031308 else 12.92 * g
    b = 1.055 * pow(b, 1 / 2.4) - 0.055 if b > 0.0031308 else 12.92 * b

    return Color(int(r * 255), int(g * 255), int(b * 255), alpha)


def percentage_string_to_float(string: str) -> float:
    """Convert a string percentage e.g. '20%' to a float e.g. 20.0.
    Args:
        string (str): The percentage string to convert.
    """
    string = string.strip()
    if string.endswith("%"):
        float_percentage = _clamp(float(string[:-1]) / 100.0, 0.0, 1.0)
    else:
        float_percentage = float(string)
    return float_percentage


class ColorParseError(Exception):
    """A color failed to parse.
    Args:
        message (str): the error message
        suggested_color (str | None): a close color we can suggest. Defaults to None.
    """

    def __init__(self, message: str, suggested_color: Optional[str] = None):
        super().__init__(message)
        self.suggested_color = suggested_color


class HSL(NamedTuple):
    """A color in HLS format."""

    hue: float
    """Hue"""
    saturation: float
    """Saturation"""
    lightness: float
    """Lightness"""

    @property
    def css(self) -> str:
        """HSL in css format."""
        hue, saturation, lightness = self

        def as_str(number: float) -> str:
            """Cast float to string."""
            return f"{number:.1f}".rstrip("0").rstrip(".")

        return f"hsl({as_str(hue * 360)},{as_str(saturation * 100)}%,{as_str(lightness * 100)}%)"


class HSV(NamedTuple):
    """A color in HSV format."""

    hue: float
    """Hue"""
    saturation: float
    """Saturation"""
    value: float
    """Value"""


class Lab(NamedTuple):
    """A color in CIE-L*ab format."""

    L: float
    a: float
    b: float


class Color(NamedTuple):
    """A class to represent a RGB color with an alpha component."""

    red: int
    """Red component (0-255)"""
    green: int
    """Green component (0-255)"""
    blue: int
    """Blue component (0-255)"""
    alpha: float = 1.0
    """Alpha component (0-1)"""

    @classmethod
    def from_hsl(cls, hue: float, saturation: float, lightness: float) -> 'Color':
        """Create a color from HLS components.

        Parameters
        ----------
        hue : float
            Hue
        saturation : float
            Saturation
        lightness : float
            Lightness

        Returns
        -------
            Color
            A new colo

        """
        red, green, blue = hls_to_rgb(hue, lightness, saturation)
        return cls(int(red * 255 + 0.5), int(green * 255 + 0.5), int(blue * 255 + 0.5))

    @property
    def inverse(self) -> 'Color':
        """The inverse of this color."""
        red, green, blue, alpha = self
        return Color(255 - red, 255 - green, 255 - blue, alpha)

    @property
    def is_transparent(self) -> bool:
        """Check if the color is transparent, i.e. has 0 alpha.

        Returns:
            bool: True if transparent, otherwise False.
        """
        return self.alpha == 0

    @property
    def clamped(self) -> 'Color':
        """Get a color with all components saturated to maximum and minimum values.

        Returns:
            Color: A color object.
        """
        red, green, blue, alpha = self
        color = Color(
            _clamp(red, 0, 255),
            _clamp(green, 0, 255),
            _clamp(blue, 0, 255),
            _clamp(alpha, 0.0, 1.0),
        )
        return color

    @property
    def normalized(self) -> tuple[float, float, float]:
        """A tuple of the color components normalized to between 0 and 1.

        Returns:
            tuple[float, float, float]: Normalized components.
        """
        red, green, blue, _ = self
        return red / 255, green / 255, blue / 255

    @property
    def rgb(self) -> tuple[int, int, int]:
        """Get just the red, green, and blue components.

        Returns:
            tuple[int, int, int]: Color components
        """
        red, green, blue, _ = self
        return red, green, blue

    @property
    def hsl(self) -> HSL:
        """Get the color as HSL.

        Returns:
            HSL: Color in HSL format.
        """
        red, green, blue = self.normalized
        hue, lightness, saturation = rgb_to_hls(red, green, blue)
        return HSL(hue, saturation, lightness)

    @property
    def brightness(self) -> float:
        """Get the human perceptual brightness.

        Returns:
            float: Brightness value (0-1).
        """
        red, green, blue = self.normalized
        brightness = (299 * red + 587 * green + 114 * blue) / 1000
        return brightness

    @property
    def hex(self) -> str:
        """The color in CSS hex form, with 6 digits for RGB, and 8 digits for RGBA.

        Returns:
            str: A CSS hex-style color, e.g. `"#46b3de"` or `"#3342457f"`
        """
        red, green, blue, alpha = self.clamped
        return (
            f"#{red:02X}{green:02X}{blue:02X}"
            if alpha == 1
            else f"#{red:02X}{green:02X}{blue:02X}{int(alpha * 255):02X}"
        )

    @property
    def hex6(self) -> str:
        """The color in CSS hex form, with 6 digits for RGB. Alpha is ignored.

        Returns:
            str: A CSS hex-style color, e.g. "#46b3de"
        """
        red, green, blue, _ = self.clamped
        return f"#{red:02X}{green:02X}{blue:02X}"

    @property
    def css(self) -> str:
        """The color in CSS rgb or rgba form.

        Returns:
            str: A CSS style color, e.g. `"rgb(10,20,30)"` or `"rgb(50,70,80,0.5)"`
        """
        red, green, blue, alpha = self
        return f"rgb({red},{green},{blue})" if alpha == 1 else f"rgba({red},{green},{blue},{alpha})"

    @property
    def monochrome(self) -> 'Color':
        """Get alpha monochrome version of this color.

        Returns:
            Color: A new monochrome color.
        """
        red, green, blue, alpha = self
        gray = round(red * 0.2126 + green * 0.7152 + blue * 0.0722)
        return Color(gray, gray, gray, alpha)

    def with_alpha(self, alpha: float) -> 'Color':
        """Create a new color with the given alpha.

        Parameters
        ----------
        alpha : float
            New value for transparency.

        Returns
        -------
            Color
            A new color

        """
        red, green, blue, _ = self
        return Color(red, green, blue, alpha)

    def blend(self, other: 'Color', factor: float, alpha: Optional[float] = None) -> 'Color':
        """Generate a new color between two colors.

        Parameters
        ----------
        other : Color
            Another color.
        factor : float
            A blend factor, must be between 0 and 1.
        alpha : Optional[float]
            New alpha for results.

        Returns
        -------
            Color
            A new color.
        """
        if factor == 0:
            return self
        elif factor == 1:
            return other
        r1, g1, b1, a1 = self
        r2, g2, b2, a2 = other

        if alpha is None:
            new_alpha = a1 + (a2 - a1) * factor
        else:
            new_alpha = alpha

        return Color(
            int(r1 + (r2 - r1) * factor),
            int(g1 + (g2 - g1) * factor),
            int(b1 + (b2 - b1) * factor),
            new_alpha,
        )

    def __add__(self, other: object) -> 'Color':
        if isinstance(other, Color):
            new_color = self.blend(other, other.alpha, alpha=1.0)
            return new_color
        return NotImplemented

    @classmethod
    @lru_cache(maxsize=1024 * 4)
    def parse(cls, color_text: Union[str, 'Color']) -> 'Color':
        """Parse a string containing a named color or CSS-style color.
        Colors may be parsed from the following formats:
        Text beginning with a `#` is parsed as hex:
        R, G, and B must be hex digits (0-9A-F)
        - `#RGB`
        - `#RRGGBB`
        - `#RRGGBBAA`
        Text in the following formats is parsed as decimal values:
        RED, GREEN, and BLUE must be numbers between 0 and 255.
        ALPHA should ba a value between 0 and 1.
        - `rgb(RED,GREEN,BLUE)`
        - `rgba(RED,GREEN,BLUE,ALPHA)`
        - `hsl(RED,GREEN,BLUE)`
        - `hsla(RED,GREEN,BLUE,ALPHA)`
        All other text will raise a `ColorParseError`.

        Parameters
        ----------
        color_text : Union[str, Color]
            Text with a valid color format. Color objects will be returned unmodified.

        Raises
        ------
            ColorParseError : If the color is not encoded correctly.

        Returns
        -------
            Color: New color object.
        """
        if isinstance(color_text, Color):
            return color_text
        color_from_name = COLOR_NAME_TO_RGB.get(color_text)
        if color_from_name is not None:
            return cls(*color_from_name)
        color_match = RE_COLOR.match(color_text)
        if color_match is None:
            error_message = f"failed to parse {color_text!r} as a color"
            suggested_color = None
            if not color_text.startswith(("#", "rgb", "hsl")):
                # Seems like we tried to use a color name: let's try to find one that is close enough:
                suggested_color = get_suggestion(color_text, COLOR_NAME_TO_RGB.keys())
                if suggested_color:
                    error_message += f"; did you mean '{suggested_color}'?"
            raise ColorParseError(error_message, suggested_color)
        (
            rgb_hex_triple,
            rgb_hex_quad,
            rgb_hex,
            rgba_hex,
            rgb,
            rgba,
            hsl,
            hsla,
        ) = color_match.groups()

        if rgb_hex_triple is not None:
            r, g, b = rgb_hex_triple
            color = cls(int(f"{r}{r}", 16), int(f"{g}{g}", 16), int(f"{b}{b}", 16))
        elif rgb_hex_quad is not None:
            r, g, b, alpha = rgb_hex_quad
            color = cls(
                int(f"{r}{r}", 16),
                int(f"{g}{g}", 16),
                int(f"{b}{b}", 16),
                int(f"{alpha}{alpha}", 16) / 255.0,
            )
        elif rgb_hex is not None:
            r, g, b = [int(pair, 16) for pair in _split_pairs3(rgb_hex)]
            color = cls(r, g, b, 1.0)
        elif rgba_hex is not None:
            r, g, b, alpha = [int(pair, 16) for pair in _split_pairs4(rgba_hex)]
            color = cls(r, g, b, alpha / 255.0)
        elif rgb is not None:
            r, g, b = [_clamp(int(float(value)), 0, 255) for value in rgb.split(",")]
            color = cls(r, g, b, 1.0)
        elif rgba is not None:
            float_r, float_g, float_b, float_a = [
                float(value) for value in rgba.split(",")
            ]
            color = cls(
                _clamp(int(float_r), 0, 255),
                _clamp(int(float_g), 0, 255),
                _clamp(int(float_b), 0, 255),
                _clamp(float_a, 0.0, 1.0),
            )
        elif hsl is not None:
            hue, saturation, lightness = hsl.split(",")
            hue = float(hue) % 360 / 360
            saturation = percentage_string_to_float(saturation)
            lightness = percentage_string_to_float(lightness)
            color = Color.from_hsl(hue, saturation, lightness)
        elif hsla is not None:
            hue, saturation, lightness, alpha = hsla.split(",")
            hue = float(hue) % 360 / 360
            saturation = percentage_string_to_float(saturation)
            lightness = percentage_string_to_float(lightness)
            alpha = _clamp(float(alpha), 0.0, 1.0)
            color = Color.from_hsl(hue, saturation, lightness).with_alpha(alpha)
        else:
            raise AssertionError("Can't get here if RE_COLOR matches")
        return color

    @lru_cache(maxsize=1024)
    def darken(self, amount: float, alpha: Optional[float] = None) -> 'Color':
        """Darken the color by a given amount.

        Parameters
        ----------
        amount : float
            Value between 0-1 to reduce luminance by.
        alpha : Optional[alpha]
            Alpha component for new color or None to copy alpha. Defaults to None.

        Returns
        -------
            Color
            New color.

        """
        l, a, b = rgb_to_lab(self)
        l -= amount * 100
        return lab_to_rgb(Lab(l, a, b), self.alpha if alpha is None else alpha).clamped

    def lighten(self, amount: float, alpha: Optional[float] = None) -> 'Color':
        """Lighten the color by a given amount.
        Args:
            amount (float): Value between 0-1 to increase luminance by.
            alpha (float | None, optional): Alpha component for new color or None to copy alpha. Defaults to None.
        Returns:
            Color: New color.
        """
        return self.darken(-amount, alpha)

    @lru_cache(maxsize=1024)
    def get_contrast_text(self, alpha=0.95) -> 'Color':
        """Get a light or dark color that best contrasts this color, for use with text.
        Args:
            alpha (float, optional): An alpha value to adjust the pure white / black by.
                Defaults to 0.95.
        Returns:
            Color: A new color, either an off-white or off-black
        """
        brightness = self.brightness
        white_contrast = abs(brightness - WHITE.brightness)
        black_contrast = abs(brightness - BLACK.brightness)
        return (WHITE if white_contrast > black_contrast else BLACK).with_alpha(alpha)


# Color constants
WHITE = Color(255, 255, 255)
BLACK = Color(0, 0, 0)
