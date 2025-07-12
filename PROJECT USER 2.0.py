#   CHEAH XUE XIAN
#   TP076244

import datetime
import json

LOGIN_FILE = "Login.txt"
ACTIVITY_LOG_FILE = "activity_log.txt"

FILE_INVENTORY_DATA = 'inventory_data.json'
FILE_PURCHASE_ORDERS = "purchase_orders.json"


def usertype(type=None):
    valid_types = {
        "SUPER_USER": "superuser",
        "ADMIN": "admin",
        "CUSTOMER_USER": "customer",
        "INVENTORY_STAFF": "inventory_staff"
    }
    if type:
        return valid_types.get(type.upper(), None)
    return list(valid_types.values())  # Return all valid user types


def log_activity(username, activity):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ACTIVITY_LOG_FILE, 'a') as file:
        file.write(f"{timestamp}, {username}, {activity}\n")

# username, password, ic_number, phone, city, date, type, approved


def load_users():
    users = []
    try:
        with open(LOGIN_FILE, 'r') as file:
            for line in file:
                if line.strip() and not line.startswith('#'):
                    fields = line.strip().split(',')
                    user = {
                        "username": fields[0],
                        "password": fields[1],
                        "ic_number": fields[2],
                        "phone": fields[3],
                        "city": fields[4],
                        "date": fields[5],
                        "type": fields[6],
                        "approved": fields[7] == 'True'
                    }
                    users.append(user)
    except FileNotFoundError:
        pass
    return users


def save_user(user):
    with open(LOGIN_FILE, 'a') as file:
        file.write(
            f"{user['username']},{user['password']},{user['ic_number']},{user['phone']},{user['city']},{user['date']},"
            f"{user['type']},{user['approved']}\n")


def save_all_users(users):
    with open(LOGIN_FILE, 'w') as file:
        file.write("# username, password, ic_number, phone, city, date, type, approved\n")
        for user in users:
            file.write(
                f"{user['username']},{user['password']},{user['ic_number']},{user['phone']},{user['city']},"
                f"{user['date']},{user['type']},{user['approved']}\n")


def sign_up():
    users = load_users()

    # Username validation
    while True:
        username = input("Enter username: ")
        if any(user['username'] == username for user in users):
            print("Username already exists. Please choose a different username.")
        else:
            break

    symbols = "!@#$%^&*(),.?\":{}|<>"

    # Password validation
    while True:
        password = input("Enter password (or type 'exit' to cancel): ")
        if password.lower() == 'exit':
            print("Password creation canceled. Exiting sign-up process.")
            return

        if len(password) < 8 or not any(char in symbols for char in password):
            print("Password must be at least 8 characters long and contain at least one symbol.")
            continue

        print("Password created")
        break

    # IC number validation
    while True:
        ic_number = input("Enter IC number: ")
        if len(ic_number) != 12 or not ic_number.isdigit():
            print("IC number should have 12 digits.")
            continue

        print("Successful")
        break

    phone = input("Enter phone number: ")
    city = input("Enter your city: ")

    # Date validation
    while True:
        date_str = input("Enter date of registration (yyyy-mm-dd): ")
        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            print("Date is valid.")
            break
        except ValueError:
            print("Invalid date format. Please enter the date in yyyy-mm-dd format.")

    user_type = input("Enter type (superuser/admin/customer/inventory_staff): ").lower()
    if user_type not in usertype():
        print("Invalid type. Please enter 'superuser', 'admin', 'customer', or 'inventory_staff'.")
        return

    user = {
        "username": username,
        "password": password,
        "ic_number": ic_number,
        "phone": phone,
        "city": city,
        "date": date.strftime("%Y/%m/%d"),
        "type": user_type,
        "approved": False  # New users need approval
    }

    if user_type == usertype("SUPER_USER"):
        # Superuser needs approval via passcode
        passcode = "SUPER123"  # Use a secure way to store and check passcodes in a real application
        entered_passcode = input("Enter passcode to approve superuser registration: ")
        if entered_passcode == passcode:
            user["approved"] = True
            print(f"Superuser '{username}' has been approved.")
        else:
            print("Incorrect passcode. Superuser registration pending manual approval.")

    save_user(user)
    print(f"{user_type.capitalize()} user '{username}' has been registered.")


def login():
    users = load_users()
    username = input("Enter username: ")
    password = input("Enter password: ")

    for user in users:
        if user["username"] == username and user["password"] == password:
            if user["approved"]:
                print(f"Login successful! Welcome {username}.")
                log_activity(username, "logged in")

                # Redirect to the correct menu based on user type
                if user["type"] == "SUPER_USER":
                    superuser_menu()  # Redirect to superuser menu
                elif user["type"] == "ADMIN":
                    admin_menu()  # Redirect to admin menu
                elif user["type"] == "CUSTOMER_USER":
                    customer_menu()  # Redirect to user menu
                elif user["type"] == "INVENTORY_STAFF":
                    inventory_staff_menu()  # Redirect to inventory staff menu

                return user
            else:
                print("Your account is not approved yet.")
                log_activity(username, "attempted to log in but is not approved")
                return None

    print("Invalid username or password.")
    log_activity(username, "failed login attempt")
    return None


