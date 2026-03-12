from __future__ import annotations

from typing import Literal


class Element:
    """Common ancestor for all elements, useless on its own.

    color : str (color name: 'blue' or hex string '#ffddcc')
        Color of text or line

    align : str ('center'|'left'|'right')
        Horizontal alignment

    valign : str ('top'|'bottom'|'center')
        Vertical alignment.
        Note: only one element can have valign=='center'

    hmargin : int (pixels)
        Horizontal margin: left and right

    vmargin : int (pixels)
        Top margin if valign=='top', bottom margin if valign=='bottom'
    """
    def __init__(self, color: str = 'black',
                 align: Literal['left', 'right', 'center'] = 'center',
                 valign: Literal['top', 'bottom', 'center'] = 'top',
                 hmargin: int = 10, vmargin: int = 10) -> None:
        if align not in {'left', 'right', 'center'}:
            raise ValueError(f"align must be 'left', 'right', or 'center'; got {align!r}")
        if valign not in {'top', 'bottom', 'center'}:
            raise ValueError(f"valign must be 'top', 'bottom', or 'center'; got {valign!r}")
        if not isinstance(hmargin, int):
            raise TypeError(f'hmargin must be an int; got {type(hmargin).__name__}')
        if not isinstance(vmargin, int):
            raise TypeError(f'vmargin must be an int; got {type(vmargin).__name__}')
        self.color = color
        self.align = align
        self.valign = valign
        self.hmargin = hmargin
        self.vmargin = vmargin


class Textline(Element):
    """A single line of text rendered at the largest font size that fits.

    Parameters
    ----------
    text : str
        The text to render. Must be a non-empty string.
    font : str
        Path to a TrueType font file (e.g. ``'fonts/arial.ttf'``).
    font_size : int, optional
        Fixed font size in points. Mutually exclusive with *max_font_size*.
    max_font_size : int, optional
        Upper bound for auto-sized rendering (default 16). The renderer
        decreases the size until the text fits within the available width.
        Mutually exclusive with *font_size*.
    underline : bool, optional
        Whether to draw an underline beneath the text (default ``False``).
    underline_thickness : int, optional
        Thickness of the underline in pixels (default 1).
    color : str, optional
        Color of text (default ``'black'``).
    align : str, optional
        Horizontal alignment — ``'left'``, ``'right'``, or ``'center'``
        (default ``'center'``).
    valign : str, optional
        Vertical alignment — ``'top'``, ``'bottom'``, or ``'center'``
        (default ``'top'``).
    hmargin : int, optional
        Horizontal margin in pixels (default 10).
    vmargin : int, optional
        Vertical margin in pixels (default 10).
    """
    def __init__(self, text: str, font: str, font_size: int | None = None,
                 max_font_size: int = 16, underline: bool = False,
                 underline_thickness: int = 1, color: str = 'black',
                 align: Literal['left', 'right', 'center'] = 'center',
                 valign: Literal['top', 'bottom', 'center'] = 'top',
                 hmargin: int = 10, vmargin: int = 10) -> None:
        Element.__init__(self, color=color, align=align, valign=valign,
                         hmargin=hmargin, vmargin=vmargin)
        if not text:
            raise ValueError('text must be a non-empty string')
        if font_size and max_font_size:
            raise ValueError('Specify either font_size or max_font_size, not both')
        if underline not in {True, False}:
            raise TypeError(f'underline must be True or False; got {underline!r}')
        self.text = text
        self.font = font
        self.font_size = font_size
        self.max_font_size = max_font_size
        self.underline = underline
        self.underline_thickness = underline_thickness


class MultilineQuote(Element):
    """A block of text wrapped across multiple lines with decorative quotes.

    Parameters
    ----------
    text : str
        The text to render. It is automatically wrapped at *chars_per_line*
        characters and surrounded by curly quotes.
    font : str
        Path to a TrueType font file (e.g. ``'fonts/cour.ttf'``).
    chars_per_line : int, optional
        Maximum number of characters per wrapped line (default 40).
    line_spacing_px : int, optional
        Extra spacing between lines in pixels (default 0).
    color : str, optional
        Color of text (default ``'black'``).
    align : str, optional
        Horizontal alignment — ``'left'``, ``'right'``, or ``'center'``
        (default ``'center'``).
    valign : str, optional
        Vertical alignment — ``'top'``, ``'bottom'``, or ``'center'``
        (default ``'top'``).
    hmargin : int, optional
        Horizontal margin in pixels (default 10).
    vmargin : int, optional
        Vertical margin in pixels (default 10).
    """
    def __init__(self, text: str, font: str, chars_per_line: int = 40,
                 line_spacing_px: int = 0, color: str = 'black',
                 align: Literal['left', 'right', 'center'] = 'center',
                 valign: Literal['top', 'bottom', 'center'] = 'top',
                 hmargin: int = 10, vmargin: int = 10) -> None:
        Element.__init__(self, color=color, align=align, valign=valign,
                         hmargin=hmargin, vmargin=vmargin)
        if not (isinstance(chars_per_line, int) and chars_per_line > 0):
            raise ValueError(f'chars_per_line must be a positive int; got {chars_per_line!r}')
        self.text = text
        self.font = font
        self.chars_per_line = chars_per_line
        self.line_spacing_px = line_spacing_px


class HLine(Element):
    """A horizontal rule drawn across the image.

    Parameters
    ----------
    length : int, optional
        Length of the line in pixels (default 100).
    thickness : int, optional
        Thickness of the line in pixels (default 2).
    color : str, optional
        Color of the line (default ``'black'``).
    align : str, optional
        Horizontal alignment — ``'left'``, ``'right'``, or ``'center'``
        (default ``'center'``).
    valign : str, optional
        Vertical alignment — ``'top'``, ``'bottom'``, or ``'center'``
        (default ``'top'``).
    hmargin : int, optional
        Horizontal margin in pixels (default 10).
    vmargin : int, optional
        Vertical margin in pixels (default 10).
    """
    def __init__(self, length: int = 100, thickness: int = 2,
                 color: str = 'black',
                 align: Literal['left', 'right', 'center'] = 'center',
                 valign: Literal['top', 'bottom', 'center'] = 'top',
                 hmargin: int = 10, vmargin: int = 10) -> None:
        Element.__init__(self, color=color, align=align, valign=valign,
                         hmargin=hmargin, vmargin=vmargin)
        if not (isinstance(length, int) and length > 0):
            raise ValueError(f'length must be a positive int; got {length!r}')
        if not (isinstance(thickness, int) and thickness > 0):
            raise ValueError(f'thickness must be a positive int; got {thickness!r}')
        self.length = length
        self.thickness = thickness
