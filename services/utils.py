import random, string

def gen_registration_code(existing: set[str], length: int = 8) -> str:
    """Возвращает новый уникальный код."""
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = "".join(random.choices(alphabet, k=length))
        if code not in existing:
            return code