from reportlab.pdfgen import canvas
from reportlab_qrcode import QRCodeImage
from yaml import safe_load

from rally.qr_code import generate_qr_code_text

config = safe_load(open("data/track.yaml", "r"))

WIDTH = 297
HEIGHT = 419
c = canvas.Canvas("qr_codes.pdf", pagesize=(WIDTH, HEIGHT))

for element in config["elements"]:
    if element["type"] == "qr_code":
        c.setFillColorRGB(1, 1, 1)
        c.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
        c.setFillColorRGB(0, 0, 0)

        c.drawImage("static/stuvus-logo.png", (WIDTH - 150) / 2, 340, width=150, height=70, preserveAspectRatio=True)
        def draw_centered_text(text, position, font_size=20, font_name="Helvetica"):
            string_width = c.stringWidth(text, font_name, font_size)
            c.setFont(font_name, font_size)
            c.drawString((WIDTH - string_width) / 2, position, text)


        draw_centered_text("Campus Rally", 320)
        qr = QRCodeImage(generate_qr_code_text(config["qr_salt"], element["id"]), size=250)
        qr.drawOn(c, 24, 50)
        draw_centered_text(f"ID: {element['id']}", 30, font_size=15)
        c.showPage()

c.save()
