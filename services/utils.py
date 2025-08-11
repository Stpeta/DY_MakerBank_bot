import random
import string


def gen_registration_code(existing: set[str], length: int = 8) -> str:
    """Return a new unique registration code."""
    alphabet = string.ascii_uppercase + string.digits
    while True:
        code = "".join(random.choices(alphabet, k=length))
        if code not in existing:
            return code

