# Main module for the Student Organization Management System

import mysql.connector
from datetime import datetime
from typing import Tuple, Optional
from tabulate import tabulate
from membership import MembershipManager
from organization import OrganizationManager
from fees import FeesManager
from reports import AdvancedReports

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

def search_student(db_manager: DatabaseManager, search_term: str) -> Optional[str]:
    """Search for a student by name or student number"""
    try:
        # Try exact student number match first
        db_manager.cursor.execute("""
            SELECT stud_no, firstname, lastname, degrprog, batch 
            FROM student 
            WHERE stud_no = %s
        """, (search_term,))
        result = db_manager.cursor.fetchone()
        
        if result:
            return result['stud_no']
        
        # If no exact match, search by name
        db_manager.cursor.execute("""
            SELECT stud_no, firstname, lastname, degrprog, batch 
            FROM student 
            WHERE firstname LIKE %s OR lastname LIKE %s
        """, (f"%{search_term}%", f"%{search_term}%"))
        results = db_manager.cursor.fetchall()
        
        if not results:
            print("✗ No students found!")
            return None
            
        if len(results) == 1:
            return results[0]['stud_no']
            
        # If multiple results, show them in a table
        print("\nMultiple students found. Please select one:")
        table_data = [[
            idx + 1,
            row['stud_no'],
            row['firstname'],
            row['lastname'],
            row['degrprog'],
            row['batch']
        ] for idx, row in enumerate(results)]
        
        print(tabulate(table_data, 
                      headers=["#", "Student No", "First Name", "Last Name", "Program", "Batch"],
                      tablefmt="grid"))
        
        while True:
            try:
                choice = int(input("\nEnter the number of the student (0 to cancel): "))
                if choice == 0:
                    return None
                if 1 <= choice <= len(results):
                    return results[choice - 1]['stud_no']
                print("Invalid choice! Please try again.")
            except ValueError:
                print("Please enter a valid number!")
                
    except mysql.connector.Error as e:
        print(f"✗ Error searching for student: {e}")
        return None

def authenticate_user(db_manager: DatabaseManager, username: str, password: str) -> Tuple[bool, str]:
    """Authenticate a user and return their role"""
    # Check admin credentials
    if username == "admin" and password == "admin":
        return True, "admin"
    
    # Check student credentials
    query = """
        SELECT s.stud_no, b.role, b.org_id, o.org_name
        FROM student s
        JOIN belongs_to b ON s.stud_no = b.stud_no
        JOIN organization o ON b.org_id = o.org_id
        WHERE s.stud_no = %s AND b.status = 'Active'
    """
    db_manager.cursor.execute(query, (username,))
    result = db_manager.cursor.fetchone()
    
    if result:
        return True, f"member_{result['role']}_{result['org_id']}"
    return False, ""

