from typing import Any, Dict, List, Optional, Tuple, Union

from pygments.token import STANDARD_TYPES


from zulipterminal.themes import gruvbox_dark, gruvbox_light, zt_blue, zt_dark, zt_light


StyleSpec = Union[
    Tuple[Optional[str], str, str],
    Tuple[Optional[str], str, str, Optional[str]],
    Tuple[Optional[str], str, str, Optional[str], str, str],
]
ThemeSpec = List[StyleSpec]

# fmt: off
# The keys in REQUIRED_STYLES specify what styles are necessary for a theme to
# be complete, while the values are those used to style each element in
# monochrome (1-bit) mode - independently of the specified theme
REQUIRED_STYLES = {
    # style name      : monochrome style
    None              : '',
    'selected'        : 'standout',
    'msg_selected'    : 'standout',
    'header'          : 'bold',
    'general_narrow'  : 'standout',
    'general_bar'     : '',
    'name'            : '',
    'unread'          : 'strikethrough',
    'user_active'     : 'bold',
    'user_idle'       : '',
    'user_offline'    : '',
    'user_inactive'   : '',
    'title'           : 'bold',
    'column_title'    : 'bold',
    'time'            : '',
    'bar'             : 'standout',
    'msg_emoji'       : 'bold',
    'reaction'        : 'bold',
    'reaction_mine'   : 'standout',
    'msg_heading'     : 'bold',
    'msg_math'        : 'standout',
    'msg_mention'     : 'bold',
    'msg_link'        : '',
    'msg_link_index'  : 'bold',
    'msg_quote'       : 'underline',
    'msg_code'        : 'bold',
    'msg_bold'        : 'bold',
    'msg_time'        : 'bold',
    'footer'          : 'standout',
    'footer_contrast' : 'standout',
    'starred'         : 'bold',
    'unread_count'    : 'bold',
    'starred_count'   : '',
    'table_head'      : 'bold',
    'filter_results'  : 'bold',
    'edit_topic'      : 'standout',
    'edit_tag'        : 'standout',
    'edit_author'     : 'bold',
    'edit_time'       : 'bold',
    'current_user'    : '',
    'muted'           : 'bold',
    'popup_border'    : 'bold',
    'popup_category'  : 'bold',
    'popup_contrast'  : 'standout',
    'popup_important' : 'bold',
    'widget_disabled' : 'strikethrough',
    'area:help'       : 'standout',
    'area:msg'        : 'standout',
    'area:stream'     : 'standout',
    'area:error'      : 'standout',
    'area:user'       : 'standout',
    'search_error'    : 'standout',
    'task:success'    : 'standout',
    'task:error'      : 'standout',
    'task:warning'    : 'standout',
}

REQUIRED_META = {
    'pygments': {
        'styles'     : None,
        'background' : None,
        'overrides'  : None,
    }
}
# fmt: on

# This is the main list of themes
THEMES: Dict[str, Any] = {
    "gruvbox_dark": gruvbox_dark,
    "gruvbox_light": gruvbox_light,
    "zt_dark": zt_dark,
    "zt_light": zt_light,
    "zt_blue": zt_blue,
}

# These are older aliases to some of the above, for compatibility
# NOTE: Do not add to this section, and only modify if a theme name changes
THEME_ALIASES = {
    "default": "zt_dark",
    "gruvbox": "gruvbox_dark",
    "light": "zt_light",
    "blue": "zt_blue",
}

# These are urwid color names with underscores instead of spaces
valid_16_color_codes = [
    "default",
    "black",
    "dark_red",
    "dark_green",
    "brown",
    "dark_blue",
    "dark_magenta",
    "dark_cyan",
    "dark_gray",
    "light_red",
    "light_green",
    "yellow",
    "light_blue",
    "light_magenta",
    "light_cyan",
    "light_gray",
    "white",
]


class InvalidThemeColorCode(Exception):
    pass


def all_themes() -> List[str]:
    return list(THEMES.keys())


def aliased_themes() -> Dict[str, str]:
    return dict(THEME_ALIASES)


