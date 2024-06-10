import mysql.connector
import re

# Connect to MySQL database
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="milk_store"
)
db_cursor = connection.cursor()

def calculate_total_price(selected_product, selected_size, qty):
    # Retrieve unit price from the database based on the selected product and size
    db_cursor.execute(
        "SELECT P_unitprice FROM products WHERE P_name = %s AND P_size = %s",
        (selected_product, selected_size)
    )
    unit_price = db_cursor.fetchone()[0]

    # Calculate total price
    total_price = qty * unit_price
    return total_price

def choose_product():
    print("\nSelect a Product:")
    print("1. Milk")
    print("2. Yoghurt")
    print("3. Cheese")
    while True:
        try:
            selection = int(input("Please enter your choice (1-3): "))
            if selection in [1, 2, 3]:
                product_names = {1: "Milk", 2: "Yoghurt", 3: "Cheese"}
                return product_names[selection]
            else:
                print("Invalid choice. Please enter a number between 1 and 3.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def choose_size():
    print("\nSelect the Size:")
    print("1. 250ml")
    print("2. 1L")
    print("3. 3L")
    while True:
        try:
            selection = int(input("Please enter your choice (1-3): "))
            if selection in [1, 2, 3]:
                size_names = {1: "250ml", 2: "1L", 3: "3L"}
                return size_names[selection]
            else:
                print("Invalid choice. Please enter a number between 1 and 3.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def input_quantity():
    while True:
        try:
            qty = int(input("Please enter the quantity: "))
            return qty
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

def verify_order(selected_product, selected_size, qty, customer_details):
    total_price = calculate_total_price(selected_product, selected_size, qty)

    print(f"\nOrder Summary:")
    print(f"Product: {selected_product}")
    print(f"Size: {selected_size}")
    print(f"Quantity: {qty}")
    print(f"Total Price: {total_price} RWF")
    print(f"Customer Information: {customer_details}")

    return total_price

def save_order_to_database(selected_product, selected_size, qty, total_price, user_id):
    # Insert order details
    db_cursor.execute(
        "INSERT INTO orders (user_id, product_name, product_size, quantity, total_price) VALUES (%s, %s, %s, %s, %s)",
        (user_id, selected_product, selected_size, qty, total_price)
    )

    # Commit the transaction
    connection.commit()

    print("Your order has been placed successfully!")

def validate_phone_number(phone_number):
    return re.fullmatch(r'07[89]\d{7}', phone_number) is not None

def register_user():
    while True:
        phone_number = input("Enter your phone number (starts with 078 or 079 and 10 digits long): ")
        if validate_phone_number(phone_number):
            pin = input("Enter a 4-digit PIN: ")
            email = input("Please enter your email: ")
            road_number = input("Please enter your road number: ")
            db_cursor.execute(
                "INSERT INTO users (phone_number, pin, email, road_number) VALUES (%s, %s, %s, %s)",
                (phone_number, pin, email, road_number)
            )
            connection.commit()
            print("Registration successful!")
            return db_cursor.lastrowid  # Returning the user_id
        else:
            print("Invalid phone number. Please try again.")

def login_user():
    phone_number = input("Enter your phone number: ")
    pin = input("Enter your PIN: ")
    db_cursor.execute(
        "SELECT user_id FROM users WHERE phone_number = %s AND pin = %s",
        (phone_number, pin)
    )
    result = db_cursor.fetchone()
    if result:
        print("Login successful!")
        return result[0]  # Returning the user_id
    else:
        print("Invalid phone number or PIN. Please try again.")
        return None

def start_application():
    ussd_input = input("Enter the USSD Code: ")
    if ussd_input == "*777#":
        print("\nWelcome to MUKAMIRA Dairy Ltd!")
        print("-------------------------------")

        user_id = None

        while user_id is None:
            print("\n1. Register")
            print("\n2. Login")
            choice = input("Please enter your choice: ")

            if choice == "1":
                user_id = register_user()
            elif choice == "2":
                user_id = login_user()
            else:
                print("\nInvalid choice. Please try again.")

        while True:
            print("\nMake your order now")
            print("1. Place an Order")
            print("2. Exit")
            choice = input("Please enter your choice: ")

            if choice == "1":
                selected_product = choose_product()
                selected_size = choose_size()
                qty = input_quantity()
                total_price = verify_order(selected_product, selected_size, qty, user_id)
                print("1. Confirm")
                print("2. Cancel")
                confirm_order = input("Choose any option: ")
                if confirm_order == "1":
                    save_order_to_database(selected_product, selected_size, qty, total_price, user_id)
                else:
                    print("Your order has been cancelled!")

            elif choice == "2":
                print("\nThank you for visiting MUKAMIRA Dairy Ltd")
                break
            else:
                print("\nInvalid choice. Please try again.")
    else:
        print("\nInvalid USSD Code. Please try again.")

if __name__ == "__main__":
    start_application()

# Close connection
db_cursor.close()
connection.close()
