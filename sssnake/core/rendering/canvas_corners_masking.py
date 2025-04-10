from PIL import Image, ImageDraw


def add_corners(im, rad, fill_color):

    circle = Image.new('L', (rad * 2, rad * 2), 0)

    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)

    alpha = Image.new('L', im.size, 255)

    w, h = im.size

    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))

    im.putalpha(alpha)

    return composite_with_bg(im, fill_color)

def composite_with_bg(img, bg_color):
    bg = Image.new("RGBA", img.size, bg_color)
    return Image.alpha_composite(bg, img)