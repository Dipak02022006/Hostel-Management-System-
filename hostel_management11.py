"""
HOSTEL MANAGEMENT SYSTEM USING FILE HANDLING
--------------------------------------------
A menu-driven console project that stores data permanently in JSON files.

Files used (created automatically in the same folder as this program):
    students.json - all student admission records
    rooms.json    - the 20 rooms (101-120) and their occupancy status
"""

import json
import os

# ------------------------------------------------------------------
# CONSTANTS
# ------------------------------------------------------------------
# Build file paths next to this script, so it works from any folder.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STUDENTS_FILE = os.path.join(BASE_DIR, "students.json")
ROOMS_FILE = os.path.join(BASE_DIR, "rooms.json")

FIRST_ROOM = 101
LAST_ROOM = 120
LINE = "=" * 70
THIN_LINE = "-" * 70


# ------------------------------------------------------------------
# FILE HANDLING FUNCTIONS
# ------------------------------------------------------------------
def read_json_file(filename, default):
    """Read a JSON file safely. Returns `default` if the file is
    missing, empty, or contains invalid data."""
    try:
        with open(filename, "r") as file:
            content = file.read().strip()
            if content == "":                 # empty file
                return default
            data = json.loads(content)
            # Make sure we got the type of data we expect (list/dict)
            if isinstance(data, type(default)):
                return data
            return default
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        print("Warning: '{}' was corrupted. Starting with empty data."
              .format(os.path.basename(filename)))
        return default
    except OSError as error:
        print("File error:", error)
        return default


def write_json_file(filename, data):
    """Write data to a JSON file. Returns True if saved successfully."""
    try:
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        return True
    except OSError as error:
        print("Error: could not save data ->", error)
        return False


def load_students():
    """Return the list of student records from students.json."""
    return read_json_file(STUDENTS_FILE, [])


def save_students(students):
    return write_json_file(STUDENTS_FILE, students)


def load_rooms():
    """Return the list of rooms from rooms.json."""
    return read_json_file(ROOMS_FILE, [])


def save_rooms(rooms):
    return write_json_file(ROOMS_FILE, rooms)


def create_default_rooms():
    """Create rooms 101-120, all vacant."""
    return [{"room_no": number, "status": "Vacant", "student_id": ""}
            for number in range(FIRST_ROOM, LAST_ROOM + 1)]


def initialize_files():
    """Create the data files if missing and make sure that the room
    status always matches the student records (keeps data consistent)."""
    students = load_students()
    rooms = load_rooms()

    # If rooms file is missing/invalid/incomplete, rebuild default rooms
    valid_rooms = (
        len(rooms) == (LAST_ROOM - FIRST_ROOM + 1)
        and all(isinstance(r, dict) and "room_no" in r for r in rooms)
    )
    if not valid_rooms:
        rooms = create_default_rooms()

    # Reset every room to vacant, then occupy rooms using student records
    for room in rooms:
        room["status"] = "Vacant"
        room["student_id"] = ""
    for student in students:
        for room in rooms:
            if room["room_no"] == student.get("room_no"):
                room["status"] = "Occupied"
                room["student_id"] = student.get("student_id", "")

    save_students(students)
    save_rooms(rooms)


# ------------------------------------------------------------------
# INPUT VALIDATION HELPERS
# ------------------------------------------------------------------
def get_text(prompt):
    """Keep asking until the user types something non-empty."""
    while True:
        value = input(prompt).strip()
        if value != "":
            return value
        print("  Error: this field cannot be empty.")


def get_name(prompt):
    """Name must contain only letters and spaces."""
    while True:
        value = get_text(prompt)
        if value.replace(" ", "").isalpha():
            return value.title()
        print("  Error: name should contain only letters and spaces.")


def get_age(prompt):
    """Age must be a whole number between 15 and 60."""
    while True:
        value = input(prompt).strip()
        try:
            age = int(value)
            if 15 <= age <= 60:
                return age
            print("  Error: age must be between 15 and 60.")
        except ValueError:
            print("  Error: please enter a valid number.")


def get_gender(prompt):
    while True:
        value = input(prompt).strip().upper()
        if value in ("M", "MALE"):
            return "Male"
        if value in ("F", "FEMALE"):
            return "Female"
        if value in ("O", "OTHER"):
            return "Other"
        print("  Error: enter M, F or O.")


