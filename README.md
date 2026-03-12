# picturesque

Postcard-like image generation from textual posts and pics.

## Installation

```bash
pip install picturesque
```

## Quick usage

> **Font paths:** the `font` parameter accepts any path (absolute or relative
> to the working directory) pointing to a `.ttf` file.  The examples below
> assume fonts live in a `fonts/` subdirectory — adjust the paths to match
> your setup.

```python
import picturesque

heading = picturesque.Textline(
    text='COMPANY NAME',
    font='fonts/arialbd.ttf',
    max_font_size=192,
    color='#2d3192',
    hmargin=30,
    vmargin=70,
)

line = picturesque.HLine(
    length=500,
    thickness=2,
    color='#2d3192',
    hmargin=0,
    vmargin=20,
)

quote = picturesque.MultilineQuote(
    text='This is some text just to try if this works...',
    font='fonts/modern-monospace-regular.ttf',
    chars_per_line=36,
    color='#2d3192',
    valign='center',
    line_spacing_px=20,
    hmargin=50,
    vmargin=0,
)

footer = picturesque.Textline(
    text='www.example.com/thread/ab01lO4',
    font='fonts/cour.ttf',
    max_font_size=60,
    color='blue',
    underline=True,
    underline_thickness=4,
    valign='bottom',
    hmargin=30,
    vmargin=50,
)

img = picturesque.generate_image(
    elements=[heading, line, quote, footer],
    width=1528,
    height=800,
    bg='#fef8e8',
    pic_position='left',
)

img.save('output.jpg', quality=90)
```

## How it works

Elements are stacked vertically in the available space (the full image width,
or the portion not occupied by the picture):

- Elements with `valign='top'` are placed from the top downwards, consuming
  space as they go.
- Elements with `valign='bottom'` are placed from the bottom upwards.
- The single element with `valign='center'` (at most one) is placed last,
  centred in whatever space remains between the top and bottom elements.

A picture (`pic_position='left'` or `'right'`) is scaled to the full image
height and pasted on the chosen side before any text elements are drawn.

## API reference

### `generate_image(elements=None, width=1528, height=800, bg='white', pics_dir='pics', pic_filename=None, pic_selection_key=None, pic_position=None)`

Generate a postcard-style image and return a `PIL.Image.Image`.

| Parameter | Type | Description |
|---|---|---|
| `elements` | list | Ordered list of `Textline`, `MultilineQuote`, or `HLine` instances. |
| `width` | int | Image width in pixels (default 1528). |
| `height` | int | Image height in pixels (default 800). |
| `bg` | str | Background colour as a name or hex string (default `'white'`). |
| `pics_dir` | str | Directory containing candidate picture files (default `'pics'`). |
| `pic_filename` | str or None | Exact filename of the picture to use. |
| `pic_selection_key` | str or None | String whose hash deterministically selects a picture from `pics_dir`. |
| `pic_position` | str or None | `'left'`, `'right'`, or `None` (no picture). |

---

### `Textline(text, font, max_font_size=16, font_size=None, underline=False, underline_thickness=1, color='black', align='center', valign='top', hmargin=10, vmargin=10)`

A single line of text rendered at the largest font size that fits.

| Parameter | Type | Description |
|---|---|---|
| `text` | str | Text to render. Must be non-empty. |
| `font` | str | Path to a `.ttf` font file (e.g. `'fonts/arial.ttf'`). May be absolute or relative to the working directory. |
| `max_font_size` | int | Maximum font size; renderer shrinks until text fits (default 16). |
| `font_size` | int | Fixed font size. Mutually exclusive with `max_font_size`. |
| `underline` | bool | Draw an underline beneath the text (default `False`). |
| `underline_thickness` | int | Underline thickness in pixels (default 1). |
| `color` | str | Text colour (default `'black'`). |
| `align` | str | Horizontal alignment: `'left'`, `'center'`, or `'right'` (default `'center'`). |
| `valign` | str | Vertical alignment: `'top'`, `'bottom'`, or `'center'` (default `'top'`). |
| `hmargin` | int | Left/right margin in pixels (default 10). |
| `vmargin` | int | Top margin (for `valign='top'`) or bottom margin (for `valign='bottom'`) in pixels (default 10). |

---

### `MultilineQuote(text, font, chars_per_line=40, line_spacing_px=0, color='black', align='center', valign='top', hmargin=10, vmargin=10)`

A block of text wrapped across multiple lines with decorative quotes.

| Parameter | Type | Description |
|---|---|---|
| `text` | str | Text to render. Automatically wrapped and surrounded by curly quotes. |
| `font` | str | Path to a `.ttf` font file (e.g. `'fonts/cour.ttf'`). May be absolute or relative to the working directory. |
| `chars_per_line` | int | Maximum characters per wrapped line (default 40). |
| `line_spacing_px` | int | Extra spacing between lines in pixels (default 0). |
| `color` | str | Text colour (default `'black'`). |
| `align` | str | Horizontal alignment: `'left'`, `'center'`, or `'right'` (default `'center'`). |
| `valign` | str | Vertical alignment: `'top'`, `'bottom'`, or `'center'` (default `'top'`). |
| `hmargin` | int | Left/right margin in pixels (default 10). |
| `vmargin` | int | Top/bottom margin in pixels (default 10). |

---

### `HLine(length=100, thickness=2, color='black', align='center', valign='top', hmargin=10, vmargin=10)`

A horizontal rule drawn across the image.

| Parameter | Type | Description |
|---|---|---|
| `length` | int | Length of the line in pixels (default 100). |
| `thickness` | int | Thickness of the line in pixels (default 2). |
| `color` | str | Line colour (default `'black'`). |
| `align` | str | Horizontal alignment: `'left'`, `'center'`, or `'right'` (default `'center'`). |
| `valign` | str | Vertical alignment: `'top'`, `'bottom'`, or `'center'` (default `'top'`). |
| `hmargin` | int | Left/right margin in pixels (default 10). |
| `vmargin` | int | Top/bottom margin in pixels (default 10). |

## Repository

[https://github.com/grkteam/picturesque](https://github.com/grkteam/picturesque)
