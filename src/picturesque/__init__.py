"""picturesque — postcard-like image generation from text and pictures.

Layout model
------------
Elements are stacked vertically using three alignment modes:

* ``valign='top'``    — placed from the top downwards, consuming space as they go.
* ``valign='bottom'`` — placed from the bottom upwards, consuming space as they go.
* ``valign='center'`` — placed last, centred in whatever space remains between
  the top and bottom elements.  At most one element may use ``valign='center'``.

A picture (``pic_position='left'`` or ``'right'``) is scaled to the full image
height and pasted on the chosen side before any text elements are drawn.
"""
from __future__ import annotations

import random
import os
import os.path
import textwrap
from typing import Literal
import PIL
from PIL import Image, ImageDraw, ImageFont
from hashlib import sha1
from .elements import (
    Element,
    Textline,
    MultilineQuote,
    HLine,
)

__all__ = ['Textline', 'MultilineQuote', 'HLine', 'generate_image', '__version__']

__version__ = "0.1.0"

WIDTH = 1528
HEIGHT = 800
MIN_WSPACE = 100
BG = 'white'
PICS_DIR = 'pics'


def generate_image(elements: list[Element] | None = None, width: int = WIDTH,
                   height: int = HEIGHT, bg: str = BG,
                   pics_dir: str = PICS_DIR, pic_filename: str | None = None,
                   pic_selection_key: str | None = None,
                   pic_position: Literal['left', 'right'] | None = None) -> Image.Image:
    """Generate a postcard-style image from a list of elements.

    Elements are laid out vertically in the available space (the full image
    width, or the portion not occupied by the picture).  Elements with
    ``valign='top'`` are stacked from the top; elements with
    ``valign='bottom'`` are stacked from the bottom; the single element with
    ``valign='center'`` (if any) is placed last in the remaining space.

    Parameters
    ----------
    elements : list of Element, optional
        Ordered list of :class:`Textline`, :class:`MultilineQuote`, or
        :class:`HLine` instances to render.  Defaults to an empty list.
    width : int, optional
        Image width in pixels (default 1528).
    height : int, optional
        Image height in pixels (default 800).
    bg : str, optional
        Background colour as a name or hex string (default ``'white'``).
    pics_dir : str, optional
        Directory that contains candidate picture files (default ``'pics'``).
    pic_filename : str, optional
        Exact filename of the picture to use.  When provided, *pics_dir* is
        used to build the full path.  Mutually exclusive with
        *pic_selection_key*.
    pic_selection_key : str, optional
        Arbitrary string whose hash deterministically selects a picture from
        *pics_dir*.  Mutually exclusive with *pic_filename*.
    pic_position : str or None, optional
        Where to place the picture — ``'left'``, ``'right'``, or ``None``
        (no picture, default).

    Returns
    -------
    PIL.Image.Image
        The rendered image.

    Raises
    ------
    ValueError
        If *pic_position* is not one of ``'left'``, ``'right'``, or ``None``,
        or if more than one element uses ``valign='center'``.
    """
    if elements is None:
        elements = []
    elements = _validate_elements(elements)
    if pic_position not in {'left', 'right', None}:
        raise ValueError(
            f"pic_position must be 'left', 'right', or None; got {pic_position!r}"
        )
    W, H = width, height
    img = Image.new('RGB', (W, H), bg)

    # Scale and position pic onto image ===
    if pic_position:
        pic_path = _select_pic(pics_dir=pics_dir,
                               filename=pic_filename,
                               selection_key=pic_selection_key)
    else:
        pic_path = None
    if pic_path is None:
        Wpic = 0
    else:
        Wpic = _scale_and_paste_pic(path=pic_path, img=img,
                                    pic_position=pic_position)

    draw = ImageDraw.Draw(img)

    Wspace = W - Wpic
    if Wspace < MIN_WSPACE:
        raise ValueError('Not enough space left after pasting pic')
    # X0: left corner of empty space -> remains constant
    if pic_position == 'left':
        X0 = Wpic
    else:
        X0 = 0
    # x coord of empty space center (axis for center alignment):
    Xc = X0 + int(Wspace/2)

    # Y-coordintes of available space -> get updated as space fills up
    Y0 = 0  # top of available space
    Y1 = H  # bottom of available space

    for i, e in enumerate(elements):

        if isinstance(e, Textline):
            # find the font size to use ---
            if e.font_size is not None:
                font = ImageFont.truetype(e.font, e.font_size)
                _, _, w, h = draw.textbbox(((0, 0)), e.text, font=font)
            else:
                font_sizes = range(e.max_font_size, 12, -1)
                for font_size in font_sizes:
                    font = ImageFont.truetype(e.font, font_size)
                    _, _, w, h = draw.textbbox(((0, 0)), e.text, font=font)
                    if w + 2*e.hmargin < Wspace:
                        break

            # horizontal position
            if e.align == 'left':
                x = X0 + e.hmargin
            elif e.align == 'right':
                x = X0 + Wspace - w - e.hmargin
            elif e.align == 'center':
                x = int(Xc - w/2)

            # vertical position
            if e.valign == 'top':
                y = Y0 + e.vmargin
            elif e.valign == 'bottom':
                y = Y1 - e.vmargin - h
            elif e.valign == 'center':
                y = int((Y0 + Y1)/2 - h/2)

            # write text
            draw.text((x, y), e.text, font=font, fill=e.color)
            if e.underline:
                xy0 = (x, y+h)
                xy1 = (x+w, y+h)
                draw.line((xy0, xy1), width=e.underline_thickness,
                          fill=e.color)

            # update Y0, Y1
            if e.valign == 'top':
                Y0 += h + e.vmargin
            elif e.valign == 'bottom':
                Y1 -= h + e.vmargin
            else:
                # center valign => last element => no need to adjust
                if i != len(elements) - 1:
                    raise ValueError(
                        'Only the last element may use valign="center"'
                    )

        elif isinstance(e, MultilineQuote):
            # If using monospace font, then space after newline
            # will pull the opening quote outside of the text alignment
            lines = textwrap.wrap(e.text, e.chars_per_line)
            text = '"' + '\n '.join(lines) + '"'

            # find the largest font size that fits
            text_font_sizes = range(72, 12, -1)
            for font_size in text_font_sizes:
                font = ImageFont.truetype(e.font, font_size)
                _, _, wtext, htext = draw.multiline_textbbox(
                    ((0, 0)), text, font=font,
                    spacing=e.line_spacing_px)
                if ((wtext + 2*e.hmargin < Wspace) and
                        htext + 2*e.vmargin < Y1 - Y0):
                    break

            # horizontal position
            if e.align == 'left':
                x = X0 + e.hmargin
            elif e.align == 'right':
                x = X0 + Wspace - wtext - 2*e.hmargin
            elif e.align == 'center':
                x = int(Xc - wtext/2)

            # vertical position
            if e.valign == 'top':
                y = Y0 + e.vmargin
            elif e.valign == 'bottom':
                y = Y1 - e.vmargin - htext
            elif e.valign == 'center':
                y = int((Y0 + Y1)/2 - htext/2)
            # This may not be necessary:
            if y < Y0:
                y = Y0
            if y + htext > Y1:
                y = Y1 - htext

            # write text
            draw.multiline_text((x, y), text, font=font,
                                fill=e.color, spacing=e.line_spacing_px)

            # update Y0, Y1
            if e.valign == 'top':
                Y0 += htext + 2*e.vmargin
            elif e.valign == 'bottom':
                Y1 -= htext + 2*e.vmargin
            else:
                # center valign => last element => no need to adjust
                if i != len(elements) - 1:
                    raise ValueError(
                        'Only the last element may use valign="center"'
                    )

        elif isinstance(e, HLine):
            # fix possible overflow
            line_length = e.length
            if line_length + 2*e.hmargin > Wspace:
                line_length = Wspace - 2*e.hmargin

            # horizontal position ---
            if e.align == 'left':
                x0 = X0 + e.hmargin
            elif e.align == 'right':
                x0 = X0 + Wspace - line_length - e.hmargin
            elif e.align == 'center':
                x0 = int(Xc - line_length/2)

            # vertical position ---
            if e.valign == 'top':
                y = Y0 + e.vmargin
            elif e.valign == 'bottom':
                y = Y1 - e.vmargin - e.thickness
            elif e.valign == 'center':
                y = int((Y0 + Y1)/2 - e.thickness/2)

            # draw line
            xy0 = (x0, y)
            xy1 = (x0 + line_length, y)
            draw.line((xy0, xy1), width=e.thickness, fill=e.color)

            # update Y0, Y1
            if e.valign == 'top':
                Y0 += e.vmargin + e.thickness
            elif e.valign == 'bottom':
                Y1 -= e.vmargin + e.thickness
            elif e.valign == 'center':
                # center valign => last element => no need to adjust
                if i != len(elements) - 1:
                    raise ValueError(
                        'Only the last element may use valign="center"'
                    )

    return img