def approve_user():
    users = load_users()
    admin_username = input("Enter username for access: ")
    admin_password = input("Enter password for access: ")

    # Check superuser credentials
    valid_superuser = False
    for user in users:
        if (user["username"] == admin_username and user["password"] == admin_password and
                user["type"] in ("superuser", "admin") and user["approved"]):

            valid_superuser = True
            break

    if not valid_superuser:
        print("Invalid user credentials.")
        return

    pending_users = [user for user in users if not user["approved"]]

    if not pending_users:
        print("No users pending approval.")
        return

    user_types = usertype()  # Use usertype function to get valid user types
    categorized_users = {user_type: [] for user_type in user_types}

    for user in pending_users:
        categorized_users[user["type"]].append(user)

    print("Select a user type to approve users:")
    for i, user_type in enumerate(user_types, start=1):
        print(f"{i}. {user_type.capitalize()}")

    try:
        choice = int(input("Enter the number of the user type: "))
        if 1 <= choice <= len(user_types):
            selected_type = user_types[choice - 1]
            users_of_selected_type = categorized_users[selected_type]

            if not users_of_selected_type:
                print(f"No pending {selected_type} users to approve.")
                return

            print(f"Select a {selected_type} to approve:")
            for i, user in enumerate(users_of_selected_type, start=1):
                print(f"{i}. Username: {user['username']}")

            try:
                user_choice = int(input("Enter the number of the user: "))
                if 1 <= user_choice <= len(users_of_selected_type):
                    user_to_approve = users_of_selected_type[user_choice - 1]
                    user_to_approve["approved"] = True
                    save_all_users(users)
                    log_activity(user_to_approve["username"], "approved")
                    print(f"{selected_type.capitalize()} user '{user_to_approve['username']}' has been approved.")
                else:
                    print("Invalid choice. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        else:
            print("Invalid choice. Please enter a valid number.")
    except ValueError:
        print("Invalid input. Please enter a number.")


def list_pending_approvals():
    users = load_users()
    pending_users = [user for user in users if not user["approved"]]
    if pending_users:
        print("Pending Approvals:")
        for user in pending_users:
            print(f"Username: {user['username']}, Type: {user['type']}")
    else:
        print("No users pending approval.")


def disable_user_access():
    users = load_users()
    admin_username = input("Enter superuser username for access: ")
    admin_password = input("Enter superuser password for access: ")

    # Check superuser credentials
    valid_superuser = False
    for user in users:
        if (user["username"] == admin_username and user["password"] == admin_password and
                user["type"] == "superuser" and user["approved"]):
            valid_superuser = True
            break

    if not valid_superuser:
        print("Invalid superuser credentials.")
        return

#   not showing disabled users from the report list
    enabled_users = [user for user in users if user["approved"]]
    if enabled_users:
        print("All Users Report:")
        for user in users:
            if user["approved"]:
                print(f"Username: {user['username']}, Date: {user['date']}, Type: {user['type']}")
    else:
        print("No enable user available")

    user_to_disable = input("Enter the username to disable: ")
    user_found = False
    for u in users:
        if u["username"] == user_to_disable:
            u["approved"] = False
            save_all_users(users)
            print(f"User '{user_to_disable}' has been disabled.")
            user_found = True
            break

    if not user_found:
        print(f"User '{user_to_disable}' not found. ")


def view_user_system_usage():
    print("System usage by users:")
    try:
        with open(ACTIVITY_LOG_FILE, 'r') as file:
            for line in file:
                print(line.strip())
    except FileNotFoundError:
        print("No activity log found.")
        return


def report():
    users = load_users()
    if users:
        print("All Users Report:")
        for user in users:
            print(f"Username: {user['username']}, Date: {user['date']}, Type: {user['type']}")
    else:
        print("No users found.")


def admin_menu():
    while True:
        print("\nAdmin Menu")
        print("1. Approve User")
        print("2. Check Inventory Purchase Order")
        print("3. Report")
        print("4. Logout")
        choice = input("Enter your choice: ")

        if choice == '1':
            approve_user()
        elif choice == '2':
            check_inventory_purchase_order()
        elif choice == '3':
            report()
        elif choice == '4':
            main_menu()
            break
        else:
            print("Invalid choice. Please try again.")


def modify_user_details():
    users = load_users()
    admin_username = input("Enter superuser username for access: ")
    admin_password = input("Enter superuser password for access: ")

    # Check superuser credentials
    valid_superuser = False
    for user in users:
        if user["username"] == admin_username and user["password"] == admin_password and user["type"] == usertype(
                "SUPER_USER") and user["approved"]:
            valid_superuser = True
            break

    if not valid_superuser:
        print("Invalid superuser credentials.")
        return
    pending_users = [user for user in users if not user["approved"]]

    if not pending_users:
        print("No users pending approval.")
        return

    # Display the list of users with numbers
    print("Select a user to modify:")
    for i, user in enumerate(users, start=1):
        print(f"{i}. Username: {user['username']}, Type: {user['type']}, City: {user['city']}")

    try:
        user_choice = int(input("Enter the number of the user to modify: "))
        if 1 <= user_choice <= len(users):
            user_to_modify = users[user_choice - 1]

            print(f"Modifying details for user '{user_to_modify['username']}':")
            new_ic_number = input("Enter new IC number: ")
            new_phone = input("Enter new phone number: ")
            new_city = input("Enter new city: ")
            new_date = input("Enter new date (yyyy/mm/dd): ")

            user_to_modify["ic_number"] = new_ic_number
            user_to_modify["phone"] = new_phone
            user_to_modify["city"] = new_city
            user_to_modify["date"] = new_date

            save_all_users(users)
            log_activity(admin_username, f"Modified details of user '{user_to_modify['username']}'")
            print(f"Details for user '{user_to_modify['username']}' have been updated.")
        else:
            print("Invalid choice. Please enter a valid number.")
    except ValueError:
        print("Invalid input. Please enter a number.")


def superuser_menu():
    while True:
        print("\nSuperuser Menu")
        print("1. Approve User")
        print("2. List Pending Approvals")
        print("3. Add User")
        print("4. Disable User Access")
        print("5. View User System Usage")
        print("6. Modify User Details")
        print("7. Check Inventory Purchase Order")
        print("8. Report")
        print("9. Logout")
        choice = input("Enter your choice: ")

        if choice == '1':
            approve_user()
        elif choice == '2':
            list_pending_approvals()
        elif choice == '3':
            sign_up()
        elif choice == '4':
            disable_user_access()
        elif choice == '5':
            view_user_system_usage()
        elif choice == '6':
            modify_user_details()
        elif choice == '7':
            check_inventory_purchase_order()
        elif choice == '8':
            report()
        elif choice == '9':
            main_menu()
            break
        else:
            print("Invalid choice. Please try again.")


def main_menu():

    print("\nWelcome to KL CENTRAL COMPUTER COMPANY  "
          "Please sign up or login! ")

    while True:
        print("\n1. Sign Up")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            sign_up()
        elif choice == '2':
            user = login()
            if user:
                if user["type"] == usertype("CUSTOMER_USER"):
                    customer_menu()
                elif user["type"] == usertype("ADMIN"):
                    admin_menu()
                elif user["type"] == usertype("SUPER_USER"):
                    superuser_menu()
                elif user["type"] == usertype("INVENTORY_STAFF"):
                    inventory_staff_menu()

        elif choice == '3':
            print("Exiting. Have a nice day!")
            break
        else:
            print("Invalid choice. Please try again.")


#   Inventory Management
def json_load_file(file_name):
    try:
        with open(file_name, 'r') as temp_file:
            return json.load(temp_file)
    except FileNotFoundError:
        print("There Is No Any Data. ")
        return {}
    except json.JSONDecodeError:
        print(f"Error: The file {file_name} is not a valid JSON file.")
        return {}


def dump_data(file_name, data_dump):
    with open(file_name, 'w') as temp_file:
        json.dump(data_dump, temp_file, indent=4)


def check_inventory():
    inventory_data = json_load_file(FILE_INVENTORY_DATA)

    if not inventory_data:
        print("No Items in The Inventory.")
        return

    # define column width
    column_width = 20
    line_length = column_width * 5
    title = "Current Stock"
    title_length = len(title)
    padding = (line_length - title_length) // 2
    centered_title = f"{'-' * padding}{title}{'-' * (line_length - padding - title_length)}"
    headers = (f"{'Item':<{column_width}}{'Purchase Price(RM)':<{column_width}}{'Selling Price(RM)':<{column_width}}"
               f"{'Service Price':<{column_width}}{'Quantity':<{column_width}}")

    print(centered_title)
    print(headers)
    print("-" * line_length)

    for item, details in inventory_data.items():
        purchase_price = details.get("Purchase Price", 0.0)
        selling_price = details.get("Selling Price", 0.0)
        service_price = details.get("service_price", 0.0)
        quantity = details.get("Quantity", 0)
        print(f"{item:<{column_width + 1}}{purchase_price:<{column_width + 1}}{selling_price:<{column_width + 1}}"
              f"{service_price:<{column_width + 1}}{quantity:<{column_width + 1}}")

    print('-' * line_length)

    while True:
        answer = input("Enter '0' for Exit: ")
        if answer == '0':
            break
        else:
            print("Invalid Value. Please Enter '0' for Exit! ")


def add_item_to_inventory():

    inventory_data = json_load_file(FILE_INVENTORY_DATA)

    print("Enter New Product Name or '0' to Exit : ")
    product = input().upper()

    if product == "0":
        return

    elif product not in inventory_data.keys():

        try:
            purchase_price = float(input("Enter The Purchase Price for The Product: "))
            selling_price = float(input("Enter The Selling Price for The Product: "))
            service_price = float(input("Enter The Service Price for The Product: "))
            quantity = int(input("Enter Quantity of Product: "))
            if quantity <= 0:
                print("Quantity Must Be Greater Than 0!")
                return

            inventory_data[product] = {"Purchase Price": purchase_price, "Selling Price": selling_price,
                                       "service_price": service_price, "Quantity": quantity}
            dump_data(FILE_INVENTORY_DATA, inventory_data)
            print(f"{product} Added Successfully! ")

        except ValueError:
            print("Invalid Input. Price Must Be A Number and Quantity Must Be An Integer. ")


def delete_inventory():
    inventory_data = json_load_file(FILE_INVENTORY_DATA)

    del_item = input("Enter The Product Name Want to Delete: ").upper()

    if del_item in inventory_data.keys():
        print(f"{'-' * 17}Delete Item{'-' * 17}")
        print(f"Item: {del_item}\nQuantity: {inventory_data[del_item]['Quantity']}"
              f"\nPurchase Price: {inventory_data[del_item]['Purchase Price']}"
              f"\nSelling Price: {inventory_data[del_item]['Purchase Price']}")

        print(f"{'-' * 45}")

        choice = input(f"Do You Want to Delete {del_item}? 'YES' / 'NO': ").upper()

        if choice == "YES":
            inventory_data.pop(del_item)
            dump_data(FILE_INVENTORY_DATA, inventory_data)
            print(f"{del_item} Deleted Successfully! ")

        elif choice == "NO":
            print(f"{del_item} Delete Unsuccessfully! ")
            return
        else:
            print("Invalid Value.")

    else:
        print(f"{del_item} Not Found in Inventory! ")


def update_inventory():
    inventory_data = json_load_file(FILE_INVENTORY_DATA)

    item = input("Enter The Product Name: ").upper()

    if item in inventory_data.keys():
        print("1. Update Selling Price. ")
        print("2. Update Quantity. ")
        print("3. Update Service Price.")
        print("0. Exit. ")
        print("Enter Your Choice: ")

        choice = input()
        if choice in ("1", "2", "3", "0"):

            if choice == "1":
                new_selling_price = float(input(f"Enter The New Selling Price for {item}: "))
                new_selling_price = round(new_selling_price, 2)
                inventory_data[item]["Selling Price"] = new_selling_price

            elif choice == "2":
                new_quantity = int(input(f"Enter The Quantity for {item}: "))
                inventory_data[item]["Quantity"] = new_quantity
            elif choice == "3":
                new_service_price = int(input(f"Enter The Service Price for {item}: "))
                inventory_data[item]["service_price"] = new_service_price

            elif choice == "0":
                return

            else:
                print("Invalid Choice. Please Try Again.")

            print(f"The {item} Updated Successfully!!!")

        else:
            print("Invalid Value. Please Try Again.")

        dump_data(FILE_INVENTORY_DATA, inventory_data)

    else:
        print("Product Not Found! ")


def stock_menu():

    while True:
        print(f"{'-' * 18}Stock Memu{'-' * 18}")
        print("1. Check Stock")
        print("2. Add Item to Inventory")
        print("3. Delete Item")
        print("4. Update Item Data")
        print("0. Return to Inventory Staff Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            check_inventory()

        elif choice == "2":
            add_item_to_inventory()

        elif choice == "3":
            delete_inventory()

        elif choice == "4":
            update_inventory()

        elif choice == "0":
            inventory_staff_menu()

        else:
            print("Invalid Value. Please Try Again.")


#   validation of order id exp: 'O00001'
def validate_order_id():
    while True:
        order_id = input("Enter The Order ID or '0' to Exit (e.g., OR0001, OR0002): ").upper()
        if order_id == "0":
            return
        elif len(order_id) == 6 and order_id[: 2] == 'OR' and order_id[2:].isdigit():
            print(f"Valid Order ID: {order_id}")
            return order_id

        else:
            print("Invalid Order ID. Please Enter Again!")


def create_inventory_purchase_order():
    purchase_orders = json_load_file(FILE_PURCHASE_ORDERS)
    inventory_data = json_load_file(FILE_INVENTORY_DATA)
    users = load_users()

    order_id = validate_order_id()

    if order_id not in purchase_orders:
        while True:
            # check if the staff is in the staff list
            staff_name = input("Enter The Staff Name: ")
            valid_staff = False

            for user in users:
                if user['username'] == staff_name and user['approved']:
                    valid_staff = True
                    break

            if valid_staff:
                break
            else:
                print("Invalid Order ID. Please Enter Again!")
    else:
        print("This Order ID Is Existed! ")
        return

    purchase_items = []

    while True:
        item = input("Enter Item Name or 'D' for Next Step: ").upper()

        if item == "D":
            break

        elif item in inventory_data.keys():
            try:
                quantity = int(input('Enter The Quantity: '))
                item_price = inventory_data[item]["Purchase Price"]
                amount = quantity * item_price
                purchase_items.append({
                    "Item": item,
                    "Quantity": quantity,
                    "Purchase Price": item_price,
                    "Amount": amount})
            except KeyError as e:
                print(f"{e} Not Found in Inventory for Item {item}")
            except ValueError:
                print("Invalid Input for Quantity.")

        elif item not in inventory_data.keys():
            answer = input("This Is New Item. Do You Want To Purchase? 'YES'/'NO': ").upper()
            if answer == 'YES':
                quantity = int(input('Enter The Quantity: '))
                item_price = float(input("Please Enter The Purchase Price: "))
                amount = quantity * item_price
                purchase_items.append({
                    "Item": item,
                    "Quantity": quantity,
                    "Purchase Price": item_price,
                    "Amount": amount})

            elif answer == 'NO':
                return

    total_amount = 0
    for item in purchase_items:
        total_amount += item["Amount"]

    while True:
        try:
            order_date = input("Enter Order Date (YYYY-MM-DD): ")
            datetime.datetime.strptime(order_date, '%Y-%m-%d')
            break
        except ValueError:
            print("Invalid Date Format. Please Enter The Date in YYYY-MM-DD Format.")

    while True:
        payment_status = input("Enter Payment Status (PAID/UNPAID): ").upper()
        if payment_status in ("PAID", "UNPAID"):
            break

        else:
            print("Invalid Value. Please Enter 'PAID' or 'UNPAID'!")

    purchase_order = {"Order ID:": order_id,
                      "Staff Name": staff_name,
                      "Order Date": order_date,
                      "Purchase Items": purchase_items,
                      "Total Amount": total_amount,
                      "Payment Status": payment_status,
                      "Order Status": "Pending"}

    #   insert order to purchase orders
    purchase_orders[order_id] = purchase_order
    dump_data(FILE_PURCHASE_ORDERS, purchase_orders)

    column_width = 15
    line_length = column_width * 4

    headers = f"{'Item':<{column_width}}{'Quantity':<{column_width}}{'Price':<{column_width}}{'Amount':<{column_width}}"

    print(f"{'-'*23}Order Details{'-'*23}")
    print(f"Order ID: {order_id}")
    print(f"Staff Name: {staff_name}")
    print(f"Order Date: {order_date}")
    print('-' * line_length)
    print(headers)

    for item in purchase_items:
        print(f"{item['Item']:<{column_width}}{item['Quantity']:<{column_width}}"
              f"{item['Purchase Price']:<{column_width}}{item['Amount']:<{column_width}.2f}")

    print('-' * line_length)
    print(f"Total Amount: {total_amount}")
    print(f"Payment Status: {payment_status}")
    print("Order Status: Pending")
    print('-' * line_length)
    answer = input("Enter '0' to Go Back: ")

    if answer == '0':
        return

    else:
        print("Invalid Value. Please Enter '0' to Go Back: ")


def order_add_item(order_data, inventory_data, order_id):

    while True:
        print("1. Done.")
        print("0. Exit.")
        print("Enter Item Name: ")

        new_item = input().upper()

        purchase_items = order_data[order_id]['Purchase Items']

        #  for people who don't want to add item
        if new_item == "0":
            return

        elif new_item == "1":
            break

        if new_item not in inventory_data:
            print(f"{new_item} Is A New Item. It Can Only Be Placed in A New Order. ")
            continue

        #   check if the item existed in the current order
        item_exists = False
        for item in purchase_items:
            if item['Item'] == new_item:
                item_exists = True
                break

        if item_exists:
            print(f"{new_item} Already Exist in This Order And Can Only Be Modified.")
            continue

        try:
            quantity = int(input("Enter The Quantity: "))
            if quantity <= 0:
                print("Quantity Must Be Greater Than 0. ")
                continue
        except ValueError:
            print("Invalid Input. Please Enter A Valid Number. ")
            continue
        item_price = inventory_data[new_item]["Purchase Price"]
        amount = quantity * item_price
        purchase_items.append({
            "Item": new_item,
            "Quantity": quantity,
            "Purchase Price": item_price,
            "Amount": amount})

        total_amount = 0
        for item in purchase_items:
            total_amount += item["Amount"]
        order_data[order_id]['Total Amount'] = total_amount

        dump_data(FILE_PURCHASE_ORDERS, order_data)
        print("Item Added Successfully")


def order_edit_quantity(order_data, order_id):
    while True:
        edit_item = input("Enter The Item Name You Want to Edit or 'D' for Done: ").upper()

        if edit_item == "D":
            break

        item_found = False

        order = order_data[order_id]
        for item in order['Purchase Items']:
            if item['Item'] == edit_item:
                item_found = True
                new_quantity = int(input("Enter The New Quantity: "))

                if new_quantity == 0:
                    #  remove item from order
                    order['Purchase Items'] = [
                        item for item in order['Purchase Items']
                        if item['Item'] != edit_item
                    ]
                    print(f"{edit_item} Remove from Order {order_id}as Quantity is 0.")

                else:
                    item['Quantity'] = new_quantity
                    item['Amount'] = new_quantity * item['Purchase Price']

                # recalculate total amount
                total_amount = 0
                for i in order['Purchase Items']:
                    total_amount += i['Amount']
                order['Total Amount'] = total_amount

                if total_amount == 0:
                    del order_data[order_id]

                # save updated data
                dump_data(FILE_PURCHASE_ORDERS, order_data)
                print(f"Quantity of {edit_item} in Order {order_id} Updated Successfully!")
                break

        if not item_found:
            print("Item Not Existed in The Order. ")


def order_edit_payment(order_data, order_id):
    print('1. Paid')
    print('0. Exit')
    choice = input("Please Enter Your Choice: ")
    if choice == "0":
        return
    elif choice == "1":
        order_data[order_id]['Payment Status'] = "PAID"
        order_data[order_id]['Order Status'] = "Received"
        print(f"Payment Status for Order{order_id} "
              f"Updated Successfully to {order_data[order_id]['Payment Status']}!")
        dump_data(FILE_PURCHASE_ORDERS, order_data)

    else:
        print("Invalid Value. Please Enter '1' for Update Payment Status")


def modify_inventory_purchase_order():
    order_data = json_load_file(FILE_PURCHASE_ORDERS)
    inventory_data = json_load_file(FILE_INVENTORY_DATA)

    order_id = validate_order_id()

    if order_id in order_data.keys():
        if order_data[order_id]['Payment Status'] == "UNPAID":
            print("Modify Purchase Order:")
            print("1. Add Item")
            print("2. Edit Quantity")
            print("3. Edit Payment Status")
            print("O. Exit ")
            print("Choose The Program: ")

            choice = input()
            if choice == "1":
                order_add_item(order_data, inventory_data, order_id)

            elif choice == "2":
                order_edit_quantity(order_data, order_id)

            elif choice == "3":
                order_edit_payment(order_data, order_id)

            elif choice == "0":
                return

        elif order_data[order_id]['Payment Status'] == "PAID":
            order = order_data[order_id]
            answer = input(f"Order {order_id} Has Been Paid! Any Item Not Available? ('YES'/'NO'): ").upper()

            if answer == 'YES':
                while True:
                    product = input("Enter The Unavailable Product Name or '0' for Done: ").upper()

                    if product == "0":
                        break
                    item_found = False

                    for item in order['Purchase Items']:
                        if item['Item'].upper() == product:
                            item_found = True
                            while True:
                                try:
                                    available_quantity = int(input(f"Enter Available Quantity for {product}: "))
                                    if available_quantity < 0:
                                        print("Quantity Cannot Be Negative. Please Enter Again. ")
                                    else:
                                        break
                                except ValueError:
                                    print("Invalid Input. Please Enter  A Valid Integer. ")

                            if available_quantity == 0:
                                #   remove item from order
                                order['Purchase Items'] = [item for item in order['Purchase Items']
                                                           if item['Item'].upper() != product]
                                print(f"{product} Removed fromOrder {order_id} As Quantity Is 0.")

                                #   check if order should be removed
                                if not order['Purchase Items']:
                                    del order_data[order_id]
                                    print(f"Order {order_id} Removed as No Items Left !")
                                    dump_data(FILE_PURCHASE_ORDERS, order_data)
                                    return
                            else:
                                original_quantity = item['Quantity']
                                item_price = item['Purchase Price']

                                if available_quantity < original_quantity:
                                    refund_amount = (original_quantity - available_quantity) * item_price
                                    print(f"Refund Amount for {product}: RM {refund_amount}")

                                #  update item quantity in order
                                item['Quantity'] = available_quantity
                                item['Amount'] = available_quantity * item_price
                            break
                    if not item_found:
                        print(f"Item {product} Not Found in The Order. ")

                # recalculate total amount
                total_amount = 0
                for item in order['Purchase Items']:
                    total_amount += item['Amount']
                order['Total Amount'] = total_amount

                if order['Purchase Items']:
                    dump_data(FILE_PURCHASE_ORDERS, order_data)
                    print(f"Order {order_id} updated successfully!")
                else:
                    dump_data(FILE_PURCHASE_ORDERS, order_data)
                    print(f"Order {order_id} updated successfully!")
            elif answer == "NO":
                return
            else:
                print("Invalid Value. Please Enter 'YES'/'NO'.)")
    else:
        print(f"Order {order_id} Not Found!")


#   2.3 check purchase order status
def check_inventory_purchase_order():
    purchase_orders = json_load_file(FILE_PURCHASE_ORDERS)

    while True:
        order_id = input("Enter Order ID to Check Status or '0' for Exit: ").upper()
        if order_id == "0":
            break
        elif order_id in purchase_orders:
            order = purchase_orders[order_id]

            print(f"{'-'*25} Order Details {'-'*25}")
            print(f"Order ID: {order_id}")
            print(f"Staff Name: {order['Staff Name']}")
            print(f"Order Date: {order['Order Date']}")
            print('-' * 65)
            print(f"{'No.':<5}{'Item':<15}{'Quantity':<15}{'Price':<15}{'Amount':<15}")
            print('-' * 65)

            item_num = 1
            for item in order['Purchase Items']:
                print(
                    f"{item_num:<5}{item['Item']:<15}{item['Quantity']:<15}{item['Purchase Price']:<15}"
                    f"{item['Amount']:<15.2f}")
                item_num += 1
            print('-' * 65)
            print(f"Total Amount: {order['Total Amount']}")
            print(f"Payment Status: {order['Payment Status']}")
            print(f"Order Status: {order['Order Status']}")
            print('-' * 65)
            e = input("Enter '0' for Exit: ")
            if e == "0":
                break
            else:
                print("Enter '0' for Exit: ")

        else:
            print("Order ID Nor Found! Please Enter A Valid Order ID.")


def cancel_inventory_purchase_order():
    order_data = json_load_file(FILE_PURCHASE_ORDERS)

    order_id = validate_order_id().upper()

    if order_id in order_data:

        if order_data[order_id]['Payment Status'] == "UNPAID":
            cancel = input(f"Do You Want to Cancel Order {order_id}? 'YES'/'NO'").upper()

            if cancel == "YES":
                del order_data[order_id]
                dump_data(FILE_PURCHASE_ORDERS, order_data)
                print(f"Order Cancelled Successfully!")

            elif cancel == "NO":
                print(f"Order {order_id} Cancel Unsuccessfully")
                return

            else:
                print("Invalid Value. Please Enter 'YES' / 'NO'")

        elif order_data[order_id]['Payment Status'] == "PAID":
            print("This Order Has Been Paid. Cannot Be Cancelled!")

    else:
        print(f"Order for {order_id} Not Found")


def receive_inventory_order():
    inventory_data = json_load_file(FILE_INVENTORY_DATA)
    purchase_orders = json_load_file(FILE_PURCHASE_ORDERS)
    order_id = input("Please Enter The Received Order ID: ").upper()

    if order_id in purchase_orders:
        order = purchase_orders[order_id]
        if order["Order Status"] == "Pending":
            order["Order Status"] = "Received"
            order["Payment Status"] = "PAID"

            #   add received item to stock
            for item in order["Purchase Items"]:
                item_name = item["Item"]
                purchase_price = item["Purchase Price"]
                quantity = item["Quantity"]

                if item_name in inventory_data:
                    inventory_data[item_name]["Quantity"] += quantity

                else:
                    #   add item that is not in inventory
                    print(f"Item {item_name} is not in the inventory.")
                    selling_price = float(input(f"Enter Selling Price for {item_name}: "))
                    service_price = float(input(f"Enter Service Price for {item_name}: "))
                    inventory_data[item_name] = {
                        "Purchase Price": purchase_price,
                        "Selling Price": selling_price,
                        "service_price": service_price,
                        "Quantity": quantity
                    }
            dump_data(FILE_PURCHASE_ORDERS, purchase_orders)
            dump_data(FILE_INVENTORY_DATA, inventory_data)

            print(f"Order ID {order_id} has been received and stock has been updated.")
        else:
            print(f"Order ID {order_id} has already been processed.")
    else:
        print(f"Order {order_id} Not Found!")


def inventory_purchase_order_menu():
    while True:
        print(f"{'-'*13}Purchase Order Menu{'-'*13}")
        print("1. Create Purchase Order")
        print("2. Modify Purchase Order")
        print("3. Check Purchase Order Status")
        print("4. Cancel Purchase Order")
        print("5. Receive Purchase Order")
        print("0. Back to Inventory Menu")

        choice = input("Enter Your Choice: ")

        if choice == "1":
            create_inventory_purchase_order()
        elif choice == "2":
            modify_inventory_purchase_order()
        elif choice == "3":
            check_inventory_purchase_order()
        elif choice == "4":
            cancel_inventory_purchase_order()
        elif choice == "5":
            receive_inventory_order()
        elif choice == "0":
            break
        else:
            print("Invalid Value. Please Try Again!")


def inventory_report():
    inventory_data = json_load_file(FILE_INVENTORY_DATA)
    column_width = 20
    line_length = column_width * 4

    title = "Current Stock"
    title_length = len(title)
    padding = (line_length - title_length) // 2
    centered_title = f"{'-' * padding}{title}{'-' * (line_length - padding - title_length)}"
    headers = (f"{'Item':<{column_width}}{'Purchase Price(RM)':<{column_width}}"
               f"{'Selling Price(RM)':<{column_width}}{'Quantity':<{column_width}}")

    print(centered_title)
    print(headers)
    print("-" * line_length)

    for item, details in inventory_data.items():
        purchase_price = details.get("Purchase Price")
        selling_price = details.get("Selling Price")
        quantity = details.get("Quantity")
        print(f"{item:<{column_width}}{purchase_price:<{column_width}}{selling_price:<{column_width}}"
              f"{quantity:<{column_width}}")
        #  need to add 1 to align with the headers
    print('-' * line_length)
    e = input("Enter '0' for Exit: ")
    if e == "0":
        return
    else:
        print("Invalid Value! Please Enter '0' for Exit! ")


def inventory_purchase_order_report():
    purchase_orders = json_load_file(FILE_PURCHASE_ORDERS)

    print(f"{'-' * 36} Purchase Order Report {'-' * 36}")
    print(
        f"{'Order ID':<15}{'Staff Name':<20}{'Order Date':<15}{'Total Amount':<15}{'Payment Status':<15}"
        f"{'Order Status':<15}")
    print('-' * 95)

    for order_id, order in purchase_orders.items():
        print(f"{order.get('Order ID:', 'N/A'):<15}"
              f"{order.get('Staff Name', 'N/A'):<20}"
              f"{order.get('Order Date', 'N/A'):<15}"
              f"{order.get('Total Amount', 'N/A'):<15}"
              f"{order.get('Payment Status', 'N/A'):<15}"
              f"{order.get('Order Status', 'N/A'):<15}\n")
    print('-'*95)
    e = input("Enter '0' for Exit: ")
    if e == "0":
        return
    else:
        print("Enter '0' for Exit: ")


def inventory_staff_reports():

    print("Report: ")
    print("1. Inventory Reports")
    print("2. Purchase Order Report")
    print("0. Exit")

    choice = input("Enter Your Choice: ")

    if choice == "1":
        inventory_report()
    elif choice == "2":
        inventory_purchase_order_report()
    elif choice == "0":
        return
    else:
        print("Invalid Value. Please Try Again!")


def inventory_staff_menu():
    while True:
        print(f"{'-' * 16}Inventory Staff Menu{'-' * 16}")
        print("1. Stock")
        print("2. Purchase Order")
        print("3. Reports")
        print("0. Exit")
        print(f"{'-' * 52}")

        choice = input("Please Enter Your Choice: ")

        if choice == "1":
            stock_menu()
        elif choice == "2":
            inventory_purchase_order_menu()
        elif choice == "3":
            inventory_staff_reports()
        elif choice == "0":
            main_menu()
            break
        else:
            print("Invalid Value. Please Try Again.")


#   Customer Management
def list_items(inventory):
    for item, details in inventory.items():
        print(f"{item.capitalize()}: Price = ${details['Selling Price']}, Stock = {details['Quantity']},"
              f" Service Price = ${details['service_price']}")


def update_stock(inventory, item, quantity):
    if item in inventory:
        inventory[item]['Quantity'] -= quantity


def restock(inventory, item, quantity):
    if item in inventory:
        inventory[item]['Quantity'] += quantity


def calculate_max(values, default_value=None):
    """Custom function to find maximum value."""
    if not values:
        return default_value

    max_value = values[0]
    for value in values:
        if value > max_value:
            max_value = value
    return max_value


def calculate_sum(values):
    """Custom function to calculate sum."""
    return sum(values)


def save_order_status(orders):
    with open("order_status.txt", "w") as f:
        for order in orders:
            f.write(f"Item: {order['item']}, Quantity: {order['quantity']}, Total Price: ${order['total_price']},"
                    f" Payment: {order['payment']}\n")


def save_service_order_status(service_orders):
    with open("service_order_status.txt", "w") as f:
        for order in service_orders:
            f.write(f"Item: {order['item']}, Quantity: {order['quantity']}, Service Cost: ${order['service_cost']},"
                    f" Status: {order['status']}, Payment: {order['payment']}\n")


def display_items_table(inventory):
    if not inventory:
        print("No items available in inventory.")
        return
    headers = ["#", "Item", "Price", "Stock"]

    widths = [
        3,
        calculate_max([len(str(i)) for i in inventory.keys()]) + 2,
        8,
        8,
    ]

    def print_row(data, widths):
        row = "|".join(str(item).ljust(width) for item, width in zip(data, widths))
        print(row)

    print_row(headers, widths)
    print("-" * (calculate_sum(widths) + len(headers) - 1))

    i = 1
    for item, details in inventory.items():
        data = [i, item.capitalize(), f"${details['Selling Price']}", details['Quantity']]
        print_row(data, widths)
        i += 1


def place_order(inventory, orders):
    if not inventory:
        print("No items available for purchase")
        return

    print("Available items:")
    display_items_table(inventory)

    try:
        item_choice = int(input("Enter the number of the item you want to purchase: "))
        items_list = list(inventory.keys())

        if 1 <= item_choice <= len(items_list):
            item = items_list[item_choice - 1]
            quantity = int(input("Enter the quantity: "))

            if inventory[item]['Quantity'] >= quantity:
                total_price = inventory[item]['Selling Price'] * quantity
                print(f"Total price: ${total_price}")
                payment_option = input("Choose payment option: (1) Pay Now (2) Pay Later: ")

                if payment_option == '1':
                    payment = float(input("Enter the exact payment amount: "))
                    if payment >= total_price:
                        update_stock(inventory, item, quantity)
                        orders.append({'item': item, 'quantity': quantity, 'total_price': total_price,
                                       'payment': 'Paid'})
                        change = payment - total_price
                        if change > 0:
                            print(f"Order placed successfully! Your change is ${change:.2f}")
                        else:
                            print("Order placed successfully!")
                    else:
                        print("Insufficient payment. Order not placed.")
                elif payment_option == '2':
                    orders.append({'item': item, 'quantity': quantity, 'total_price': total_price,
                                   'payment': 'Pending'})
                    print("Order placed successfully, but payment is pending.")
                    save_order_status(orders)
                else:
                    print("Invalid payment option.")

                save_order_status(orders)
            else:
                print("Item not available or insufficient stock.")
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input. Please enter a number corresponding to the item.")


def display_service_items_table(inventory):
    headers = ["#", "Item", "Service Price"]

    item_lengths = [len(str(item)) for item in inventory.keys()]

    #   default width if item_length is empty
    default_width = 10
    if item_lengths:
        widths = [
            3,
            calculate_max(item_lengths) + 2,
            15,
        ]
    else:
        widths = [
            3,
            default_width,
            15,
        ]

    def print_row(data, widths):
        row = "|".join(str(item).ljust(width) for item, width in zip(data, widths))
        print(row)

    if not inventory:
        print("There are no available services.")
        return

    print_row(headers, widths)
    print("-" * (calculate_sum(widths) + len(headers) - 1))

    i = 1
    for item, details in inventory.items():
        data = [i, item.capitalize(), f"${details['service_price']}"]
        print_row(data, widths)
        i += 1


def request_service(inventory, service_orders):
    print("Available items for service/repair:")
    display_service_items_table(inventory)

    if not inventory:
        return

    try:
        item_choice = int(input("Enter the number of the item you want to service/repair: "))
        items_list = list(inventory.keys())

        if 1 <= item_choice <= len(items_list):
            item = items_list[item_choice - 1]
            quantity = int(input("Enter the quantity for service/repair: "))
            tentative_time = "2-3 days"
            service_cost_per_item = inventory[item]['service_price']
            total_service_cost = service_cost_per_item * quantity
            print(f"Tentative timeline for service/repair: {tentative_time}")
            print(f"Service price per item: ${service_cost_per_item}")
            print(f"Total service cost: ${total_service_cost}")
            payment_option = input("Choose payment option: (1) Pay Now (2) Pay Later: ")

            if payment_option == '1':
                payment = float(input("Enter the exact payment amount for service: "))
                if payment >= total_service_cost:
                    service_orders.append({'item': item, 'quantity': quantity, 'service_cost': total_service_cost,
                                           'status': 'Pending', 'payment': 'Paid'})
                    change = payment - total_service_cost
                    if change > 0:
                        print(f"Service/Repair order placed successfully! Your change is ${change:.2f}")
                    else:
                        print("Service/Repair order placed successfully!")
                else:
                    print("Insufficient payment. Service/Repair order not placed.")
            elif payment_option == '2':
                service_orders.append({'item': item, 'quantity': quantity, 'service_cost': total_service_cost,
                                       'status': 'Pending', 'payment': 'Pending'})
                print("Service/Repair order placed successfully, but payment is pending.")
            else:
                print("Invalid payment option.")

            save_service_order_status(service_orders)
        else:
            print("Invalid selection.")
    except ValueError:
        print("Invalid input. Please enter a number corresponding to the item.")


def modify_order(inventory, orders, service_orders):
    def print_row(data, widths):
        row = "|".join(str(item).ljust(width) for item, width in zip(data, widths))
        print(row)

    print("1. Modify Purchase Order")
    print("2. Modify Service/Repair Order")
    choice = int(input("Enter your choice: "))

    if choice == 1:
        if orders:
            headers_purchase = ["#", "Item", "Quantity", "Total Price", "Payment"]
            widths_purchase = [5, 12, 12, 12, 12]

            print("\nPurchase Orders:")
            print_row(headers_purchase, widths_purchase)
            print("-" * (calculate_sum(widths_purchase) + len(headers_purchase) - 1))

            i = 1
            for order in orders:
                data = [i, order['item'].capitalize(), order['quantity'], f"${order['total_price']}", order['payment']]
                print_row(data, widths_purchase)
                i += 1

            order_index = int(input("Enter the order number to modify: ")) - 1
            if 0 <= order_index < len(orders):
                order = orders[order_index]
                print(
                    f"Current order details: Item: {order['item']}, Quantity: {order['quantity']},"
                    f" Total Price: ${order['total_price']}, Payment: {order['payment']}")

                if order['payment'] == 'Paid':
                    new_quantity = int(input("Enter the new quantity: ")) if order['payment'] == 'Pending' else order[
                        'quantity']
                else:
                    new_quantity = int(input("Enter the new quantity: "))

                if new_quantity <= inventory[order['item']]['Quantity'] + order['quantity']:
                    if order['payment'] == 'Pending':
                        restock(inventory, order['item'], order['quantity'])  # Revert the previous stock reduction
                        update_stock(inventory, order['item'], new_quantity)
                        order['quantity'] = new_quantity
                        order['total_price'] = inventory[order['item']]['Selling Price'] * new_quantity
                        # Corrected line
                        print("Order modified successfully!")
                    else:
                        print("Cannot modify a paid order.")
                else:
                    print("Insufficient stock for the new quantity.")
            else:
                print("Invalid order number.")
        else:
            print("No purchase orders to modify.")
    elif choice == 2:
        if service_orders:
            headers_service = ["#", "Item", "Quantity", "Service Cost", "Status", "Payment"]
            widths_service = [5, 12, 12, 15, 10, 12]

            print("\nService/Repair Orders:")
            print_row(headers_service, widths_service)
            print("-" * (calculate_sum(widths_service) + len(headers_service) - 1))

            i = 1
            for order in service_orders:
                data = [i, order['item'].capitalize(), order['quantity'], f"${order['service_cost']}", order['status'],
                        order['payment']]
                print_row(data, widths_service)
                i += 1

            order_index = int(input("Enter the service/repair order number to modify: ")) - 1
            if 0 <= order_index < len(service_orders):
                order = service_orders[order_index]
                print(
                    f"Current service order details: Item: {order['item']}, Quantity: {order['quantity']},"
                    f" Service Cost: ${order['service_cost']}, Status: {order['status']}, Payment: {order['payment']}")

                if order['payment'] == 'Paid':
                    new_quantity = int(input("Enter the new quantity: ")) if order['payment'] == 'Pending' else order[
                        'quantity']
                else:
                    new_quantity = int(input("Enter the new quantity: "))

                new_service_cost = inventory[order['item']]['service_price'] * new_quantity
                if order['payment'] == 'Pending':
                    order['quantity'] = new_quantity
                    order['service_cost'] = new_service_cost
                    print("Service/Repair order modified successfully!")
                else:
                    print("Cannot modify a paid order.")
            else:
                print("Invalid order number.")
        else:
            print("No service/repair orders to modify.")
    else:
        print("Invalid choice.")


def inquire_order_status(service_orders):
    def print_row(data, widths):
        row = "|".join(str(item).ljust(width) for item, width in zip(data, widths))
        print(row)

    headers_service = ["Item", "Quantity", "Service Cost", "Status", "Payment"]
    widths_service = [12, 12, 12, 12, 12]

    print("\nService/Repair Orders:")
    if service_orders:
        print_row(headers_service, widths_service)
        print("-" * calculate_sum(widths_service) + "-" * (len(headers_service) - 1))
        for order in service_orders:
            data = [order['item'].capitalize(), order['quantity'], f"${order['service_cost']}", order['status'],
                    order['payment']]
            print_row(data, widths_service)
    else:
        print("No service/repair orders available.")


def cancel_order(inventory, orders, service_orders):
    def print_row(data, widths):
        row = "|".join(str(item).ljust(width) for item, width in zip(data, widths))
        print(row)

    print("1. Cancel Purchase Order")
    print("2. Cancel Service/Repair Order")
    choice = int(input("Enter your choice: "))

    if choice == 1:
        if orders:
            headers_purchase = ["#", "Item", "Quantity", "Total Price", "Payment"]
            widths_purchase = [5, 12, 12, 12, 12]

            print("\nPurchase Orders:")
            print_row(headers_purchase, widths_purchase)
            print("-" * (calculate_sum(widths_purchase) + len(headers_purchase) - 1))

            i = 1
            for order in orders:
                data = [i, order['item'].capitalize(), order['quantity'], f"${order['total_price']}", order['payment']]
                print_row(data, widths_purchase)
                i += 1

            order_index = int(input("Enter the order number to cancel: ")) - 1
            if 0 <= order_index < len(orders):
                if orders[order_index]['payment'] == 'Pending':
                    restock(inventory, orders[order_index]['item'], orders[order_index]['quantity'])
                    orders.pop(order_index)
                    print("Order cancelled successfully.")
                    save_order_status(orders)
                else:
                    print("Cannot cancel a paid order.")
            else:
                print("Invalid order number.")
        else:
            print("No purchase orders to cancel.")
    elif choice == 2:
        if service_orders:
            headers_service = ["#", "Item", "Quantity", "Service Cost", "Status", "Payment"]
            widths_service = [5, 12, 12, 15, 10, 12]

            print("\nService/Repair Orders:")
            print_row(headers_service, widths_service)
            print("-" * (calculate_sum(widths_service) + len(headers_service) - 1))

            i = 1
            for order in service_orders:
                data = [i, order['item'].capitalize(), order['quantity'],
                        f"${order['service_cost']}", order['status'], order['payment']]
                print_row(data, widths_service)
                i += 1

            order_index = int(input("Enter the service/repair order number to cancel: ")) - 1
            if 0 <= order_index < len(service_orders):
                if service_orders[order_index]['payment'] == 'Pending':
                    service_orders.pop(order_index)
                    print("Service/Repair order cancelled successfully.")
                    save_service_order_status(service_orders)
                else:
                    print("Cannot cancel a paid order.")
            else:
                print("Invalid order number.")
        else:
            print("No service/repair orders to cancel.")
    else:
        print("Invalid choice.")


def view_reports(orders, service_orders):
    def print_row(data, widths):
        row = "|".join(str(item).ljust(width) for item, width in zip(data, widths))
        print(row)

    print("\nOrder Reports:")

    headers = ["Order Type", "Item", "Quantity", "Total Price/Service Cost", "Status", "Payment"]
    widths = [12, 12, 10, 25, 10, 12]

    print_row(headers, widths)
    print("-" * calculate_sum(widths) + "-" * (len(headers) - 1))

    for order in orders:
        data = ["Purchase", order['item'].capitalize(), order['quantity'], f"${order['total_price']}", "N/A",
                order['payment']]
        print_row(data, widths)

    for order in service_orders:
        data = ["Service", order['item'].capitalize(), order['quantity'], f"${order['service_cost']}", order['status'],
                order['payment']]
        print_row(data, widths)


def customer_menu():
    inventory = json_load_file(FILE_INVENTORY_DATA)
    orders = []
    service_orders = []

    while True:
        print("\nCustomer Menu")
        print("1. Purchase Order")
        print("2. Service/Repair Order")
        print("3. Modify Purchase/Service/Repair Order")
        print("4. Inquire Order Status")
        print("5. Cancel Order")
        print("6. View Reports")
        print("7. Exit")
        choice = int(input("Enter your choice: "))
        if choice == 1:
            place_order(inventory, orders)
        elif choice == 2:
            request_service(inventory, service_orders)
        elif choice == 3:
            modify_order(inventory, orders, service_orders)
        elif choice == 4:
            inquire_order_status(service_orders)
        elif choice == 5:
            cancel_order(inventory, orders, service_orders)
        elif choice == 6:
            view_reports(orders, service_orders)
        elif choice == 7:
            main_menu()
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")


main_menu()
