import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io

def _get_font_path(family, is_italic=False):
    fonts_dir = os.path.join("static", "fonts")
    candidates = [f for f in os.listdir(fonts_dir) if f.lower().endswith(".ttf")]

    if is_italic:
        # Only look at files that BOTH start with family and contain Italic
        for f in candidates:
            if f.startswith(family) and "Italic" in f:
                return os.path.join(fonts_dir, f)
    else:
        # Prefer files that start with family AND do not contain Italic
        for f in candidates:
            if f.startswith(family) and "Italic" not in f:
                return os.path.join(fonts_dir, f)
    for f in candidates:
        if f.startswith(family):
            return os.path.join(fonts_dir, f)

    return os.path.join(fonts_dir, f"{family}.ttf")

# For drawing value texts that are not dictionaries but not simple strings
def draw_key_values(
        draw: ImageDraw.Draw,
        x_center: int,
        y: int,
        data: dict,
        font: ImageFont.FreeTypeFont,
        line_spacing: int = 4
    ) -> int:

    ascent, descent = font.getmetrics()
    line_h = ascent + descent
    cur_y = y

    for key, val in data.items():
        # Draw the value
        txt = str(val)
        w_txt = draw.textlength(txt, font=font)
        draw.text(
            (x_center - w_txt/2, cur_y),
            txt,
            font=font,
            fill="black"
        )
        cur_y += line_h + line_spacing

    return cur_y - y

