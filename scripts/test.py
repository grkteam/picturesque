import picturesque

PALE_YELLOW = '#fef8e8'
LOGO_RED = '#cd2027'
DARK_BLUE = '#2d3192'
URL_BLUE = 'blue'


def test(width=1528, height=800, bg=PALE_YELLOW,
         company_name='Company Name',
         sub_text='Example.com',
         text='This is some text just to try if this works...',
         url='www.example.com/thread/ab01lO4',
         head_color=DARK_BLUE, line_color=DARK_BLUE,
         sub_color=LOGO_RED, text_color=DARK_BLUE,
         url_color=URL_BLUE,
         line_width=500, line_height=2,
         head_hmargin=30, head_vmargin=70,
         line_hmargin=0, line_vmargin=20,
         sub_hmargin=10, sub_vmargin=13,
         text_hmargin=50, text_vmargin=0,
         url_hmargin=30, url_vmargin=50,
         head_font='arialbd.ttf',
         sub_font='verdana.ttf',
         text_font='modern-monospace-regular.ttf',
         url_font='cour.ttf',
         head_max_font_size=192, sub_max_font_size=84,
         text_chars_per_line=36, url_max_font_size=60):

    heading = picturesque.Textline(text=company_name.upper(),
                              font=head_font,
                              max_font_size=head_max_font_size,
                              color=head_color,
                              hmargin=head_hmargin,
                              vmargin=head_vmargin)

    line = picturesque.HLine(length=line_width,
                        thickness=line_height,
                        color=line_color,
                        hmargin=line_hmargin,
                        vmargin=line_vmargin)

    subheading = picturesque.Textline(text=sub_text,
                                 font=sub_font,
                                 max_font_size=sub_max_font_size,
                                 color=sub_color,
                                 hmargin=sub_hmargin,
                                 vmargin=sub_vmargin)

    quote = picturesque.MultilineQuote(text=text,
                                  font=text_font,
                                  chars_per_line=text_chars_per_line,
                                  color=text_color,
                                  valign='center',
                                  line_spacing_px=20,
                                  hmargin=text_hmargin,
                                  vmargin=text_vmargin)

    footer = picturesque.Textline(text=url,
                             font=url_font,
                             max_font_size=url_max_font_size,
                             color=url_color,
                             underline=True,
                             underline_thickness=4,
                             valign='bottom',
                             hmargin=url_hmargin,
                             vmargin=url_vmargin)

    elements = [heading, line, subheading, quote, footer]

    img = picturesque.generate_image(
        elements=elements,
        width=1528, height=800, bg=bg,
        pic_selection_key=url,
        pic_position='left')

    img.save('test.jpg', quality=90)
    return img


if __name__ == '__main__':
    test()
