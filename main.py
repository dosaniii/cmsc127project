# Main module for the Student Organization Management System

import hashlib
import mysql.connector
from datetime import datetime
from membership import MembershipManager
from organization import OrganizationManager
from fees import FeesManager

class DatabaseManager:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="admin",
                password="admin",
                database="studentorg",
                auth_plugin='mysql_native_password'
            )
            self.cursor = self.connection.cursor(dictionary=True)
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                print("Error: Access denied. Please check your username and password.")
            elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                print("Error: Database does not exist.")
            else:
                print(f"Error: {err}")
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(db_manager: DatabaseManager, username: str, password: str) -> bool:
    """Authenticate a user (admin or regular user)"""
    hashed_password = hash_password(password)
    
    # Check admin credentials
    if username == "admin" and password == "admin":
        return True
    
    # Check regular user credentials
    db_manager.cursor.execute("SELECT * FROM student WHERE username = %s AND password = %s", 
                            (username, hashed_password))
    result = db_manager.cursor.fetchone()
    
    return result is not None

def signup(db_manager: DatabaseManager) -> bool:
    """Handle student signup"""
    print("\n=== Student Signup ===")
    try:
        stud_no = input("Student Number: ")
        firstname = input("First Name: ")
        lastname = input("Last Name: ")
        degrprog = input("Degree Program: ")
        batch = int(input("Batch Year: "))
        gender = input("Gender (M/F): ").upper()
        birthday = input("Birthday (YYYY-MM-DD): ")
        
        # Get username and validate it's unique
        while True:
            username = input("Username: ")
            db_manager.cursor.execute("SELECT stud_no FROM student WHERE username = %s", (username,))
            if not db_manager.cursor.fetchone():
                break
            print("✗ Username already taken. Please choose another one.")
        
        # Get password securely
        while True:
            password = input("Password: ")
            confirm_password = input("Confirm Password: ")
            if password == confirm_password:
                break
            print("✗ Passwords do not match. Please try again.")
        
        # Hash the password
        hashed_password = hash_password(password)
        
        query = """INSERT INTO student (stud_no, firstname, lastname, degrprog, batch, gender, birthday, username, password) 
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (stud_no, firstname, lastname, degrprog, batch, gender, birthday, username, hashed_password)
        
        db_manager.cursor.execute(query, values)
        db_manager.connection.commit()
        print("✓ Signup successful! You can now login.")
        return True
        
    except Exception as e:
        print(f"✗ Error during signup: {e}")
        return False

def login(db_manager: DatabaseManager) -> bool:
    """Handle user login"""
    print("\n=== Login ===")
    username = input("Username: ")
    password = input("Password: ")
    
    if authenticate_user(db_manager, username, password):
        print("✓ Login successful!")
        return True
    else:
        print("✗ Invalid username or password!")
        return False

def main():
    """Main function to run the Student Organization Management System"""
    print("\n" + "=" * 70)
    print("              STUDENT ORGANIZATION MANAGEMENT SYSTEM")
    print("=" * 70)
    
    with DatabaseManager() as db_manager:
        while True:
            print("\n1. Login")
            print("2. Signup (Students Only)")
            print("3. Exit")
            
            choice = input("\nEnter your choice (1-3): ")
            
            if choice == '1':
                if login(db_manager):
                    # Initialize managers
                    membership_manager = MembershipManager(db_manager)
                    organization_manager = OrganizationManager(db_manager)
                    fees_manager = FeesManager(db_manager)
                    
                    while True:
                        print("\n" + "=" * 70)
                        print("                    MAIN MENU")
                        print("=" * 70)
                        print("1. Manage Members")
                        print("2. Manage Organizations")
                        print("3. Manage Fees")
                        print("4. Logout")
                        print("5. Exit")
                        
                        choice = input("\nEnter your choice (1-5): ")
                        
                        if choice == '1':
                            membership_manager.manage_membership()
                        elif choice == '2':
                            organization_manager.manage_organizations()
                        elif choice == '3':
                            fees_manager.manage_fees()
                        elif choice == '4':
                            print("\nLogging out...")
                            print("✓ Successfully logged out!")
                            break
                        elif choice == '5':
                            print("\nThank you for using the Student Organization Management System!")
                            return
                        else:
                            print("Invalid choice! Please try again.")
            elif choice == '2':
                signup(db_manager)
            elif choice == '3':
                print("\nThank you for using the Student Organization Management System!")
                break
            else:
                print("Invalid choice! Please try again.")

if __name__ == "__main__":
    main()
