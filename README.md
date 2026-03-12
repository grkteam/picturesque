# picturesque

Postcard-like image generation from textual posts and pics.

## Installation

```bash
pip install picturesque
```

## Quick usage

```python
import picturesque

heading = picturesque.Textline(
    text='COMPANY NAME',
    font='arialbd.ttf',
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
    font='modern-monospace-regular.ttf',
    chars_per_line=36,
    color='#2d3192',
    valign='center',
    line_spacing_px=20,
    hmargin=50,
    vmargin=0,
)

footer = picturesque.Textline(
    text='www.example.com/thread/ab01lO4',
    font='cour.ttf',
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

## Repository

[https://github.com/grkteam/picturesque](https://github.com/grkteam/picturesque)
