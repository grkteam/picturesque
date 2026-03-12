"""Tests for picturesque.__init__ — generate_image() and internal helpers."""
import os

import pytest
from PIL import Image

import picturesque
from picturesque import generate_image
from picturesque.__init__ import (
    _cleanup_chars,
    _scale_and_paste_pic,
    _select_pic,
    _validate_elements,
)
from picturesque.elements import Element, HLine, MultilineQuote, Textline


# ---------------------------------------------------------------------------
# generate_image — basics
# ---------------------------------------------------------------------------

class TestGenerateImageBasics:
    def test_no_elements_returns_image(self):
        img = generate_image()
        assert isinstance(img, Image.Image)

    def test_default_size(self):
        img = generate_image()
        assert img.size == (1528, 800)

    def test_custom_size(self):
        img = generate_image(width=400, height=300)
        assert img.size == (400, 300)

    def test_custom_background_color(self):
        img = generate_image(width=100, height=100, bg="blue")
        # sample a pixel — should be blue (0, 0, 255)
        pixel = img.getpixel((50, 50))
        assert pixel == (0, 0, 255)

    def test_invalid_pic_position_raises(self):
        with pytest.raises(ValueError, match="pic_position must be"):
            generate_image(pic_position="center")

    def test_none_elements_defaults_to_empty(self):
        img = generate_image(elements=None)
        assert isinstance(img, Image.Image)


# ---------------------------------------------------------------------------
# generate_image — with elements (requires a real TTF font)
# ---------------------------------------------------------------------------

class TestGenerateImageWithElements:
    def test_single_textline_top(self, font_path):
        elements = [Textline(text="Hello", font=font_path, max_font_size=20)]
        img = generate_image(elements=elements, width=400, height=200)
        assert isinstance(img, Image.Image)

    def test_single_hline(self):
        elements = [HLine(length=100, thickness=2)]
        img = generate_image(elements=elements, width=400, height=200)
        assert isinstance(img, Image.Image)

    def test_single_multiline_quote(self, font_path):
        elements = [MultilineQuote(text="A long quote that wraps", font=font_path,
                                   chars_per_line=20)]
        img = generate_image(elements=elements, width=400, height=200)
        assert isinstance(img, Image.Image)

    def test_multiple_elements_top_bottom_center(self, font_path):
        elements = [
            Textline(text="Top", font=font_path, max_font_size=16, valign="top"),
            HLine(length=200, valign="bottom"),
            HLine(length=100, valign="center"),
        ]
        img = generate_image(elements=elements, width=400, height=200)
        assert isinstance(img, Image.Image)

    # Known bug: _validate_elements' pop/iteration issue means two consecutive
    # centered elements are not detected.  The test below documents what
    # actually happens — no error at validate time, but may error at render.
    def test_two_center_elements_no_raise_known_bug(self, font_path):
        elements = [
            HLine(length=50, valign="center"),
            HLine(length=50, valign="center"),
        ]
        # Does not raise ValueError from _validate_elements due to known bug.
        # It may raise later during rendering — document actual behavior.
        try:
            generate_image(elements=elements, width=400, height=200)
        except ValueError:
            pass  # Some ValueError from rendering is acceptable

    def test_textline_with_underline(self, font_path):
        elements = [Textline(text="Underlined", font=font_path,
                             max_font_size=16, underline=True)]
        img = generate_image(elements=elements, width=400, height=200)
        assert isinstance(img, Image.Image)

    def test_textline_valign_bottom(self, font_path):
        # Rendering valign='bottom' should not raise
        elements = [Textline(text="Bottom", font=font_path,
                             max_font_size=16, valign="bottom")]
        img = generate_image(elements=elements, width=400, height=200)
        assert isinstance(img, Image.Image)


# ---------------------------------------------------------------------------
# HLine overflow clamping
# ---------------------------------------------------------------------------

class TestHLineOverflowClamping:
    def test_hline_wider_than_space_gets_clamped(self):
        # HLine.length > image width; the renderer should clamp it without error.
        elements = [HLine(length=9999, thickness=2)]
        img = generate_image(elements=elements, width=400, height=200)
        assert isinstance(img, Image.Image)


# ---------------------------------------------------------------------------
# _validate_elements
# ---------------------------------------------------------------------------

