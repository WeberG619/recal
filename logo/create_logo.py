"""
Create NeverOnce logo — clean, modern, developer-focused.
The logo represents memory that corrects itself:
a circular recall arrow with a checkmark (correction) integrated.
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def draw_arc(draw, center, radius, start_angle, end_angle, color, width):
    """Draw a thick arc."""
    bbox = [
        center[0] - radius, center[1] - radius,
        center[0] + radius, center[1] + radius
    ]
    draw.arc(bbox, start_angle, end_angle, fill=color, width=width)


def draw_arrowhead(draw, tip_x, tip_y, angle_deg, size, color):
    """Draw a filled arrowhead pointing in the given direction."""
    angle = math.radians(angle_deg)
    left_angle = angle + math.radians(150)
    right_angle = angle - math.radians(150)

    points = [
        (tip_x, tip_y),
        (tip_x + size * math.cos(left_angle), tip_y + size * math.sin(left_angle)),
        (tip_x + size * math.cos(right_angle), tip_y + size * math.sin(right_angle)),
    ]
    draw.polygon(points, fill=color)


def create_logo(size=1024, bg_color=None, dark=False):
    """Create the NeverOnce logo."""
    if bg_color is None:
        bg_color = (20, 20, 30) if dark else (255, 255, 255, 0)

    img = Image.new("RGBA", (size, size), bg_color)
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2

    # Colors
    primary = (99, 179, 237)      # Blue — recall/memory
    accent = (72, 219, 148)       # Green — correction/success
    dark_text = (30, 30, 40) if not dark else (240, 240, 245)

    # Main circular arrow (the "recall" symbol)
    radius = int(size * 0.35)
    arc_width = int(size * 0.06)

    # Draw the circular arrow — a ~300 degree arc
    draw_arc(draw, (cx, cy), radius, -210, 90, primary, arc_width)

    # Arrowhead at the end of the arc (top, pointing right/down)
    arrow_angle_rad = math.radians(-210)
    arrow_x = cx + radius * math.cos(arrow_angle_rad)
    arrow_y = cy + radius * math.sin(arrow_angle_rad)
    draw_arrowhead(draw, arrow_x, arrow_y, -120, int(size * 0.08), primary)

    # Checkmark in the center (the "correction" symbol)
    check_size = int(size * 0.18)
    check_cx = cx - int(check_size * 0.1)
    check_cy = cy + int(check_size * 0.05)
    check_width = int(size * 0.045)

    # Short stroke of checkmark
    p1 = (check_cx - check_size * 0.4, check_cy)
    p2 = (check_cx, check_cy + check_size * 0.4)
    draw.line([p1, p2], fill=accent, width=check_width, joint="curve")

    # Long stroke of checkmark
    p3 = (check_cx + check_size * 0.6, check_cy - check_size * 0.5)
    draw.line([p2, p3], fill=accent, width=check_width, joint="curve")

    return img


def create_logo_with_text(size=1024, dark=False):
    """Create logo with 'NeverOnce' text below."""
    logo = create_logo(int(size * 0.6), dark=dark)

    bg_color = (20, 20, 30, 255) if dark else (255, 255, 255, 0)
    full = Image.new("RGBA", (size, int(size * 1.2)), bg_color)

    # Paste logo centered at top
    logo_x = (size - logo.width) // 2
    full.paste(logo, (logo_x, int(size * 0.05)), logo)

    # Add text
    draw = ImageDraw.Draw(full)
    text_color = (240, 240, 245) if dark else (30, 30, 40)

    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    font = None
    for fp in font_paths:
        if os.path.exists(fp):
            font = ImageFont.truetype(fp, int(size * 0.12))
            break
    if not font:
        font = ImageFont.load_default()

    text = "NeverOnce"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_x = (size - text_w) // 2
    text_y = int(size * 0.72)
    draw.text((text_x, text_y), text, fill=text_color, font=font)

    # Tagline
    tag_font = None
    for fp in font_paths:
        if os.path.exists(fp):
            tag_font = ImageFont.truetype(fp.replace("-Bold", ""), int(size * 0.04))
            break
    if tag_font:
        tagline = "Memory that learns from mistakes"
        tbbox = draw.textbbox((0, 0), tagline, font=tag_font)
        tag_w = tbbox[2] - tbbox[0]
        tag_x = (size - tag_w) // 2
        tag_y = text_y + int(size * 0.14)
        tag_color = (150, 150, 160) if dark else (100, 100, 110)
        draw.text((tag_x, tag_y), tagline, fill=tag_color, font=tag_font)

    return full


def create_favicon(size=64):
    """Create a small favicon version."""
    logo = create_logo(size * 4, bg_color=(99, 179, 237, 255))
    # Make it circular
    mask = Image.new("L", (size * 4, size * 4), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse([0, 0, size * 4, size * 4], fill=255)

    bg = Image.new("RGBA", (size * 4, size * 4), (99, 179, 237, 255))
    result = Image.composite(logo, bg, mask)
    result = result.resize((size, size), Image.LANCZOS)
    return result


if __name__ == "__main__":
    print("Creating NeverOnce logos...\n")

    # 1. Icon only (transparent background)
    logo = create_logo(1024)
    logo.save(os.path.join(OUTPUT_DIR, "neveronce_icon.png"))
    print("  neveronce_icon.png (1024x1024, transparent)")

    # 2. Icon dark background
    logo_dark = create_logo(1024, dark=True)
    logo_dark.save(os.path.join(OUTPUT_DIR, "neveronce_icon_dark.png"))
    print("  neveronce_icon_dark.png (1024x1024, dark bg)")

    # 3. Full logo with text (transparent)
    full = create_logo_with_text(1024)
    full.save(os.path.join(OUTPUT_DIR, "neveronce_logo.png"))
    print("  neveronce_logo.png (1024x1228, with text)")

    # 4. Full logo dark
    full_dark = create_logo_with_text(1024, dark=True)
    full_dark.save(os.path.join(OUTPUT_DIR, "neveronce_logo_dark.png"))
    print("  neveronce_logo_dark.png (1024x1228, dark)")

    # 5. Favicon
    fav = create_favicon(64)
    fav.save(os.path.join(OUTPUT_DIR, "favicon.png"))
    print("  favicon.png (64x64)")

    # 6. GitHub social preview (1280x640)
    social = Image.new("RGBA", (1280, 640), (20, 20, 30, 255))
    social_draw = ImageDraw.Draw(social)

    # Logo on left
    small_logo = create_logo(400, dark=True)
    social.paste(small_logo, (80, 120), small_logo)

    # Text on right
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    title_font = tag_font = desc_font = None
    for fp in font_paths:
        if os.path.exists(fp):
            title_font = ImageFont.truetype(fp, 72)
            tag_font = ImageFont.truetype(fp.replace("-Bold", ""), 28)
            desc_font = ImageFont.truetype(fp.replace("-Bold", ""), 22)
            break

    if title_font:
        social_draw.text((540, 180), "NeverOnce", fill=(240, 240, 245), font=title_font)
        social_draw.text((540, 270), "Persistent, correctable memory for AI", fill=(150, 150, 160), font=tag_font)
        social_draw.text((540, 340), "pip install neveronce", fill=(72, 219, 148), font=desc_font)
        social_draw.text((540, 390), "400 lines  |  Zero dependencies  |  Any LLM", fill=(120, 120, 130), font=desc_font)
        social_draw.text((540, 430), "Store → Recall → Correct → Feedback → Decay", fill=(99, 179, 237), font=desc_font)

    social.save(os.path.join(OUTPUT_DIR, "social_preview.png"))
    print("  social_preview.png (1280x640, GitHub social)")

    print("\nAll logos created!")
