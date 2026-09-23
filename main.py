"""
main.py
-------
Entry point for the Campus MakerSpace Checkout System.
"""

from services import MakerSpaceService
from validators import (
    validate_person_name,
    validate_email,
    validate_phone,
    validate_equipment_text,
)

def prompt_text(label, allow_blank=False):
    """Ask for plain text with no format rules -- just "not blank"."""
    while True:
        value = input(f"{label}: ").strip()
        if value or allow_blank:
            return value
        print("  -> This can't be blank. Please try again.")


def prompt_valid(label, validator, skip_if_blank=False, **validator_kwargs):
    """Keep asking until `validator` accepts what was typed.
    """
    while True:
        raw = input(f"{label}: ")
        if skip_if_blank and not raw.strip():
            return ""
        try:
            return validator(raw, **validator_kwargs)
        except ValueError as e:
            print(f"  -> {e} Please try again.")


def prompt_int(label):
    while True:
        raw = input(f"{label}: ").strip()
        try:
            return int(raw)
        except ValueError:
            print(f"  -> '{raw}' isn't a whole number. Please try again.")


# ---------------------------------------------------------------
# Member menu options
# ---------------------------------------------------------------

def do_register_member(service):
    print("\n-- Register New Member --")
    name = prompt_valid("Full name", validate_person_name,
                         field_label="Name")
    email = prompt_valid("Email", validate_email)
    phone = prompt_valid("Phone number",
                          validate_phone, allow_blank=False)
    member = service.register_member(name, email, phone)
    print(f"Registered: {member}")


def do_list_members(service):
    print("\n-- All Members --")
    members = service.list_members()
    if not members:
        print("No members registered yet.")
    for m in members:
        print(m)


def do_update_member(service):
    print("\n-- Update Member --")
    member_id = prompt_int("Member ID to update")
    print("Leave a field blank to keep its current value.")
    name = prompt_valid("New name", validate_person_name,
                         skip_if_blank=True, field_label="Name")
    email = prompt_valid("New email", validate_email, skip_if_blank=True)
    phone = prompt_valid("New phone (e.g. 57123456 or +230-57-123-456)",
                          validate_phone, skip_if_blank=True)
    member = service.update_member(member_id, name or None,
                                    email or None, phone or None)
    print(f"Updated: {member}")


def do_delete_member(service):
    print("\n-- Delete Member --")
    member_id = prompt_int("Member ID to delete")
    service.delete_member(member_id)
    print("Member deleted.")


def do_search_members(service):
    print("\n-- Search Members --")
    keyword = prompt_text("Name or ID to search for")
    results = service.search_members(keyword)
    if not results:
        print("No matches found.")
    for m in results:
        print(m)


# ---------------------------------------------------------------
# Equipment menu options
# ---------------------------------------------------------------

def do_register_equipment(service):
    print("\n-- Register New Equipment --")
    name = prompt_valid("Equipment name", validate_equipment_text,
                         field_label="Equipment name")
    category = prompt_valid("Category (e.g. 3D Printing, Electronics)",
                             validate_equipment_text, field_label="Category")
    item = service.register_equipment(name, category)
    print(f"Registered: {item}")


def do_list_equipment(service):
    print("\n-- All Equipment --")
    items = service.list_equipment()
    if not items:
        print("No equipment registered yet.")
    for e in items:
        print(e)


def do_update_equipment(service):
    print("\n-- Update Equipment --")
    equipment_id = prompt_int("Equipment ID to update")
    print("Leave a field blank to keep its current value.")
    name = prompt_valid("New name", validate_equipment_text,
                         skip_if_blank=True, field_label="Equipment name")
    category = prompt_valid("New category", validate_equipment_text,
                             skip_if_blank=True, field_label="Category")
    item = service.update_equipment(equipment_id, name or None,
                                     category or None)
    print(f"Updated: {item}")


