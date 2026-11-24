import json
import csv
import os
from datetime import datetime, date, timedelta
from collections import Counter

# ==========================================
# TRAVEL ITINERARY ORGANIZER
# ==========================================

DATA_FILE = "trips.json"
CSV_FILE = "trips.csv"

# ==========================================
# FILE HANDLING
# ==========================================

def load_trips():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        print("Invalid data format. Starting fresh.")
        return []

    except (json.JSONDecodeError, OSError):
        print("Warning: Unable to read saved data.")
        return []


def save_trips(trips):
    try:
        with open(DATA_FILE, "w") as file:
            json.dump(trips, file, indent=4)

        fields = [
            "id", "destination", "start_date",
            "end_date", "category", "cost", "notes"
        ]

        with open(CSV_FILE, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()

            for trip in trips:
                writer.writerow({
                    field: trip.get(field, "")
                    for field in fields
                })

    except OSError as error:
        print("Storage error:", error)


# ==========================================
# INPUT VALIDATION
# ==========================================

def get_text(message):
    while True:
        value = input(message).strip()

        if value:
            return value

        print("Error: This field cannot be empty.")


def get_date(message):
    while True:
        value = input(message).strip()

        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value

        except ValueError:
            print("Enter date in YYYY-MM-DD format.")


def get_cost(message):
    while True:
        try:
            value = float(input(message))

            if value >= 0:
                return round(value, 2)

            print("Cost cannot be negative.")

        except ValueError:
            print("Please enter a valid number.")


def get_trip_id():
    while True:
        try:
            value = int(input("Enter Trip ID: "))

            if value > 0:
                return value

            print("ID must be positive.")

        except ValueError:
            print("Enter a valid whole number.")


def next_id(trips):
    return max(
        (trip["id"] for trip in trips),
        default=0
    ) + 1


# ==========================================
# ADD NEW TRIP
# ==========================================

def add_trip(trips):

    print("\n========== ADD NEW TRIP ==========")

    destination = get_text("Destination: ")

    start = get_date("Start date: ")

    while True:
        end = get_date("End date: ")

        if end >= start:
            break

        print("End date cannot be before start date.")

    print("\nCategories:")
    print("Holiday | Education | Family | Adventure | Other")

    category = get_text("Category: ").title()

    cost = get_cost("Estimated cost: ")

    notes = input("Travel notes: ").strip()

    trip = {
        "id": next_id(trips),
        "destination": destination,
        "start_date": start,
        "end_date": end,
        "category": category,
        "cost": cost,
        "notes": notes
    }

    trips.append(trip)

    save_trips(trips)

    print("\nTrip added successfully!")


# ==========================================
# VIEW ALL TRIPS
# ==========================================

def view_trips(trips):

    print("\n========== ALL TRIPS ==========")

    if not trips:
        print("No trips available.")
        return

    for trip in sorted(
        trips,
        key=lambda item: item["start_date"]
    ):

        print("\nTrip ID:", trip["id"])
        print("Destination:", trip["destination"])
        print("Start date:", trip["start_date"])
        print("End date:", trip["end_date"])
        print("Category:", trip["category"])
        print("Estimated cost: Rs.", trip["cost"])
        print("Notes:", trip["notes"])

        print("-" * 40)


# ==========================================
# SEARCH TRIPS
# ==========================================

def search_trip(trips):

    print("\n========== SMART TRIP SEARCH ==========")

    keyword = get_text(
        "Search destination/category/notes: "
    ).lower()

    results = []

    for trip in trips:

        details = (
            trip["destination"] + " " +
            trip["category"] + " " +
            trip["notes"]
        ).lower()

        if keyword in details:
            results.append(trip)

    if results:
        print("\nMatching trips:", len(results))

        for trip in results:
            print(
                trip["id"],
                "|",
                trip["destination"],
                "|",
                trip["start_date"],
                "| Rs.",
                trip["cost"]
            )

    else:
        print("No matching trips found.")


# ==========================================
# EDIT TRIP
# ==========================================

def edit_trip(trips):

    print("\n========== EDIT TRIP ==========")

    trip_id = get_trip_id()

    trip = next(
        (item for item in trips if item["id"] == trip_id),
        None
    )

    if trip is None:
        print("Trip not found.")
        return

    print("Press Enter to keep existing information.")

    value = input("New destination: ").strip()

    if value:
        trip["destination"] = value

    value = input("New start date: ").strip()

    if value:
        try:
            datetime.strptime(value, "%Y-%m-%d")
            trip["start_date"] = value
        except ValueError:
            print("Invalid date. Keeping old date.")

    value = input("New end date: ").strip()

    if value:
        try:
            datetime.strptime(value, "%Y-%m-%d")

            if value >= trip["start_date"]:
                trip["end_date"] = value
            else:
                print("Invalid date range.")

        except ValueError:
            print("Invalid date.")

    value = input("New category: ").strip()

    if value:
        trip["category"] = value.title()

    value = input("New estimated cost: ").strip()

    if value:
        try:
            amount = float(value)

            if amount >= 0:
                trip["cost"] = amount
            else:
                print("Cost cannot be negative.")

        except ValueError:
            print("Invalid cost.")

    value = input("New notes: ").strip()

    if value:
        trip["notes"] = value

    save_trips(trips)

    print("Trip updated successfully!")


# ==========================================
# DELETE TRIP
# ==========================================

def delete_trip(trips):

    print("\n========== DELETE TRIP ==========")

    trip_id = get_trip_id()

    for trip in trips:

        if trip["id"] == trip_id:

            print("Destination:", trip["destination"])

            confirm = input(
                "Confirm deletion (yes/no): "
            ).lower()

            if confirm == "yes":

                trips.remove(trip)
                save_trips(trips)

                print("Trip deleted successfully!")

            else:
                print("Deletion cancelled.")

            return

    print("Trip ID not found.")


# ==========================================
# EXPENSE ANALYSIS
# ==========================================

def expense_summary(trips):

    print("\n========== EXPENSE ANALYSIS ==========")

    if not trips:
        print("No trip data available.")
        return

    costs = [float(trip["cost"]) for trip in trips]

    total = sum(costs)
    average = total / len(costs)

    highest = max(trips, key=lambda x: x["cost"])
    lowest = min(trips, key=lambda x: x["cost"])

    print("Total trips:", len(trips))
    print("Total expense: Rs.", round(total, 2))
    print("Average expense: Rs.", round(average, 2))

    print(
        "Highest expense:",
        highest["destination"],
        "- Rs.",
        highest["cost"]
    )

    print(
        "Lowest expense:",
        lowest["destination"],
        "- Rs.",
        lowest["cost"]
    )

    print("\nCategory Analysis:")

    categories = Counter(
        trip["category"] for trip in trips
    )

    for category, count in categories.items():
        print(category, ":", count, "trip(s)")


# ==========================================
# SMART DATE WARNINGS
# ==========================================

def date_warnings(trips):

    print("\n========== TRAVEL STATUS ==========")

    today = date.today()

    if not trips:
        print("No trips available.")
        return

    for trip in trips:

        start = date.fromisoformat(trip["start_date"])
        end = date.fromisoformat(trip["end_date"])

        if start > today:

            remaining = (start - today).days

            print(
                "UPCOMING:",
                trip["destination"],
                "-",
                remaining,
                "days remaining"
            )

        elif start <= today <= end:

            print(
                "ONGOING:",
                trip["destination"]
            )

        else:

            print(
                "COMPLETED:",
                trip["destination"]
            )


# ==========================================
# EXPORT REPORTS
# ==========================================

def export_reports(trips):

    print("\n========== EXPORT REPORTS ==========")

    if not trips:
        print("No trips to export.")
        return

    total = sum(trip["cost"] for trip in trips)

    average = total / len(trips)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # TEXT REPORT

    with open(
        f"travel_report_{timestamp}.txt",
        "w"
    ) as file:

        file.write("TRAVEL ITINERARY ORGANIZER\n")
        file.write("=" * 40 + "\n")

        file.write(f"Total trips: {len(trips)}\n")
        file.write(f"Total cost: Rs. {total}\n")
        file.write(f"Average cost: Rs. {average:.2f}\n")

        for trip in trips:
            file.write(
                f"\n{trip['destination']} | "
                f"{trip['start_date']} to {trip['end_date']} | "
                f"Rs. {trip['cost']}\n"
            )

    # MARKDOWN REPORT

    with open(
        f"travel_report_{timestamp}.md",
        "w"
    ) as file:

        file.write("# Travel Itinerary Report\n\n")

        file.write(f"- Total trips: {len(trips)}\n")
        file.write(f"- Total expense: Rs. {total}\n")
        file.write(f"- Average expense: Rs. {average:.2f}\n\n")

        file.write(
            "| Destination | Start Date | End Date | Cost |\n"
        )

        file.write(
            "|---|---|---|---:|\n"
        )

        for trip in trips:

            file.write(
                f"| {trip['destination']} | "
                f"{trip['start_date']} | "
                f"{trip['end_date']} | "
                f"{trip['cost']} |\n"
            )

    # CSV REPORT

    with open(
        f"travel_report_{timestamp}.csv",
        "w",
        newline=""
    ) as file:

        fields = [
            "id", "destination", "start_date",
            "end_date", "category", "cost", "notes"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()
        writer.writerows(trips)

    print("Three reports created successfully!")
    print("TXT, Markdown and CSV reports are ready.")


# ==========================================
# CSV IMPORT WITH ERROR CHECKING
# ==========================================

def import_csv(trips):

    print("\n========== IMPORT TRIPS ==========")

    filename = input("Enter CSV file name: ").strip()

    if not os.path.exists(filename):
        print("CSV file not found.")
        return

    added = 0
    errors = []

    required = {
        "destination", "start_date",
        "end_date", "category", "cost"
    }

    try:

        with open(filename, "r", newline="") as file:

            reader = csv.DictReader(file)

            if not reader.fieldnames or not required.issubset(
                set(reader.fieldnames)
            ):
                print("CSV file has missing columns.")
                return

            for row_number, row in enumerate(reader, start=2):

                try:

                    destination = row["destination"].strip()

                    start = row["start_date"]
                    end = row["end_date"]

                    datetime.strptime(start, "%Y-%m-%d")
                    datetime.strptime(end, "%Y-%m-%d")

                    cost = float(row["cost"])

                    if not destination:
                        raise ValueError("Empty destination")

                    if end < start:
                        raise ValueError("Invalid date range")

                    if cost < 0:
                        raise ValueError("Negative cost")

                    trip = {
                        "id": next_id(trips),
                        "destination": destination,
                        "start_date": start,
                        "end_date": end,
                        "category": row["category"].strip(),
                        "cost": cost,
                        "notes": row.get("notes", "").strip()
                    }

                    trips.append(trip)
                    added += 1

                except (ValueError, KeyError):
                    errors.append(
                        f"Row {row_number}: Invalid information"
                    )

        save_trips(trips)

        print("Successfully imported:", added)

        if errors:
            print("\nImport error log:")

            for error in errors:
                print(error)

    except OSError as error:
        print("Unable to import file:", error)


# ==========================================
# SAMPLE DATA GENERATOR
# ==========================================

def add_sample_data(trips):

    print("\n========== SAMPLE DATA ==========")

    if trips:
        confirm = input(
            "Add 35 sample trips to existing records? (yes/no): "
        ).lower()

        if confirm != "yes":
            print("Sample data cancelled.")
            return

    destinations = [
        "Hyderabad", "Vizag", "Vijayawada",
        "Warangal", "Araku Valley", "Tirupati",
        "Chennai", "Bangalore", "Mumbai",
        "Delhi", "Goa", "Pune", "Mysore",
        "Kochi", "Jaipur", "Agra", "Ooty",
        "Coorg", "Munnar", "Kolkata",
        "Amritsar", "Manali", "Shimla",
        "Udaipur", "Rishikesh", "Varanasi",
        "Guntur", "Nellore", "Kurnool",
        "Rajahmundry", "Srikakulam",
        "Kanyakumari", "Madurai", "Hampi",
        "Alleppey"
    ]

    categories = [
        "Holiday", "Education", "Family",
        "Adventure", "Other"
    ]

    today = date.today()

    for i, destination in enumerate(destinations):

        start = today + timedelta(days=10 + i * 3)
        end = start + timedelta(days=2)

        trip = {
            "id": next_id(trips),
            "destination": destination,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "category": categories[i % len(categories)],
            "cost": 1500 + (i * 350),
            "notes": "Sample travel record"
        }

        trips.append(trip)

    save_trips(trips)

    print("35 sample records added successfully!")


# ==========================================
# MAIN MENU
# ==========================================

def main():

    trips = load_trips()

    while True:

        print("\n")
        print("=" * 55)
        print("       TRAVEL ITINERARY ORGANIZER")
        print("          PLAN YOUR JOURNEY")
        print("=" * 55)

        print("1. Add New Trip")
        print("2. View All Trips")
        print("3. Search Trip")
        print("4. Edit Trip")
        print("5. Delete Trip")
        print("6. Expense Analysis")
        print("7. Travel Date Warnings")
        print("8. Export Reports")
        print("9. Import CSV")
        print("10. Add 35 Sample Records")
        print("0. Exit")

        print("-" * 55)

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_trip(trips)

        elif choice == "2":
            view_trips(trips)

        elif choice == "3":
            search_trip(trips)

        elif choice == "4":
            edit_trip(trips)

        elif choice == "5":
            delete_trip(trips)

        elif choice == "6":
            expense_summary(trips)

        elif choice == "7":
            date_warnings(trips)

        elif choice == "8":
            export_reports(trips)

        elif choice == "9":
            import_csv(trips)

        elif choice == "10":
            add_sample_data(trips)

        elif choice == "0":

            save_trips(trips)

            print("\nYour travel data has been saved.")
            print("Thank you for using our application!")
            break

        else:
            print("Invalid choice. Select 0 to 10.")


# ==========================================
# START APPLICATION
# ==========================================

if __name__ == "__main__":
    main()