"""Tests for picturesque.elements — Element, Textline, MultilineQuote, HLine."""
import pytest

from picturesque.elements import Element, HLine, MultilineQuote, Textline


# ---------------------------------------------------------------------------
# Element
# ---------------------------------------------------------------------------

class TestElement:
    def test_defaults(self):
        e = Element()
        assert e.color == "black"
        assert e.align == "center"
        assert e.valign == "top"
        assert e.hmargin == 10
        assert e.vmargin == 10

    def test_explicit_values(self):
        e = Element(color="red", align="left", valign="bottom",
                    hmargin=20, vmargin=30)
        assert e.color == "red"
        assert e.align == "left"
        assert e.valign == "bottom"
        assert e.hmargin == 20
        assert e.vmargin == 30

    def test_invalid_align(self):
        with pytest.raises(ValueError, match="align must be"):
            Element(align="middle")

    def test_invalid_valign(self):
        with pytest.raises(ValueError, match="valign must be"):
            Element(valign="up")

    def test_hmargin_non_int_raises(self):
        with pytest.raises(TypeError, match="hmargin must be an int"):
            Element(hmargin=10.0)

    def test_vmargin_non_int_raises(self):
        with pytest.raises(TypeError, match="vmargin must be an int"):
            Element(vmargin="5")


# ---------------------------------------------------------------------------
# Textline
# ---------------------------------------------------------------------------

class TestTextline:
    def test_valid_construction_with_max_font_size(self):
        t = Textline(text="Hello", font="fonts/arial.ttf", max_font_size=24)
        assert t.text == "Hello"
        assert t.font == "fonts/arial.ttf"
        assert t.max_font_size == 24
        assert t.font_size is None

    def test_default_values(self):
        t = Textline(text="Hi", font="fonts/arial.ttf")
        assert t.max_font_size == 16
        assert t.font_size is None
        assert t.underline is False
        assert t.underline_thickness == 1

    def test_empty_text_raises(self):
        with pytest.raises(ValueError, match="text must be a non-empty string"):
            Textline(text="", font="fonts/arial.ttf")

    def test_none_text_raises(self):
        with pytest.raises(ValueError, match="text must be a non-empty string"):
            Textline(text=None, font="fonts/arial.ttf")

    def test_font_size_and_max_font_size_raises(self):
        with pytest.raises(ValueError, match="Specify either font_size or max_font_size"):
            Textline(text="Hi", font="fonts/arial.ttf",
                     font_size=24, max_font_size=32)

    def test_font_size_only_succeeds(self):
        t = Textline(text="Hi", font="fonts/arial.ttf", font_size=24)
        assert t.font_size == 24
        assert t.max_font_size is None

    def test_invalid_underline_raises(self):
        with pytest.raises(TypeError, match="underline must be True or False"):
            Textline(text="Hi", font="fonts/arial.ttf", underline="yes")

    def test_underline_true(self):
        t = Textline(text="Hi", font="fonts/arial.ttf", underline=True)
        assert t.underline is True

    def test_kwargs_forwarded_to_element(self):
        t = Textline(text="Hi", font="fonts/arial.ttf",
                     color="blue", align="left", valign="bottom",
                     hmargin=5, vmargin=5)
        assert t.color == "blue"
        assert t.align == "left"
        assert t.valign == "bottom"


# ---------------------------------------------------------------------------
# MultilineQuote
# ---------------------------------------------------------------------------

class TestMultilineQuote:
    def test_valid_construction(self):
        m = MultilineQuote(text="Some long text here", font="fonts/cour.ttf",
                           chars_per_line=20)
        assert m.text == "Some long text here"
        assert m.font == "fonts/cour.ttf"
        assert m.chars_per_line == 20

    def test_default_values(self):
        m = MultilineQuote(text="Hello", font="fonts/cour.ttf")
        assert m.chars_per_line == 40
        assert m.line_spacing_px == 0

    def test_chars_per_line_zero_raises(self):
        with pytest.raises(ValueError, match="chars_per_line must be a positive int"):
            MultilineQuote(text="Hi", font="fonts/cour.ttf", chars_per_line=0)

    def test_chars_per_line_negative_raises(self):
        with pytest.raises(ValueError, match="chars_per_line must be a positive int"):
            MultilineQuote(text="Hi", font="fonts/cour.ttf", chars_per_line=-1)

    def test_chars_per_line_non_int_raises(self):
        with pytest.raises(ValueError, match="chars_per_line must be a positive int"):
            MultilineQuote(text="Hi", font="fonts/cour.ttf", chars_per_line=40.5)

    def test_kwargs_forwarded_to_element(self):
        m = MultilineQuote(text="Hi", font="fonts/cour.ttf",
                           color="red", valign="bottom")
        assert m.color == "red"
        assert m.valign == "bottom"


# ---------------------------------------------------------------------------
# HLine
# ---------------------------------------------------------------------------

class TestHLine:
    def test_valid_construction(self):
        h = HLine(length=200, thickness=3)
        assert h.length == 200
        assert h.thickness == 3

    def test_default_values(self):
        h = HLine()
        assert h.length == 100
        assert h.thickness == 2

    def test_length_zero_raises(self):
        with pytest.raises(ValueError, match="length must be a positive int"):
            HLine(length=0)

    def test_length_negative_raises(self):
        with pytest.raises(ValueError, match="length must be a positive int"):
            HLine(length=-5)

    def test_length_non_int_raises(self):
        with pytest.raises(ValueError, match="length must be a positive int"):
            HLine(length=100.5)

    def test_thickness_zero_raises(self):
        with pytest.raises(ValueError, match="thickness must be a positive int"):
            HLine(thickness=0)

    def test_thickness_negative_raises(self):
        with pytest.raises(ValueError, match="thickness must be a positive int"):
            HLine(thickness=-1)

    def test_thickness_non_int_raises(self):
        with pytest.raises(ValueError, match="thickness must be a positive int"):
            HLine(thickness=2.5)

    def test_kwargs_forwarded_to_element(self):
        h = HLine(length=50, thickness=1, align="left", valign="bottom")
        assert h.align == "left"
        assert h.valign == "bottom"
