from __future__ import annotations

import re


PHONE_DEFAULT_LENGTH = 10
PHONE_NUMERIC_MESSAGE = "Phone number can contain digits only."
PHONE_LENGTH_MESSAGE = "Enter a 10-digit phone number."


def strip_phone_digits(value: object) -> str:
    return re.sub(r"\D", "", "" if value is None else str(value))


def validate_digit_phone(
    value: object,
    *,
    required: bool = False,
    min_length: int | None = None,
    max_length: int | None = None,
) -> tuple[str, str]:
    raw = "" if value is None else str(value).strip()
    if raw == "":
        return ("", "This field is required.") if required else ("", "")

    if re.search(r"\D", raw):
        return raw, PHONE_NUMERIC_MESSAGE

    if min_length is None and max_length is None:
        if len(raw) != PHONE_DEFAULT_LENGTH:
            return raw, PHONE_LENGTH_MESSAGE
        return raw, ""

    if min_length is not None and len(raw) < min_length:
        return raw, f"Ensure this value has at least {min_length} characters."
    if max_length is not None and len(raw) > max_length:
        return raw, f"Ensure this value has no more than {max_length} characters."

    return raw, ""
