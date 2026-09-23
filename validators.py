"""
validators.py
--------------
Small, single-purpose functions that check whether a piece of user
input is valid, and explain *why* when it isn't.
"""

import re

# A person's name: must start with a letter, and after that can only
# contain letters, spaces, hyphens, apostrophes and periods. This covers

_PERSON_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z'\-. ]{1,49}$")

# An equipment name or category: CAN include digits, because real
# equipment names/categories do (e.g. "Canon EOS M50", "3D Printing").
# Letters, digits, spaces are allowed
_EQUIPMENT_TEXT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9'\-./() ]{1,59}$")

# Email: allows letters AND digits mixed together on both sides of the
# @ (e.g. "jemima98@example.com" is valid) -- this is a simple, readable
# check, not a full RFC 5322 validator, but it catches the obvious

_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

# Phone number: digits, with an OPTIONAL leading + (international
# numbers start with one, e.g. "+230...") and OPTIONAL dashes between
# groups of digits (e.g. "57-123-456"). Both are entirely optional

_PHONE_RE = re.compile(r"^\+?[0-9]+(?:-[0-9]+)*$")

# above only checks the SHAPE (where + and - are allowed to
# sit). Separately, once the + and - are stripped out, there still
# need to be a realistic number of actual digits 7 to 15 of them,
# covering everything from a short local number to a full
# international one.
_PHONE_DIGIT_COUNT_MIN = 7
_PHONE_DIGIT_COUNT_MAX = 15


def validate_person_name(raw, field_label="Name"):
    value = raw.strip()
    if not value:
        raise ValueError(f"{field_label} can't be blank.")
    if not _PERSON_NAME_RE.match(value):
        raise ValueError(
            f"{field_label} should only contain letters, spaces, "
            f"hyphens or apostrophes (e.g. 'Jean-Paul' or \"O'Brien\") "
            f"-- no numbers or other symbols.")
    return value


def validate_equipment_text(raw, field_label="This field"):
    value = raw.strip()
    if not value:
        raise ValueError(f"{field_label} can't be blank.")
    if not _EQUIPMENT_TEXT_RE.match(value):
        raise ValueError(
            f"{field_label} should only contain letters, numbers, "
            f"spaces, or basic punctuation (- ' . / ()) -- no other "
            f"symbols.")
    if not any(ch.isalpha() for ch in value):
        raise ValueError(
            f"{field_label} needs at least one letter in it, not just "
            f"numbers.")
    return value


def validate_email(raw):
    value = raw.strip()
    if not value:
        raise ValueError("Email can't be blank.")
    if not _EMAIL_RE.match(value):
        raise ValueError(
            "That doesn't look like a valid email (expected something "
            "like name123@example.com -- letters and numbers are both "
            "fine).")
    return value


def validate_phone(raw, allow_blank=True):
    value = raw.strip()
    if not value:
        if allow_blank:
            return ""
        raise ValueError("Phone number can't be blank.")

    if not _PHONE_RE.match(value):
        raise ValueError(
            "Phone number should be digits only")

    
    digits_only = value.replace("+", "").replace("-", "")
    if not (_PHONE_DIGIT_COUNT_MIN <= len(digits_only) <= _PHONE_DIGIT_COUNT_MAX):
        raise ValueError(
            f"Phone number should have {_PHONE_DIGIT_COUNT_MIN}-"
            f"{_PHONE_DIGIT_COUNT_MAX} digits in total (not counting "
            f"+ or -) -- '{value}' has {len(digits_only)}.")

    return value