def get_phone(prompt):
    """Phone number must be exactly 10 digits."""
    while True:
        value = input(prompt).strip()
        if value.isdigit() and len(value) == 10:
            return value
        print("  Error: phone number must be exactly 10 digits.")


def get_student_id(prompt, students):
    """Student ID must be non-empty, without spaces and unique."""
    while True:
        value = get_text(prompt).upper()
        if " " in value:
            print("  Error: student ID cannot contain spaces.")
        elif find_student_by_id(students, value) is not None:
            print("  Error: student ID '{}' already exists.".format(value))
        else:
            return value


# ------------------------------------------------------------------
# DISPLAY HELPERS
# ------------------------------------------------------------------
def print_heading(title):
    print("\n" + LINE)
    print(title.center(70))
    print(LINE)


def find_student_by_id(students, student_id):
    """Return the student record with this ID, or None."""
    for student in students:
        if student["student_id"].upper() == student_id.upper():
            return student
    return None


def get_vacant_rooms(rooms):
    return [room for room in rooms if room["status"] == "Vacant"]


def print_student_details(student):
    print(THIN_LINE)
    print("  Student ID   :", student["student_id"])
    print("  Name         :", student["name"])
    print("  Age          :", student["age"])
    print("  Gender       :", student["gender"])
    print("  Phone        :", student["phone"])
    print("  Course       :", student["course"])
    print("  College      :", student["college"])
    print("  Address      :", student["address"])
    print("  Room Number  :", student["room_no"])
    print(THIN_LINE)


def print_room_list(vacant_rooms):
    """Show vacant room numbers, 10 per line."""
    numbers = [str(room["room_no"]) for room in vacant_rooms]
    for i in range(0, len(numbers), 10):
        print("  " + "  ".join(numbers[i:i + 10]))


# ------------------------------------------------------------------
# MENU OPTION FUNCTIONS
# ------------------------------------------------------------------
def new_admission():
    """Option 1: admit a new student and allocate a room."""
    print_heading("NEW STUDENT ADMISSION")
    students = load_students()
    rooms = load_rooms()

    vacant = get_vacant_rooms(rooms)
    if not vacant:
        print("Sorry! All rooms are occupied. Admission is not possible.")
        return

    # --- collect student details (each input is validated) ---
    student_id = get_student_id("Enter Student ID      : ", students)
    name = get_name("Enter Student Name    : ")
    age = get_age("Enter Age             : ")
    gender = get_gender("Enter Gender (M/F/O) : ")
    phone = get_phone("Enter Phone Number    : ")
    course = get_text("Enter Course          : ")
    college = get_text("Enter College Name    : ")
    address = get_text("Enter Address         : ")

    # --- show vacant rooms and let the user choose one ---
    print("\nAvailable Vacant Rooms ({}):".format(len(vacant)))
    print_room_list(vacant)

    vacant_numbers = [room["room_no"] for room in vacant]
    while True:
        choice = input("\nSelect a room number: ").strip()
        try:
            room_no = int(choice)
        except ValueError:
            print("  Error: please enter a valid room number.")
            continue
        if room_no in vacant_numbers:
            break
        print("  Error: room {} is occupied or does not exist.".format(room_no))

    # --- save the student and mark the room as occupied ---
    student = {
        "student_id": student_id,
        "name": name,
        "age": age,
        "gender": gender,
        "phone": phone,
        "course": course,
        "college": college,
        "address": address,
        "room_no": room_no,
    }
    students.append(student)

    for room in rooms:
        if room["room_no"] == room_no:
            room["status"] = "Occupied"
            room["student_id"] = student_id

    if save_students(students) and save_rooms(rooms):
        print("\n*** ADMISSION SUCCESSFUL! ***")
        print("{} (ID: {}) has been allotted Room {}."
              .format(name, student_id, room_no))
    else:
        print("Admission failed because data could not be saved.")


def view_vacant_rooms():
    """Option 2: show vacant rooms with totals."""
    print_heading("VACANT ROOMS")
    rooms = load_rooms()
    vacant = get_vacant_rooms(rooms)
    occupied_count = len(rooms) - len(vacant)

    if not vacant:
        print("No rooms are available. All rooms are occupied.")
    else:
        print("Vacant Room Numbers:\n")
        print_room_list(vacant)

    print("\n" + THIN_LINE)
    print("Total Vacant Rooms   :", len(vacant))
    print("Total Occupied Rooms :", occupied_count)
    print("Total Rooms          :", len(rooms))


