import datetime
LOGIN_FILE = "Login.txt"
ORDER_FILE = "orders.txt"
ACTIVITY_LOG_FILE = "activity_log.txt"

def usertype(type):
    if type == "SUPER_USER":
        return "superuser"
    elif type == "ADMIN":
        return "admin"
    elif type == "CUSTOMER_USER":
        return "customer"
    elif type == "INVENTORY_STAFF":
        return "inventory_staff"

    SUPER_USER = "superuser"
    ADMIN = "admin"
    CUSTOMER_USER = "customer"
    INVENTORY_STAFF = "inventory_staff"
    return SUPER_USER, ADMIN, CUSTOMER_USER, INVENTORY_STAFF


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
            f"{user['username']},{user['password']},{user['ic_number']},{user['phone']},{user['city']},{user['date']},{user['type']},{user['approved']}\n")


def save_all_users(users):
    with open(LOGIN_FILE, 'w') as file:
        file.write("# username, password, ic_number, phone, city, date, type, approved\n")
        for user in users:
            file.write(
                f"{user['username']},{user['password']},{user['ic_number']},{user['phone']},{user['city']},{user['date']},{user['type']},{user['approved']}\n")


def initialize_superusers():
    superusers = [
        {
            "username": "SUPERUSER1",
            "password": "SUPERUSER!",
            "ic_number": "050228082222",
            "phone": "0125674384",
            "city": "Kuala Lumpur",
            "date": "2024/08/01",
            "type": usertype("SUPER_USER"),
            "approved": True
        },
        {
            "username": "SUPERUSER2",
            "password": "SUPERUSER@",
            "ic_number": "050726081999",
            "phone": "0165738977",
            "city": "Kuala Lumpur",
            "date": "2024/08/01",
            "type": usertype("SUPER_USER"),
            "approved": True
        }
    ]

    # Check if superusers are already present
    for superuser in superusers:
        if not any(user['username'] == superuser['username'] for user in load_users()):
            load_users().append(superuser)

    save_all_users(load_users())


def sign_up():
    users = load_users()
    while True:
        username = input("Enter username: ")
        if any(user['username'] == username for user in users):
            print("Username already exists. Please choose a different username.")
        else:
            break

    symbols = "!@#$%^&*(),.?\":{}|<>"

    while True:
        password = input("Enter password (or type 'exit' to cancel: ")
        if password.lower() == 'exit':
            print("Password creation canceled. Exiting sign-up process.")
            return  # Exit the sign-up function

        # Check if the password length is less than 8
        if len(password) < 8:
            print("Password must be at least 8 characters long and contain at least one symbol.")
            continue  # Prompt the user to enter the password again

        # Check if there is at least one symbol in the password
        if not any(char in symbols for char in password):
            print("Password must contain at least one symbol.")
            continue  # Prompt the user to enter the password again

        print("Password created")
        break

    while True:
        ic_number = input("Enter IC number: ")
        if len(ic_number) != 12:
            print("IC number should have 12 numbers.")
            continue

        print("Successful")
        break

    phone = input("Enter phone number: ")
    city = input("Enter your city: ")
    date = input("Enter date (yyyy/mm/dd): ")
    user_type = input("Enter type (superuser/admin/customer/inventory_staff): ").lower()

    if user_type not in (usertype()):
        print("Invalid type. Please enter 'superuser', 'admin', 'customer', or 'inventory_staff'.")
        return
    if user_type == usertype("SUPER_USER") and initialize_superusers() >= 2:
        print("Cannot register more than two superusers.")
        return

    user = {
        "username": username,
        "password": password,
        "ic_number": ic_number,
        "phone": phone,
        "city": city,
        "date": date,
        "type": user_type,
        "approved": False  # New users need approval
    }
    save_user(user)
    print(f"{user_type.capitalize()} user '{username}' has been registered and is pending approval.")


