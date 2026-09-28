from io import BytesIO
import qrcode


def generate_qr_png(data, size=10):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=size,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def verification_url(request_obj, external=True):
    from flask import url_for
    return url_for("public_verify", ref=request_obj.reference, _external=external)