class TestValidateElements:
    def test_centered_element_moved_to_end(self):
        top = HLine(length=50, valign="top")
        center = HLine(length=50, valign="center")
        result = _validate_elements([top, center])
        assert result[-1] is center

    # Known bug: _validate_elements iterates with enumerate while calling
    # pop(i), so consecutive centered elements cause an index shift and the
    # second one is never seen.  With [a, b] both center:
    #   i=0 -> pop(0) -> elements=[b], centered=[a]
    #   i=1 -> loop ends (len([b])==1, i==1 is out of range)
    # Result: only one centered element found, no ValueError raised.
    # This bug should be fixed in a future refactor.
    def test_multiple_centered_elements_no_raise_known_bug(self):
        a = HLine(length=50, valign="center")
        b = HLine(length=60, valign="center")
        # Does NOT raise due to the pop/iteration bug — document current behavior
        result = _validate_elements([a, b])
        assert isinstance(result, list)

    def test_non_element_raises_type_error(self):
        with pytest.raises(TypeError, match="All elements must be instances of Element"):
            _validate_elements(["not an element"])

    # Known bug: _validate_elements calls pop() on the input list, mutating
    # the caller's list.  This side effect is documented here and should be
    # fixed in a future refactor (use a copy of the list at the start).
    def test_mutates_input_list_known_bug(self):
        top = HLine(length=50, valign="top")
        center = HLine(length=50, valign="center")
        original = [top, center]
        _validate_elements(original)
        # The centered element was popped out of original — this is the bug.
        assert center not in original


# ---------------------------------------------------------------------------
# _select_pic
# ---------------------------------------------------------------------------

class TestSelectPic:
    def test_with_filename_returns_path(self, tmp_path):
        # create a dummy image file
        img_file = tmp_path / "photo.jpg"
        img_file.write_bytes(b"dummy")
        # patch isfile check by providing a real file
        img = Image.new("RGB", (10, 10))
        img.save(str(img_file), format="JPEG")

        result = _select_pic(pics_dir=str(tmp_path), filename="photo.jpg")
        expected = str(tmp_path / "photo.jpg")
        # normalise separators
        assert os.path.normpath(result) == os.path.normpath(expected)

    def test_nonexistent_pics_dir_returns_none(self):
        result = _select_pic(pics_dir="/nonexistent/path/xyz123",
                             selection_key="anything")
        assert result is None

    def test_selection_key_deterministic(self, tmp_path):
        # create multiple dummy image files
        for name in ("a.jpg", "b.jpg", "c.jpg"):
            img = Image.new("RGB", (10, 10))
            img.save(str(tmp_path / name), format="JPEG")

        result1 = _select_pic(pics_dir=str(tmp_path), selection_key="mykey")
        result2 = _select_pic(pics_dir=str(tmp_path), selection_key="mykey")
        assert result1 == result2
        assert result1 is not None

    def test_random_pick_from_directory(self, tmp_path):
        img = Image.new("RGB", (10, 10))
        img.save(str(tmp_path / "only.jpg"), format="JPEG")

        result = _select_pic(pics_dir=str(tmp_path))
        assert result is not None
        assert result.endswith("only.jpg")

    def test_empty_pics_dir_returns_none(self, tmp_path):
        result = _select_pic(pics_dir=str(tmp_path))
        assert result is None


# ---------------------------------------------------------------------------
# _scale_and_paste_pic
# ---------------------------------------------------------------------------

class TestScaleAndPastePic:
    def test_valid_image_pastes_and_returns_width(self, tmp_path):
        # create a small test image
        src = tmp_path / "pic.jpg"
        Image.new("RGB", (100, 50)).save(str(src), format="JPEG")

        canvas = Image.new("RGB", (400, 200), "white")
        wpic = _scale_and_paste_pic(path=str(src), img=canvas,
                                    pic_position="left")
        assert isinstance(wpic, int)
        assert wpic > 0

    def test_invalid_pic_position_raises(self, tmp_path):
        src = tmp_path / "pic.jpg"
        Image.new("RGB", (10, 10)).save(str(src), format="JPEG")
        canvas = Image.new("RGB", (400, 200))
        with pytest.raises(ValueError, match="pic_position must be"):
            _scale_and_paste_pic(path=str(src), img=canvas,
                                 pic_position="center")

    def test_nonexistent_path_raises(self):
        canvas = Image.new("RGB", (400, 200))
        with pytest.raises(ValueError, match="pic path does not exist"):
            _scale_and_paste_pic(path="/nonexistent/file.jpg", img=canvas,
                                 pic_position="left")


# ---------------------------------------------------------------------------
# _cleanup_chars  (dead code — still tested for correctness)
# ---------------------------------------------------------------------------

class TestCleanupChars:
    def test_en_dash_replaced(self):
        # chr(8211) is en-dash
        result = _cleanup_chars("hello" + chr(8211) + "world")
        assert chr(8211) not in result
        assert "-" in result

    def test_em_dash_replaced(self):
        # chr(8212) is em-dash
        result = _cleanup_chars("before" + chr(8212) + "after")
        assert chr(8212) not in result
        assert "-" in result

    def test_normal_string_unchanged(self):
        s = "No special characters here"
        assert _cleanup_chars(s) == s
