import hashlib


def generate_qr_code_text(salt: str, id: str):
    return hashlib.md5((salt + id).encode("utf-8")).hexdigest()
