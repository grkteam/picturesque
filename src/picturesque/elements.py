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
    def __init__(self, color='black', align='center', valign='top',
                 hmargin=10, vmargin=10):
        assert align in {'left', 'right', 'center'}
        assert valign in {'top', 'bottom', 'center'}
        assert isinstance(hmargin, int)
        assert isinstance(vmargin, int)
        self.color = color
        self.align = align
        self.valign = valign
        self.hmargin = hmargin
        self.vmargin = vmargin


class Textline(Element):
    def __init__(self, text=None, font=None, font_size=None, max_font_size=16,
                 underline=False, underline_thickness=1, **kwargs):
        Element.__init__(self, **kwargs)
        assert text
        assert not (font_size and max_font_size)
        assert underline in {True, False}
        self.text = text
        self.font = font
        self.font_size = font_size
        self.max_font_size = max_font_size
        self.underline = underline
        self.underline_thickness = underline_thickness


class MultilineQuote(Element):
    def __init__(self, text=None, font=None, chars_per_line=40,
                 line_spacing_px=0, **kwargs):
        Element.__init__(self, **kwargs)
        assert isinstance(chars_per_line, int) and chars_per_line > 0
        self.text = text
        self.font = font
        self.chars_per_line = chars_per_line
        self.line_spacing_px = line_spacing_px


class HLine(Element):
    def __init__(self, length=100, thickness=2, **kwargs):
        Element.__init__(self, **kwargs)
        assert isinstance(length, int) and length > 0
        assert isinstance(thickness, int) and thickness > 0
        self.length = length
        self.thickness = thickness