def complete_and_incomplete_themes() -> Tuple[List[str], List[str]]:
    complete = {
        name
        for name, theme in THEMES.items()
        if set(theme.STYLES) == set(REQUIRED_STYLES)
        if set(theme.META) == set(REQUIRED_META)
        for meta, conf in theme.META.items()
        if set(conf) == set(REQUIRED_META.get(meta, {}))
    }
    incomplete = list(set(THEMES) - complete)
    return sorted(list(complete)), sorted(incomplete)


def generate_theme(theme_name: str, color_depth: int) -> ThemeSpec:
    theme_styles = THEMES[theme_name].STYLES
    validate_colors(theme_name, color_depth)
    urwid_theme = parse_themefile(theme_styles, color_depth)

    try:
        theme_meta = THEMES[theme_name].META
        add_pygments_style(theme_meta, urwid_theme)
    except AttributeError:
        pass

    return urwid_theme


def validate_colors(theme_name: str, color_depth: int) -> None:
    """
    This function validates color-codes for a given theme, given colors are in `Color`.

    If any color is not in accordance with urwid default 16-color codes then the
    function raises InvalidThemeColorCode with the invalid colors.
    """
    theme_colors = THEMES[theme_name].Color
    failure_text = []
    if color_depth == 16:
        for color in theme_colors:
            color_16code = color.value.split()[0]
            if color_16code not in valid_16_color_codes:
                invalid_16_color_code = str(color.name)
                failure_text.append(f"- {invalid_16_color_code} = {color_16code}")
        if failure_text == []:
            return
        else:
            text = "\n".join(
                [f"Invalid 16-color codes in theme '{theme_name}':"] + failure_text
            )
            raise InvalidThemeColorCode(text)


def parse_themefile(
    theme_styles: Dict[Optional[str], Tuple[Any, Any]], color_depth: int
) -> ThemeSpec:
    """This function takes a dictionary of theme styles and a color depth including 1, 16, 256 and 2^24 as input and returns a list of theme specifications in the urwid format. It iterates over the theme styles dictionary and converts the color codes and properties based on the specified color depth. The converted theme specifications are then added to the list.
    Input-Output Arguments
    :param theme_styles: Dict[Optional[str], Tuple[Any, Any]]. A dictionary containing the theme styles where the keys are style names and the values are tuples of foreground and background colors.
    :param color_depth: int. The color depth to be used for converting the color codes. It can be 1, 16, 256, or 2^24.
    :return: ThemeSpec. A list of theme specifications in the urwid format.
    """


def add_pygments_style(theme_meta: Dict[str, Any], urwid_theme: ThemeSpec) -> None:
    """
    This function adds pygments styles for use in syntax
    highlighting of code blocks and inline code.
    pygments["styles"]:
        one of those available in pygments/styles.
    pygments["background"]:
        used to set a different background for codeblocks instead of the
        one used in the syntax style, if it doesn't match with
        the overall zt theme.
        The default is available as Eg: MaterialStyle.background_color
    pygments["overrides"]:
        used to override certain pygments styles to match to urwid format.
        It can also be used to customize the syntax style.
    """
    from zulipterminal.config.color import term16
    pygments = theme_meta["pygments"]
    pygments_styles = pygments["styles"]
    pygments_bg = pygments["background"]
    pygments_overrides = pygments["overrides"]

    term16_styles = term16.styles
    term16_bg = term16.background_color

    for token, css_class in STANDARD_TYPES.items():
        if css_class in pygments_overrides:
            pygments_styles[token] = pygments_overrides[css_class]

        # Inherit parent pygments style if not defined.
        # Eg: Use `String` if `String.Double` is not present.
        if pygments_styles[token] == "":
            try:
                t = [k for k, v in STANDARD_TYPES.items() if v == css_class[0]]
                pygments_styles[token] = pygments_styles[t[0]]
            except IndexError:
                pass

        if term16_styles[token] == "":
            try:
                t = [k for k, v in STANDARD_TYPES.items() if v == css_class[0]]
                term16_styles[token] = term16_styles[t[0]]
            except IndexError:
                pass

        new_style = (
            f"pygments:{css_class}",
            term16_styles[token],
            term16_bg,
            "bold",  # Mono style
            pygments_styles[token],
            pygments_bg,
        )
        urwid_theme.append(new_style)