def signup(db_manager: DatabaseManager) -> bool:
    """Handle student signup"""
    print("\n=== Student Signup ===")
    try:
        # Check if student number already exists
        while True:
            stud_no = input("Student Number: ")
            db_manager.cursor.execute("SELECT stud_no FROM student WHERE stud_no = %s", (stud_no,))
            if not db_manager.cursor.fetchone():
                break
            print("✗ Student number already exists! Please try another one.")
        
        firstname = input("First Name: ")
        lastname = input("Last Name: ")
        degrprog = input("Degree Program: ")
        
        while True:
            try:
                batch = int(input("Batch Year: "))
                break
            except ValueError:
                print("✗ Please enter a valid year!")
        
        while True:
            gender = input("Gender (M/F): ").upper()
            if gender in ['M', 'F']:
                break
            print("✗ Please enter M or F!")
        
        while True:
            birthday = input("Birthday (YYYY-MM-DD): ")
            try:
                datetime.strptime(birthday, '%Y-%m-%d')
                break
            except ValueError:
                print("✗ Please enter a valid date in YYYY-MM-DD format!")
        
        # Insert student record
        query = """INSERT INTO student (
                    stud_no, firstname, lastname, degrprog, batch, gender, birthday
                  ) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        values = (stud_no, firstname, lastname, degrprog, batch, gender, birthday)
        
        db_manager.cursor.execute(query, values)
        db_manager.connection.commit()
        
        # Show available organizations for membership
        print("\nAvailable Organizations:")
        db_manager.cursor.execute("""
            SELECT org_id, org_name, year_established 
            FROM organization 
            ORDER BY org_name
        """)
        organizations = db_manager.cursor.fetchall()
        
        if organizations:
            table_data = [[
                idx + 1,
                org['org_id'],
                org['org_name'],
                org['year_established'].strftime('%Y-%m-%d')
            ] for idx, org in enumerate(organizations)]
            
            print(tabulate(table_data,
                          headers=["#", "ID", "Name", "Established"],
                          tablefmt="grid"))
            
            while True:
                try:
                    choice = int(input("\nSelect organization to join (0 to skip): "))
                    if choice == 0:
                        break
                    if 1 <= choice <= len(organizations):
                        org_id = organizations[choice - 1]['org_id']
                        # Add student to organization
                        current_year = datetime.now().year
                        query = """INSERT INTO belongs_to (
                                    stud_no, org_id, semester, acad_year, status, role, committee, batch_year
                                  ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                        values = (stud_no, org_id, '1', f"{current_year}-{current_year+1}", 'Active', 'Member', 'General', batch)
                        db_manager.cursor.execute(query, values)
                        db_manager.connection.commit()
                        print(f"✓ Successfully joined {organizations[choice - 1]['org_name']}!")
                        break
                    print("Invalid choice! Please try again.")
                except ValueError:
                    print("Please enter a valid number!")
        
        print("✓ Signup successful! You can now login.")
        return True
        
    except Exception as e:
        print(f"✗ Error during signup: {e}")
        return False

def login(db_manager: DatabaseManager) -> Tuple[bool, str]:
    """Handle user login and return user role"""
    print("\n=== Login ===")
    print("1. Admin Login")
    print("2. Student Login")
    print("3. Back to Main Menu")
    
    choice = input("\nEnter your choice (1-3): ")
    
    if choice == '1':
        print("\n=== Admin Login ===")
        username = input("Username: ")
        password = input("Password: ")
        is_valid, role = authenticate_user(db_manager, username, password)
        if is_valid and role == "admin":
            print("✓ Admin login successful!")
            return True, role
        else:
            print("✗ Invalid admin credentials!")
            return False, ""
            
    elif choice == '2':
        print("\n=== Student Login ===")
        stud_no = input("Student Number: ")
        is_valid, role = authenticate_user(db_manager, stud_no, "")
        if is_valid and role.startswith("member_"):
            # Extract role information
            _, member_role, org_id = role.split("_")
            print(f"✓ Login successful! Welcome to the organization.")
            return True, role
        else:
            print("✗ Invalid student number or not an active organization member!")
            return False, ""
            
    elif choice == '3':
        return False, ""
    else:
        print("Invalid choice!")
        return False, ""

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
                is_valid, role = login(db_manager)
                if is_valid:
                    # Initialize managers
                    membership_manager = MembershipManager(db_manager)
                    organization_manager = OrganizationManager(db_manager)
                    fees_manager = FeesManager(db_manager)
                    reports_manager = AdvancedReports(db_manager)
                    
                    while True:
                        print("\n" + "=" * 70)
                        print("                    MAIN MENU")
                        print("=" * 70)
                        
                        if role == "admin":
                            print("1. Manage Members")
                            print("2. Manage Organizations")
                            print("3. Manage Fees")
                            print("4. Advanced Reports")
                            print("5. Logout")
                            print("6. Exit")
                            
                            choice = input("\nEnter your choice (1-6): ")
                            
                            if choice == '1':
                                membership_manager.manage_membership()
                            elif choice == '2':
                                organization_manager.manage_organizations()
                            elif choice == '3':
                                fees_manager.manage_fees()
                            elif choice == '4':
                                reports_manager.advanced_reports_menu()
                            elif choice == '5':
                                print("\nLogging out...")
                                print("✓ Successfully logged out!")
                                break
                            elif choice == '6':
                                print("\nThank you for using the Student Organization Management System!")
                                return
                            else:
                                print("Invalid choice! Please try again.")
                        else:
                            # Organization member menu
                            _, member_role, org_id = role.split("_")
                            print(f"1. View Organization Details")
                            print(f"2. View Member Fees")
                            print(f"3. View Organization Members")
                            print(f"4. Logout")
                            print(f"5. Exit")
                            
                            choice = input("\nEnter your choice (1-5): ")
                            
                            if choice == '1':
                                organization_manager.view_organization_details(int(org_id))
                            elif choice == '2':
                                fees_manager.view_member_fees()
                            elif choice == '3':
                                membership_manager.view_org_members(int(org_id))
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
