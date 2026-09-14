import base64


def image_bytes_to_data_uri(data: bytes, mime: str) -> str:
    base64_data = base64.b64encode(data).decode("utf-8")
    return f"data:{mime};base64,{base64_data}"