def view_all_students():
    """Option 3: display all students in a table."""
    print_heading("ALL STUDENT RECORDS")
    students = load_students()

    if not students:
        print("No student records found.")
        return

    # Table header
    print("{:<10} {:<20} {:<14} {:<12} {:<6}".format(
        "ID", "Name", "Course", "Phone", "Room"))
    print(THIN_LINE)
    for s in students:
        print("{:<10} {:<20} {:<14} {:<12} {:<6}".format(
            s["student_id"], s["name"][:19], s["course"][:13],
            s["phone"], s["room_no"]))
    print(THIN_LINE)
    print("Total Students:", len(students))


def search_student():
    """Option 4: search by student ID or name."""
    print_heading("SEARCH STUDENT RECORD")
    students = load_students()

    if not students:
        print("No student records found.")
        return

    print("1. Search by Student ID")
    print("2. Search by Student Name")
    choice = input("Enter choice (1/2): ").strip()

    if choice == "1":
        key = get_text("Enter Student ID: ").upper()
        matches = [s for s in students if s["student_id"].upper() == key]
    elif choice == "2":
        key = get_text("Enter Student Name (full or part): ").lower()
        matches = [s for s in students if key in s["name"].lower()]
    else:
        print("Invalid choice. Please enter 1 or 2.")
        return

    if not matches:
        print("\nStudent record not found.")
        return

    print("\n{} record(s) found:".format(len(matches)))
    for student in matches:
        print_student_details(student)


def delete_student():
    """Option 5: delete a student and vacate their room."""
    print_heading("DELETE STUDENT RECORD / VACATE ROOM")
    students = load_students()
    rooms = load_rooms()

    if not students:
        print("No student records found.")
        return

    student_id = get_text("Enter Student ID to delete: ")
    student = find_student_by_id(students, student_id)

    if student is None:
        print("\nStudent record not found.")
        return

    print("\nStudent details:")
    print_student_details(student)

    confirm = input("Are you sure you want to delete this record? (yes/no): ")
    if confirm.strip().lower() not in ("yes", "y"):
        print("Deletion cancelled. No changes were made.")
        return

    # Remove the student and mark their room vacant
    room_no = student["room_no"]
    students.remove(student)
    for room in rooms:
        if room["room_no"] == room_no:
            room["status"] = "Vacant"
            room["student_id"] = ""

    if save_students(students) and save_rooms(rooms):
        print("\n*** RECORD DELETED SUCCESSFULLY! ***")
        print("Room {} is now vacant.".format(room_no))
    else:
        print("Deletion failed because data could not be saved.")


# ------------------------------------------------------------------
# MAIN PROGRAM
# ------------------------------------------------------------------
def show_menu():
    print_heading("HOSTEL MANAGEMENT SYSTEM")
    print("1. New Student Admission")
    print("2. View Available Vacant Rooms")
    print("3. View All Student Records")
    print("4. Search Student Record")
    print("5. Delete Student Record / Vacate Room")
    print("6. Exit")
    print(THIN_LINE)


def main():
    initialize_files()          # create/repair data files at start-up

    while True:
        show_menu()
        choice = input("Enter your choice: ").strip()

        try:
            if choice == "1":
                new_admission()
            elif choice == "2":
                view_vacant_rooms()
            elif choice == "3":
                view_all_students()
            elif choice == "4":
                search_student()
            elif choice == "5":
                delete_student()
            elif choice == "6":
                print("\nAll changes are saved. Thank you for using the")
                print("Hostel Management System. Goodbye!")
                break
            else:
                print("Invalid choice! Please enter a number from 1 to 6.")
        except (KeyError, TypeError) as error:
            # Protects against a hand-edited / damaged JSON file
            print("Data error:", error, "- please check the JSON files.")
        except (KeyboardInterrupt, EOFError):
            print("\nProgram interrupted. All saved data is safe. Goodbye!")
            break

        input("\nPress Enter to return to the main menu...")


if __name__ == "__main__":
    main()
