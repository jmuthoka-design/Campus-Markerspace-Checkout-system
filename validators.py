"""
validators.py
--------------
single-purpose functions that check whether a piece of user
input is valid, and when it isn't.
main.py calls these functions while it's still asking the question (so it can
re-prompt immediately). 
"""

import re

# A person's name: must start with a letter, and after that can only
# contain letters, spaces, hyphens, apostrophes and periods. 
_PERSON_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z'\-. ]{1,49}$")

# An equipment name or category: CAN include digits, because real
# equipment names/categories do (e.g. "Canon EOS M50", "3D Printing").
# Letters, digits, spaces, and a few common punctuation marks are
# allowed; must contain at least one letter so something like "12345"
# on its own is still rejected.
_EQUIPMENT_TEXT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9'\-./() ]{1,59}$")

# Email: allows letters AND digits mixed together on both sides of the
# @ (e.g"jemima98@example.com" is valid)this is a simple, readable
_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

# Phone number: digits only. No +,-, spaces, or parentheses just
# whole numbers, 7 to 15 digits long (covers everything from a short
# local number to a full international one).
_PHONE_RE = re.compile(r"^[0-9]{7,15}$")


def validate_person_name(raw, field_label="Name"):
    value = raw.strip()
    if not value:
        raise ValueError(f"{field_label} can't be blank.")
    if not _PERSON_NAME_RE.match(value):
        raise ValueError(
            f"{field_label} should only contain letters, spaces, "
            f"hyphens or apostrophes "
            f"no numbers or other symbols.")
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
            "like name123@example.com ,letters and numbers are both "
            "fine).")
    return value


def validate_phone(raw, allow_blank=True):
    value = raw.strip()
    if not value:
        raise ValueError("Phone number can't be blank.")
    if not _PHONE_RE.match(value):
        raise ValueError(
            "Phone number should contain digits only")
    return value
