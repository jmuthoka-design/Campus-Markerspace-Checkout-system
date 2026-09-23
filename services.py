"""
services.py
-----------
This is the "middle layer" that connects the menu (main.py) to the
database (database.py), using the classes from models.py along the
way.

Why have this layer at all? Two reasons:
1. main.py stays about *menus and printing*, not SQL or business rules.
2. All the "is this allowed?" rules (can't borrow something that's
   already out, can't delete a member who still has a loan, names and
   emails have to look like real names and emails...) live in ONE
   place, so they can't accidentally be applied differently in two
   different menu options.

Every public method here either:
  - returns a model object / list of model objects on success, or
  - raises a ValueError with a message that's safe to show the user
    directly (main.py just does print(f"Error: {e}")).

Note that the validators (validate_person_name, validate_email, etc.)
get called here TOO, even though main.py already calls them while
prompting. That's not duplication for no reason -- main.py's checks
give the user a friendly "try again" loop, but services.py's checks
are the ones that actually protect the database. Anything that ever
calls these methods without going through main.py's prompts (a test,
a future web version, anything) still can't sneak bad data in.
"""

from datetime import date, timedelta

from database import Database
from models import Member, Equipment, Loan
from validators import (
    validate_person_name,
    validate_email,
    validate_phone,
    validate_equipment_text,
)


