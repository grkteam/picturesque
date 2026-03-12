import random
import os
import os.path
import textwrap
import PIL
from PIL import Image, ImageDraw, ImageFont
from hashlib import sha1
from .elements import (
    Element,
    Textline,
    MultilineQuote,
    HLine,
)

WIDTH = 1528
HEIGHT = 800
MIN_WSPACE = 100
BG = 'white'
HEAD_COLOR = 'black'
LINE_COLOR = 'black'
SUB_COLOR = 'red'
TEXT_COLOR = 'black'
FOOTER_COLOR = 'blue'
PICS_DIR = 'pics'

char_replacement = {
    chr(8211): '-',
    chr(8212): '-',
}


def generate_image(elements=[], width=WIDTH, height=HEIGHT, bg=BG,
                   pics_dir=PICS_DIR, pic_filename=None,
                   pic_selection_key=None, pic_position=None):
    elements = _validate_elements(elements)
    assert pic_position in {'left', 'right', None}
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
            # find the largest font size that fits ---
            font_sizes = range(e.max_font_size, 12, -1)
            for font_size in font_sizes:
                font = ImageFont.truetype('fonts/'+e.font, font_size)
                _, _, w, h = draw.textbbox(((0, 0)), e.text, font=font)
                if w + 2*e.hmargin < Wspace:
                    break

            # horizontal position
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
                assert i == len(elements) - 1

        elif isinstance(e, MultilineQuote):
            # If using monospace font, then space after newline
            # will pull the opening quote outside of the text alignment
            lines = textwrap.wrap(e.text, e.chars_per_line)
            text = '"' + '\n '.join(lines) + '"'

            # find the largest font size that fits
            text_font_sizes = range(72, 12, -1)
            for font_size in text_font_sizes:
                font = ImageFont.truetype('fonts/'+e.font, font_size)
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
                Y0 += h + 2*e.vmargin
            elif e.valign == 'bottom':
                Y1 -= h + 2*e.vmargin
            else:
                # center valign => last element => no need to adjust
                assert i == len(elements) - 1

        elif isinstance(e, HLine):
            # fix possible overflow
            if e.length + 2*e.hmargin > Wspace:
                e.length = Wspace - 2*e.hmargin

            # horizontal position ---
            if e.align == 'left':
                x0 = X0 + e.hmargin
            elif e.align == 'right':
                x0 = X0 + Wspace - e.length - e.hmargin
            elif e.align == 'center':
                x0 = int(Xc - e.length/2)

            # vertical position ---
            if e.valign == 'top':
                y = Y0 + e.vmargin
            elif e.valign == 'bottom':
                y = Y1 - e.vmargin - e.thickness
            elif e.valign == 'center':
                y = int((Y0 + Y1)/2 - e.thickness/2)

            # draw line
            xy0 = (x0, y)
            xy1 = (x0 + e.length, y)
            draw.line((xy0, xy1), width=e.thickness, fill=e.color)

            # update Y0, Y1
            if e.valign == 'top':
                Y0 += e.vmargin + e.thickness
            elif e.valign == 'bottom':
                Y1 -= e.vmargin + e.thickness
            elif e.valign == 'center':
                # center valign => last element => no need to adjust
                assert i == len(elements) - 1

    return img


def _cleanup_chars(s):
    for bad, good in char_replacement.items():
        s = s.replace(bad, good)
    return s


def _select_pic(pics_dir=None, filename=None, selection_key=None):
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


def _scale_and_paste_pic(path=None, img=None, pic_position='left'):
    assert pic_position in {'left', 'right'}
    assert os.path.isfile(path) is True
    assert isinstance(img, PIL.Image.Image)
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


def _validate_elements(elements):
    assert all(map(lambda x: isinstance(x, Element), elements))
    # only one element can have valign='center'
    centered = []
    for i, e in enumerate(elements):
        if e.valign == 'center':
            centered.append(elements.pop(i))
    if len(centered) > 1:
        raise ValueError('Cannot vertically align more than 1 element')
    # put the vertically centered element at the end:
    # (need to know the available space after all other elements
    #  are positioned)
    elements = elements + centered
    return elements