def _validate_elements(elements: list[Element]) -> list[Element]:
    if not all(isinstance(x, Element) for x in elements):
        raise TypeError('All elements must be instances of Element')
    non_centered = [e for e in elements if e.valign != 'center']
    centered = [e for e in elements if e.valign == 'center']
    if len(centered) > 1:
        raise ValueError('Cannot vertically align more than 1 element')
    return non_centered + centered


def _select_pic(pics_dir: str | None = None, filename: str | None = None,
                selection_key: str | None = None) -> str | None:
    if filename is None and selection_key is None:
        # select random pic in 'pics' dir
        try:
            pics = os.listdir(pics_dir)
            pic_filename = random.choice(pics)
        except (FileNotFoundError, IndexError):
            return None
    elif filename is not None:
        pic_filename = filename
    else:  # selection_key is not None
        try:
            key_ascii = selection_key.encode('ascii', errors='ignore')
            int_hash = int(sha1(key_ascii).hexdigest(), 16)
            pics = os.listdir(pics_dir)
            i = int_hash % len(pics)
            pic_filename = pics[i]
        except (FileNotFoundError, IndexError):
            return None
    path = f'{pics_dir}/{pic_filename}'
    if not os.path.isfile(path):
        return None
    return path


def _scale_and_paste_pic(path: str, img: Image.Image,
                          pic_position: Literal['left', 'right'] = 'left') -> int:
    if pic_position not in {'left', 'right'}:
        raise ValueError(
            f"pic_position must be 'left' or 'right'; got {pic_position!r}"
        )
    if not os.path.isfile(path):
        raise ValueError(f'pic path does not exist or is not a file: {path!r}')
    if not isinstance(img, PIL.Image.Image):
        raise TypeError(
            f'img must be a PIL.Image.Image; got {type(img).__name__}'
        )
    pic = Image.open(path)
    w, h = pic.size
    W, H = img.size
    # resize pic to height H ---
    factor = H / h
    Wpic = int(w * factor)
    pic_scaled = pic.resize((Wpic, H))
    # paste pic onto img ---
    if pic_position == 'left':
        Xpic = 0
    else:
        Xpic = W - Wpic
    img.paste(pic_scaled, (Xpic, 0))
    return Wpic