class MakerSpaceService:

    def __init__(self, db_name="makerspace.db"):
        self.db = Database(db_name)

    # ---- small private helpers: turn a DB row into a model object --

    def _row_to_member(self, row):
        return Member(row["id"], row["name"], row["email"],
                       row["phone"], row["join_date"])

    def _row_to_equipment(self, row):
        return Equipment(row["id"], row["name"], row["category"],
                          row["status"])

    def _row_to_loan(self, row):
        return Loan(row["id"], row["member_id"], row["equipment_id"],
                     row["checkout_date"], row["due_date"],
                     row["return_date"], row["status"])

    # ================= MEMBERS =================

    def register_member(self, name, email, phone):
        name = validate_person_name(name, field_label="Name")
        email = validate_email(email)
        phone = validate_phone(phone, allow_blank=True)

        existing = self.db.fetch_one(
            "SELECT id FROM members WHERE email = ?", (email,))
        if existing:
            raise ValueError(f"A member with email '{email}' already exists.")

        join_date = date.today().isoformat()
        cursor = self.db.execute(
            "INSERT INTO members (name, email, phone, join_date) "
            "VALUES (?, ?, ?, ?)",
            (name, email, phone, join_date))
        return self.get_member(cursor.lastrowid)

    def get_member(self, member_id):
        row = self.db.fetch_one(
            "SELECT * FROM members WHERE id = ?", (member_id,))
        return self._row_to_member(row) if row else None

    def list_members(self):
        rows = self.db.fetch_all("SELECT * FROM members ORDER BY name")
        return [self._row_to_member(r) for r in rows]

    def update_member(self, member_id, name=None, email=None, phone=None):
        member = self.get_member(member_id)
        if not member:
            raise ValueError(f"No member with id {member_id}.")

        new_name = (validate_person_name(name, field_label="Name")
                    if name else member.name)
        new_email = validate_email(email) if email else member.email
        new_phone = (validate_phone(phone, allow_blank=True)
                     if phone else member.phone)

        self.db.execute(
            "UPDATE members SET name = ?, email = ?, phone = ? WHERE id = ?",
            (new_name, new_email, new_phone, member_id))
        return self.get_member(member_id)

    def delete_member(self, member_id):
        member = self.get_member(member_id)
        if not member:
            raise ValueError(f"No member with id {member_id}.")

        # Block on ANY loan (not just active ones). Even a returned loan
        # is a row in the loans table pointing at this member_id -- SQLite
        # would refuse the delete anyway because of the FOREIGN KEY, so we
        # check first and give a friendly message instead of a crash.
        any_loan = self.db.fetch_one(
            "SELECT id FROM loans WHERE member_id = ?", (member_id,))
        if any_loan:
            raise ValueError(
                "Can't delete this member -- they have loan history on "
                "record (deleting them would break those loan records).")

        self.db.execute("DELETE FROM members WHERE id = ?", (member_id,))

    def search_members(self, keyword):
        keyword = f"%{keyword.strip()}%"
        rows = self.db.fetch_all(
            "SELECT * FROM members WHERE name LIKE ? OR id LIKE ?",
            (keyword, keyword))
        return [self._row_to_member(r) for r in rows]

    # ================= EQUIPMENT =================

    def register_equipment(self, name, category):
        name = validate_equipment_text(name, field_label="Equipment name")
        category = validate_equipment_text(category, field_label="Category")

        cursor = self.db.execute(
            "INSERT INTO equipment (name, category, status) "
            "VALUES (?, ?, 'available')",
            (name, category))
        return self.get_equipment(cursor.lastrowid)

    def get_equipment(self, equipment_id):
        row = self.db.fetch_one(
            "SELECT * FROM equipment WHERE id = ?", (equipment_id,))
        return self._row_to_equipment(row) if row else None

    def list_equipment(self):
        rows = self.db.fetch_all("SELECT * FROM equipment ORDER BY name")
        return [self._row_to_equipment(r) for r in rows]

    def update_equipment(self, equipment_id, name=None, category=None):
        item = self.get_equipment(equipment_id)
        if not item:
            raise ValueError(f"No equipment with id {equipment_id}.")

        new_name = (validate_equipment_text(name, field_label="Equipment name")
                    if name else item.name)
        new_category = (validate_equipment_text(category, field_label="Category")
                         if category else item.category)

        self.db.execute(
            "UPDATE equipment SET name = ?, category = ? WHERE id = ?",
            (new_name, new_category, equipment_id))
        return self.get_equipment(equipment_id)

    def delete_equipment(self, equipment_id):
        item = self.get_equipment(equipment_id)
        if not item:
            raise ValueError(f"No equipment with id {equipment_id}.")
        if item.status == "borrowed":
            raise ValueError(
                "Can't delete this item -- it's currently checked out.")

        any_loan = self.db.fetch_one(
            "SELECT id FROM loans WHERE equipment_id = ?", (equipment_id,))
        if any_loan:
            raise ValueError(
                "Can't delete this item -- it has loan history on record "
                "(deleting it would break those loan records).")

        self.db.execute("DELETE FROM equipment WHERE id = ?", (equipment_id,))

    def search_equipment(self, keyword):
        keyword = f"%{keyword.strip()}%"
        rows = self.db.fetch_all(
            "SELECT * FROM equipment "
            "WHERE name LIKE ? OR category LIKE ? OR id LIKE ?",
            (keyword, keyword, keyword))
        return [self._row_to_equipment(r) for r in rows]

    # ================= LOANS (borrow / return) =================

    def borrow_equipment(self, member_id, equipment_id, loan_days=7):
        member = self.get_member(member_id)
        if not member:
            raise ValueError(f"No member with id {member_id}. "
                              "Register them first.")

        item = self.get_equipment(equipment_id)
        if not item:
            raise ValueError(f"No equipment with id {equipment_id}.")
        if not item.is_available():
            raise ValueError(f"'{item.name}' is already borrowed.")

        checkout_date = date.today().isoformat()
        due_date = (date.today() + timedelta(days=loan_days)).isoformat()

        cursor = self.db.execute(
            "INSERT INTO loans (member_id, equipment_id, checkout_date, "
            "due_date, status) VALUES (?, ?, ?, ?, 'active')",
            (member_id, equipment_id, checkout_date, due_date))

        self.db.execute(
            "UPDATE equipment SET status = 'borrowed' WHERE id = ?",
            (equipment_id,))

        return self.get_loan(cursor.lastrowid)

    def return_equipment(self, loan_id):
        loan = self.get_loan(loan_id)
        if not loan:
            raise ValueError(f"No loan with id {loan_id}.")
        if loan.status != "active":
            raise ValueError("That loan is already closed.")

        return_date = date.today().isoformat()
        self.db.execute(
            "UPDATE loans SET return_date = ?, status = 'returned' "
            "WHERE id = ?",
            (return_date, loan_id))
        self.db.execute(
            "UPDATE equipment SET status = 'available' WHERE id = ?",
            (loan.equipment_id,))

        return self.get_loan(loan_id)

    def get_loan(self, loan_id):
        row = self.db.fetch_one("SELECT * FROM loans WHERE id = ?",
                                 (loan_id,))
        return self._row_to_loan(row) if row else None

    # ================= REPORTS =================
    # Each report returns a list of sqlite3.Row objects that already
    # join member/equipment names in, so main.py can just print them
    # without extra lookups.

    def report_currently_borrowed(self):
        return self.db.fetch_all("""
            SELECT loans.id AS loan_id, members.name AS member_name,
                   equipment.name AS equipment_name, loans.checkout_date,
                   loans.due_date
            FROM loans
            JOIN members ON members.id = loans.member_id
            JOIN equipment ON equipment.id = loans.equipment_id
            WHERE loans.status = 'active'
            ORDER BY loans.due_date
        """)

    def report_overdue_loans(self):
        today = date.today().isoformat()
        return self.db.fetch_all("""
            SELECT loans.id AS loan_id, members.name AS member_name,
                   equipment.name AS equipment_name, loans.due_date
            FROM loans
            JOIN members ON members.id = loans.member_id
            JOIN equipment ON equipment.id = loans.equipment_id
            WHERE loans.status = 'active' AND loans.due_date < ?
            ORDER BY loans.due_date
        """, (today,))

    def report_member_history(self, member_id):
        return self.db.fetch_all("""
            SELECT loans.id AS loan_id, equipment.name AS equipment_name,
                   loans.checkout_date, loans.due_date, loans.return_date,
                   loans.status
            FROM loans
            JOIN equipment ON equipment.id = loans.equipment_id
            WHERE loans.member_id = ?
            ORDER BY loans.checkout_date DESC
        """, (member_id,))

