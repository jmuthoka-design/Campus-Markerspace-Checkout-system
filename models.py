"""
models.py
---------


These three classes (Member, Equipment, Loan) describe the *real-world
things* the makerspace deals with, and the behaviour that belongs to
each one. database.py knows how to save/load rows; services.py is the
one that hands rows from the database to these classes and back again.
"""

from datetime import date


class Member:
    """A person registered at the makerspace."""

    def __init__(self, id, name, email, phone, join_date):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.join_date = join_date

    def __str__(self):
        return f"[{self.id}] {self.name} | {self.email} | {self.phone}"


class Equipment:
    """A single piece of makerspace gear (a 3D-printer nozzle kit,
    a soldering iron, a camera, a laptop...).
    """

    def __init__(self, id, name, category, status="available"):
        self.id = id
        self.name = name
        self.category = category
        self.status = status  # 'available' or 'borrowed'

    def is_available(self):
        return self.status == "available"

    def mark_borrowed(self):
        self.status = "borrowed"

    def mark_available(self):
        self.status = "available"

    def __str__(self):
        return f"[{self.id}] {self.name} ({self.category}) - {self.status}"


class Loan:
    """One borrow record: this member has this piece of equipment,
    from checkout_date, due back by due_date.
    """

    def __init__(self, id, member_id, equipment_id, checkout_date,
                 due_date, return_date=None, status="active"):
        self.id = id
        self.member_id = member_id
        self.equipment_id = equipment_id
        self.checkout_date = checkout_date
        self.due_date = due_date
        self.return_date = return_date
        self.status = status  # 'active' or 'returned'

    def is_overdue(self):
        """A loan is overdue if it's still active and today is past
        the due date. A returned loan is never overdue -- it's done.
        """
        if self.status != "active":
            return False
        return date.today().isoformat() > self.due_date

    def close(self, return_date):
        """Mark this loan as finished. services.py calls this at the
        same time it frees up the equipment.
        """
        self.return_date = return_date
        self.status = "returned"

    def __str__(self):
        flag = "  ** OVERDUE **" if self.is_overdue() else ""
        return (f"Loan #{self.id} | member {self.member_id} -> "
                f"equipment {self.equipment_id} | due {self.due_date} "
                f"| {self.status}{flag}")