def login():
    users = load_users()
    username = input("Enter username: ")
    password = input("Enter password: ")

    for user in users:
        if user["username"] == username and user["password"] == password:
            if user["approved"]:
                print(f"Login successful! Welcome {username}.")
                log_activity(username, "logged in")
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
    admin_username = input("Enter superuser username for access: ")
    admin_password = input("Enter superuser password for access: ")

    # Check superuser credentials
    valid_superuser = False
    for user in users:
        if user["username"] == admin_username and user["password"] == admin_password and user["type"] == "SUPER_USER" and \
                user["approved"]:
            valid_superuser = True
            break

    if not valid_superuser:
        print("Invalid superuser credentials.")
        return

    pending_users = [user for user in users if not user["approved"]]

    if not pending_users:
        print("No users pending approval.")
        return

    user_types = ["SUPER_USER", "ADMIN", "CUSTOMER_USER", "INVENTORY_STAFF"]
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
                    print(f"{selected_type.capitalize()} user '{user_to_approve['username']}' has been approved.")
                else:
                    print("Invalid choice. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        else:
            print("Invalid choice. Please enter a valid number.")
    except ValueError:
        print("Invalid input. Please enter a number.")
# number wrong and string wrong


def get_pending_approvals():
    users = load_users()
    pending_users = [user for user in users if not user["approved"]]
    return pending_users


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
        if user["username"] == admin_username and user["password"] == admin_password and user["type"] == usertype("SUPER_USER") and user["approved"]:
            valid_superuser = True
            break

    if not valid_superuser:
        print("Invalid superuser credentials.")
        return

    user_to_disable = input("Enter the username to disable: ")
    for u in users:
        if u["username"] == user_to_disable:
            u["approved"] = False
            save_all_users(users)
            print(f"User '{user_to_disable}' has been disabled.")
            return
    print(f"User '{user_to_disable}' not found.")


def view_user_system_usage():
    admin_username = input("Enter superuser username for access: ")
    admin_password = input("Enter superuser password for access: ")

    users = load_users()
    for user in users:
        if user["username"] == admin_username and user["password"] == admin_password and user["type"] == usertype("SUPER_USER") and user["approved"]:
            print("System usage by users:")
            try:
                with open(ACTIVITY_LOG_FILE, 'r') as file:
                    for line in file:
                        print(line.strip())
            except FileNotFoundError:
                print("No activity log found.")
            return
    print("Invalid superuser credentials.")


def check_customer_order_status():
    customer_username = input("Enter the customer username to check order status: ")
    try:
        with open(ORDER_FILE, 'r') as file:
            orders = [line.strip() for line in file if line.startswith(customer_username)]
        if orders:
            print(f"Orders for customer '{customer_username}':")
            for order in orders:
                print(order)
        else:
            print(f"No orders found for customer '{customer_username}'.")
    except FileNotFoundError:
        print("No orders found.")
        superuser_menu()


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
        print("2. Check Customer Order Status")
        print("3. Report")
        print("4. Logout")
        choice = input("Enter your choice: ")

        if choice == '1':
            approve_user()
        elif choice == '2':
            check_customer_order_status()
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
        if user["username"] == admin_username and user["password"] == admin_password and user["type"] == usertype("SUPER_USER") and user["approved"]:
            valid_superuser = True
            break

    if not valid_superuser:
        print("Invalid superuser credentials.")
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
        print("6. Check Customer Order Status")
        print("7. Modify User Details")
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
            check_customer_order_status()
        elif choice == '7':
            modify_user_details()
        elif choice == '8':
            report()
        elif choice == '9':
            main_menu()
            break
        else:
            print("Invalid choice. Please try again.")


def user_menu():
    while True:
        print("\nUser Menu")
        print("1. Check Customer Order Status")
        choice = input("Enter your choice: ")
        if choice == '1':
            check_customer_order_status()
            break
        else:
            print("Invalid choice. Please try again.")


def main_menu():
    print("\nWelcome to KL CENTRAL COMPUTER COMPANY  "
          "Sign in or login to run it !")
    initialize_superusers()
    while True:
        print("\n1. Sign Up")
        print("2. Login")
        print("3. Approve User")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            sign_up()
        elif choice == '2':
            user = login()
            if user:
                if user["type"] == usertype("CUSTOMER_USER"):
                    user_menu()
                elif user["type"] == usertype("ADMIN"):
                    admin_menu()
                elif user["type"] == usertype("SUPER_USER"):
                    superuser_menu()
                elif user["type"] == usertype("INVENTORY_STAFF"):
                    inventory_menu()

        elif choice == '3':
            approve_user()
        elif choice == '4':
            print("Exiting. Have a nice day!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main_menu()

