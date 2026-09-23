# Campus MakerSpace Checkout System

A command-line application for managing members, equipment, and loans
at a student makerspace, built with Python and SQLite.

## What it does

Operators (staff at the makerspace desk) can, through a text menu:

- Register, list, update, delete, and search **members**
- Register, list, update, delete, and search **equipment**
- **Borrow** equipment (checked out to a member, with validation)
- **Return** equipment
- Run three reports:
  - Currently borrowed equipment
  - Overdue loans
  - A single member's full loan history

All data is stored in a SQLite database file (`makerspace.db`), which
is created automatically the first time the program runs.

Every name, email, and phone number entered is checked for a valid
format before it's accepted -- see **Input validation** below.

## How to run it

Requirements: Python 3.9+ (no external packages -- `sqlite3` and `re`
are both part of the Python standard library).

```bash
git clone <this-repo-url>
cd <repo-folder>
python3 main.py
```

The first run creates `makerspace.db` in the same folder and sets up
the three tables automatically. The database file is not included in
this repo, so you'll be starting with an empty makerspace -- use the
menu to register a few members and equipment items before trying
borrow/return.

## Project structure

```
main.py         # Menu loop -- reads user input, calls services.py, prints results
services.py     # Business rules -- borrow/return validation, reports, etc.
models.py       # Member, Equipment, Loan classes (what these things ARE)
database.py     # SQLite connection, schema, and generic query helpers
validators.py   # Format rules for names, emails, and phone numbers
README.md       # You are here
```

See `CODE_GUIDE.md` in this repo for a section-by-section walkthrough
of what each file does and why it's organised this way.

## Class design (OOP)

- **Member** -- id, name, email, phone, join_date
- **Equipment** -- id, name, category, status (`available` / `borrowed`);
  has `is_available()`, `mark_borrowed()`, `mark_available()`
- **Loan** -- id, member_id, equipment_id, checkout_date, due_date,
  return_date, status (`active` / `returned`); has `is_overdue()`
  and `close()`

`services.py` is the layer that makes these objects collaborate: a
borrow, for example, creates a `Loan` **and** flips the matching
`Equipment` to `borrowed`, in one method (`borrow_equipment`).

## Database design (SQLite)

Three tables, normalised so a loan doesn't repeat member/equipment
details -- it just stores the two IDs and looks the rest up via SQL
joins:

```
members(id, name, email, phone, join_date)
equipment(id, name, category, status)
loans(id, member_id -> members.id, equipment_id -> equipment.id,
      checkout_date, due_date, return_date, status)
```

## Input validation

`validators.py` defines what counts as valid input, and both the menu
prompts (`main.py`) and the business-rule layer (`services.py`) check
against it -- the prompts re-ask immediately so a mistake never has
to travel through the whole form before it's caught:

| Field | Rule |
|---|---|
| Member name | Letters, spaces, hyphens, and apostrophes only (e.g. `Jean-Paul`, `O'Brien`) -- no digits or other symbols |
| Equipment name / category | Letters, digits, spaces, and basic punctuation (e.g. `Canon EOS M50`, `3D Printing`) -- must contain at least one letter |
| Email | Standard `name@domain.tld` shape -- letters and digits both allowed |
| Phone | Digits only, 7-15 of them -- no spaces, dashes, or parentheses; optional at registration |

## Validation and error handling

Every action that could go wrong (unknown member/equipment ID, already
borrowed item, blank or malformed field, deleting a member/equipment
that still has loan history, non-numeric ID input) raises a clear
error message instead of crashing. `main.py` catches these and prints
them, then returns straight to the menu -- no "press Enter to
continue" needed.

## Use of Generative AI

<!-- Fill this in honestly before submitting -- see note below. -->
I used [tool name, e.g. Claude] while building this project for:
- [ ] Discussing the overall class/table design before I started coding
- [ ] Explaining SQLite concepts (foreign keys, parameterised queries)
- [ ] Debugging a specific error I ran into: ______________________
- [ ] Reviewing/organising code structure and comments

I wrote/adapted the final code myself and can explain every file in
the live demo.
