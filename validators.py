"""
validators.py
--------------
Small, single-purpose functions that check whether a piece of user
input is valid, and explain *why* when it isn't.

Keeping these in one file means main.py (the prompts) and services.py
(the business rules) always agree on what counts as "a valid name" or
"a valid phone number" -- there's exactly one definition of each, not
two copies that could quietly drift apart over time.

Every function here either:
  - returns the cleaned-up value (whitespace trimmed), or
  - raises ValueError with a message that's safe to print directly to
    the user.

main.py calls these while it's still asking the question (so it can
re-prompt immediately). services.py calls them again before touching
the database (so nothing bad can get in even if some other caller
skips the prompt step). That's "defense in depth" -- two checkpoints
instead of one.
"""

import re

# A person's name: must start with a letter, and after that can only
# contain letters, spaces, hyphens, apostrophes and periods. This covers
# real names like "Jean-Paul", "O'Brien", "Dr. Amara Diallo" -- but
# rejects digits and other symbols, since a person's name shouldn't
# contain either.
_PERSON_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z'\-. ]{1,49}$")

# An equipment name or category: CAN include digits, because real
# equipment names/categories do (e.g. "Canon EOS M50", "3D Printing").
# Letters, digits, spaces, and a few common punctuation marks are
# allowed; must contain at least one letter so something like "12345"
# on its own is still rejected.
_EQUIPMENT_TEXT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9'\-./() ]{1,59}$")

# Email: allows letters AND digits mixed together on both sides of the
# @ (e.g. "jemima98@example.com" is valid) -- this is a simple, readable
# check, not a full RFC 5322 validator, but it catches the obvious
# mistakes (no @, no domain, spaces inside the address).
_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

# Phone number: digits only. No +, -, spaces, or parentheses -- just
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
            "Phone number should contain digits only (no spaces, "
            "dashes, or parentheses) -- e.g. 57123456, 7 to 15 digits "
            "long.")
    return value