def render_display(display_data, output_path="rendered.png", rotated=False):
    if rotated:
        width, height = display_data["resolutionY"], display_data["resolutionX"]
    else:
        width, height = display_data["resolutionX"], display_data["resolutionY"]

    canvas = Image.new("RGB", (width, height), "white")
    draw   = ImageDraw.Draw(canvas)

    # Loop widgets
    for widget in display_data.get("widgets", []):
        x, y      = widget.get("x", 0), widget.get("y", 0)
        size      = int(widget.get("fontSize", 16))
        family    = widget.get("fontFamily", "Merriweather")
        italic    = widget.get("isItalic", False)
        bold      = widget.get("isBold", False)

        font_path = _get_font_path(family, is_italic=italic)
        font      = ImageFont.truetype(font_path, size)

        # For simulating bold (loading from bold font wasn't working)
        stroke_w = max(1, size // 200) if bold else 0

        if widget["type"] == "StaticText":
            draw.text(
                (x, y),
                widget["text"],
                font=font,
                fill="black",
                stroke_width=stroke_w,
                stroke_fill="black"
            )
        
        # If there's an extra "value" wrapper, render vertically
        elif isinstance(widget.get("value"), dict) and "value" in widget["value"]:
             inner = widget["value"]["value"]
             # Expected exactly one record inside
             if isinstance(inner, dict) and len(inner)==1:
                 record = next(iter(inner.values()))
                 cx = x + widget.get("width",0)/2
                 draw_key_values(draw, int(cx), y, record, font, line_spacing=2)
             else:
                 # Fallback to table if it's not exactly one record
                 draw_table(draw, x, y, widget["value"], font, padding=2)

        elif isinstance(widget.get("value"), dict):
            print(f"[RENDERING] Printing out table")
            draw_table(draw, x, y, widget["value"], font, padding=2)

        elif widget["type"] == "ValueText":
            if(type(widget["value"]) is int or type(widget["value"]) is float):
                decim = widget.get("decimals", 0)
                if decim > 0:
                    txt = f"{widget.get('value',0):.{decim}f}{widget.get('unit','')}"
                else:
                    txt = f"{widget.get('value',0):.0f}{widget.get('unit','')}"
            else:
                txt = f"{widget.get('value','')}{widget.get('unit','')}"
            draw.text(
                (x, y),
                txt,
                font=font,
                fill="black",
                stroke_width=stroke_w,
                stroke_fill="black"
            )

        elif widget["type"] == "ProgressBar":
            bar_w = int(widget.get("width", 100))
            bar_h = int(widget.get("height", 20))
            pct   = float(widget.get("value", 0)) / widget.get("scale", 100)
            draw.rectangle([x, y, x+bar_w, y+bar_h], outline="black", fill="white")
            draw.rectangle([x, y, x+int(bar_w*pct), y+bar_h],
                            fill=widget.get("color","blue"))
        elif widget["type"] == "Image" and widget.get("filename"):
            img = Image.open(f"./static/uploads/{widget['filename']}")\
                        .resize((widget["width"], widget["height"]))
            canvas.paste(img, (x, y))
        else:
            print(f"[RENDERING]Unknown widget type: {widget.get('type')}")

    canvas.save(output_path, format='PNG')
    print("[RENDERING] Rendering complete.")
    print(f"[RENDERING] Saved to {output_path}")


def draw_table(draw, x, y, table_data, font, padding=0, row_height=None, header_stroke=1):
    if not table_data:
        return
    
    print(table_data.keys())
    headers = list(table_data.values())[0].keys()

    labels  = [h.replace("_"," ").title() for h in headers]

    # Compute column widths
    col_ws = []
    for i, h in enumerate(headers):
        w = draw.textlength(labels[i], font=font)
        for row in table_data.values():
            w = max(w, draw.textlength(str(row.get(h,"")), font=font))
        col_ws.append(w + padding*2)

    # Determine row height
    if row_height is None:
        ascent, descent = font.getmetrics()
        row_height = ascent + descent + padding

    # Draw header
    cur_x = x
    for i, lab in enumerate(labels):
        textw = draw.textlength(lab, font=font)
        draw.text(
            (cur_x + (col_ws[i]-textw)/2, y),
            lab,
            font=font,
            fill="black",
            stroke_width=header_stroke,
            stroke_fill="black"
        )
        cur_x += col_ws[i]

    # Draw data rows
    for ri, row in enumerate(table_data.values()):
        yy    = y + row_height*(ri+1)
        cur_x = x
        for i, h in enumerate(headers):
            txt = str(row.get(h,""))
            textw = draw.textlength(txt, font=font)
            draw.text((cur_x + (col_ws[i]-textw)/2, yy),
                    txt, font=font, fill="black")
            cur_x += col_ws[i]




def transform_image(png_bytes: bytes,
                     rotated: bool,
                     flipX: bool,
                     flipY: bool) -> bytes:

    img = Image.open(io.BytesIO(png_bytes)).convert('RGB')

    # Mirror first (so rotation acts on the flipped result)
    if flipX:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if flipY:
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

    # Rotate with expand so we get the full rotated bounding box
    if rotated:
        img = img.rotate(-90, expand=True)

    # Serialize back to PNG bytes
    out = io.BytesIO()
    img.save(out, format='PNG')
    return out.getvalue()

def convert_image_to_1bpp_bin(input_path, output_path, width, height):
    try:
        image = Image.open(input_path).convert('L')
        image = image.resize((width, height), resample=Image.NEAREST)
        image = image.point(lambda p: 255 if p > 128 else 0, mode='1')

        # Convert image to numpy array for easier manipulation
        pixels = np.array(image, dtype=np.uint8)

        byte_array = bytearray()

        bytes_per_row = (width + 7) // 8  
        for y in range(height):
            byte = 0
            bit_count = 0
            for x in range(width):
                byte = (byte << 1) | pixels[y, x]
                bit_count += 1
                if bit_count == 8:
                    try:
                        byte_array.append(byte)
                        byte = 0
                        bit_count = 0
                    except Exception as e:
                        print(f"Error: {e}")
            if bit_count > 0:
                byte = byte << (8 - bit_count)
                byte_array.append(byte)

            # Pad to 32 bytes per row if needed
            while len(byte_array) % bytes_per_row != 0:
                byte_array.append(0x00)

        with open(output_path, 'wb') as f:
            f.write(byte_array)

        return f"Saved {len(byte_array)} bytes to {output_path}"
    except Exception as e:
        return str(e)

def convert_image_to_4bpp_bin(input_path, output_path, width, height):
    print(f"Processing: {input_path}")
    try:
        image = Image.open(input_path).convert('L')
        image = image.resize((width, height), resample=Image.NEAREST)

        with open(output_path, 'wb') as f:
            byte_count = 0
            #source: https://github.com/Xinyuan-LilyGO/LilyGo-EPD47/blob/esp32s3/scripts/imgconvert.py
            for y in range(0, height):
                byte = 0
                done = True
                for x in range(0, width):
                    l = image.getpixel((x, y))
                    if x % 2 == 0:
                        byte = l >> 4
                        done = False
                    else:
                        byte |= l & 0xF0
                        f.write(byte.to_bytes(1, 'big'))
                        byte_count += 1
                        done = True
                if not done:
                    f.write(byte.to_bytes(1, 'big'))
            print(f"Bytes written: {byte_count} (expected: {(width*height)//2})")
    except Exception as e:
        print(f"Error: {e}")