def do_delete_equipment(service):
    print("\n-- Delete Equipment --")
    equipment_id = prompt_int("Equipment ID to delete")
    service.delete_equipment(equipment_id)
    print("Equipment deleted.")


def do_search_equipment(service):
    print("\n-- Search Equipment --")
    keyword = prompt_text("Name, category, or ID to search for")
    results = service.search_equipment(keyword)
    if not results:
        print("No matches found.")
    for e in results:
        print(e)


# ---------------------------------------------------------------
# Loan menu options (borrow / return)
# ---------------------------------------------------------------

def do_borrow(service):
    print("\n-- Borrow Equipment --")
    member_id = prompt_int("Member ID")
    equipment_id = prompt_int("Equipment ID")
    loan = service.borrow_equipment(member_id, equipment_id)
    print(f"Borrowed! {loan}")


def do_return(service):
    print("\n-- Return Equipment --")
    loan_id = prompt_int("Loan ID")
    loan = service.return_equipment(loan_id)
    print(f"Returned. {loan}")


# ---------------------------------------------------------------
# Reports
# ---------------------------------------------------------------

def do_report_borrowed(service):
    print("\n-- Report: Currently Borrowed Equipment --")
    rows = service.report_currently_borrowed()
    if not rows:
        print("Nothing is currently borrowed.")
    for r in rows:
        print(f"Loan #{r['loan_id']}: {r['equipment_name']} -> "
              f"{r['member_name']} (out since {r['checkout_date']}, "
              f"due {r['due_date']})")


def do_report_overdue(service):
    print("\n-- Report: Overdue Loans --")
    rows = service.report_overdue_loans()
    if not rows:
        print("No overdue loans. Nice.")
    for r in rows:
        print(f"Loan #{r['loan_id']}: {r['equipment_name']} -> "
              f"{r['member_name']} (was due {r['due_date']})")


def do_report_member_history(service):
    print("\n-- Report: Member Loan History --")
    member_id = prompt_int("Member ID")
    rows = service.report_member_history(member_id)
    if not rows:
        print("This member has no loan history.")
    for r in rows:
        returned = r["return_date"] or "not yet returned"
        print(f"Loan #{r['loan_id']}: {r['equipment_name']} | "
              f"out {r['checkout_date']} | due {r['due_date']} | "
              f"returned {returned} | status: {r['status']}")


# ---------------------------------------------------------------
# Menu
# ---------------------------------------------------------------

MENU = """
========== Campus MakerSpace Checkout System ==========
 Members
  1. Register new member
  2. List all members
  3. Update member
  4. Delete member
  5. Search members

 Equipment
  6. Register new equipment
  7. List all equipment
  8. Update equipment
  9. Delete equipment
  10. Search equipment

 Loans
  11. Borrow equipment
  12. Return equipment

 Reports
  13. Currently borrowed equipment
  14. Overdue loans
  15. Member loan history

  0. Exit
=========================================================
"""

ACTIONS = {
    "1": do_register_member,
    "2": do_list_members,
    "3": do_update_member,
    "4": do_delete_member,
    "5": do_search_members,
    "6": do_register_equipment,
    "7": do_list_equipment,
    "8": do_update_equipment,
    "9": do_delete_equipment,
    "10": do_search_equipment,
    "11": do_borrow,
    "12": do_return,
    "13": do_report_borrowed,
    "14": do_report_overdue,
    "15": do_report_member_history,
}


def main():
    service = MakerSpaceService()
    print("Connected to makerspace.db")

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()

        if choice == "0":
            print("Goodbye!")
            break

        action = ACTIONS.get(choice)
        if action is None:
            print("That's not a valid option, please pick a number "
                  "from the menu.")
            continue
            
            try:
            action(service)
        except ValueError as e:
            print(f"\nCouldn't do that: {e}")
        except Exception as e:
            print(f"\nSomething unexpected went wrong: {e}")

       
        print()


if __name__ == "__main__":
    main()
