from datetime import datetime
from tabulate import tabulate
from mysql.connector import Error
from typing import Optional

class FeesManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def manage_fees(self):
        """Manage organization fees"""
        while True:
            print("\n=== Fee Management ===")
            print("1. Add Fee")
            print("2. Process Payment")
            print("3. View Member Fees")
            print("4. View Organization Fees")
            print("5. Generate Financial Reports")
            print("6. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-6): ")
            
            if choice == '1':
                self.add_fee()
            elif choice == '2':
                self.process_payment()
            elif choice == '3':
                self.view_member_fees()
            elif choice == '4':
                self.view_org_fees()
            elif choice == '5':
                self.generate_reports()
            elif choice == '6':
                break
            else:
                print("Invalid choice!")

    def search_student(self):
        """Search for a student by name or student number"""
        while True:
            print("\n=== Search Student ===")
            print("1. Search by Student Number")
            print("2. Search by Name")
            print("3. View All Students")
            print("4. Back")
            
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == '1':
                # Show existing student numbers first
                self.db_manager.cursor.execute("""
                    SELECT stud_no, firstname, lastname, degrprog, batch, gender, birthday 
                    FROM student 
                    ORDER BY stud_no
                """)
                students = self.db_manager.cursor.fetchall()
                
                if students:
                    table_data = [[
                        row['stud_no'],
                        row['firstname'],
                        row['lastname'],
                        row['degrprog'],
                        row['batch'],
                        row['gender'],
                        row['birthday']
                    ] for row in students]
                    headers = ["Student No", "First Name", "Last Name", "Program", "Batch", "Gender", "Birthday"]
                    print("\nExisting Students:")
                    print(tabulate(table_data, headers=headers, tablefmt="grid"))
                
                stud_no = input("\nEnter student number: ")
                query = """
                    SELECT stud_no, firstname, lastname, degrprog, batch, gender, birthday 
                    FROM student 
                    WHERE stud_no = %s
                """
                self.db_manager.cursor.execute(query, (stud_no,))
                results = self.db_manager.cursor.fetchall()
                
                if results:
                    table_data = [[
                        row['stud_no'],
                        row['firstname'],
                        row['lastname'],
                        row['degrprog'],
                        row['batch'],
                        row['gender'],
                        row['birthday']
                    ] for row in results]
                    
                    headers = ["Student No", "First Name", "Last Name", "Program", "Batch", "Gender", "Birthday"]
                    print("\nStudent Information:")
                    print(tabulate(table_data, headers=headers, tablefmt="grid"))
                    return stud_no
                else:
                    print("✗ Student not found!")
                    
            elif choice == '2':
                name = input("Enter student name (first or last): ").strip()
                query = """
                    SELECT stud_no, firstname, lastname, degrprog, batch, gender, birthday 
                    FROM student 
                    WHERE firstname LIKE %s OR lastname LIKE %s
                """
                self.db_manager.cursor.execute(query, (f"%{name}%", f"%{name}%"))
                results = self.db_manager.cursor.fetchall()
                
                if results:
                    table_data = [[
                        row['stud_no'],
                        row['firstname'],
                        row['lastname'],
                        row['degrprog'],
                        row['batch'],
                        row['gender'],
                        row['birthday']
                    ] for row in results]
                    
                    headers = ["Student No", "First Name", "Last Name", "Program", "Batch", "Gender", "Birthday"]
                    print("\nSearch Results:")
                    print(tabulate(table_data, headers=headers, tablefmt="grid"))
                    
                    if len(results) == 1:
                        return results[0]['stud_no']
                    else:
                        stud_no = input("\nEnter the student number from the results: ")
                        return stud_no
                else:
                    print("✗ No students found with that name!")
            
            elif choice == '3':
                # Show all students with their details
                self.db_manager.cursor.execute("""
                    SELECT stud_no, firstname, lastname, degrprog, batch, gender, birthday 
                    FROM student 
                    ORDER BY lastname, firstname
                """)
                results = self.db_manager.cursor.fetchall()
                
                if results:
                    table_data = [[
                        row['stud_no'],
                        row['firstname'],
                        row['lastname'],
                        row['degrprog'],
                        row['batch'],
                        row['gender'],
                        row['birthday']
                    ] for row in results]
                    
                    headers = ["Student No", "First Name", "Last Name", "Program", "Batch", "Gender", "Birthday"]
                    print("\nAll Students:")
                    print(tabulate(table_data, headers=headers, tablefmt="grid"))
                    
                    stud_no = input("\nEnter the student number from the list: ")
                    return stud_no
                else:
                    print("No students found in the database!")
                    
            elif choice == '4':
                return None
            else:
                print("Invalid choice!")

    def add_fee(self):
        """Add a new fee"""
        print("\n=== Add New Fee ===")
        try:
            # Search for student
            stud_no = self.search_student()
            if not stud_no:
                return
                
            # Show available organizations with their details
            query = """
                SELECT o.org_id, o.org_name, o.year_established,
                       COUNT(DISTINCT b.stud_no) as total_members,
                       COUNT(DISTINCT CASE WHEN b.status = 'Active' THEN b.stud_no END) as active_members
                FROM organization o
                LEFT JOIN belongs_to b ON o.org_id = b.org_id
                GROUP BY o.org_id, o.org_name, o.year_established
                ORDER BY o.org_name
            """
            self.db_manager.cursor.execute(query)
            orgs = self.db_manager.cursor.fetchall()
            
            org_data = [[
                row['org_id'], 
                row['org_name'],
                row['year_established'],
                row['total_members'],
                row['active_members']
            ] for row in orgs]
            
            print("\nAvailable Organizations:")
            print(tabulate(org_data, 
                          headers=["ID", "Name", "Year Established", "Total Members", "Active Members"], 
                          tablefmt="grid"))
            
            org_id = int(input("\nEnter Organization ID: "))
            amount = float(input("Amount: "))
            due_date = input("Due Date (YYYY-MM-DD): ")
            
            # Check if organization exists
            self.db_manager.cursor.execute("SELECT org_name FROM organization WHERE org_id = %s", (org_id,))
            org = self.db_manager.cursor.fetchone()
            if not org:
                print("✗ Organization not found!")
                return
            
            # Check if student belongs to organization
            self.db_manager.cursor.execute("""
                SELECT status, semester, acad_year 
                FROM belongs_to 
                WHERE stud_no = %s AND org_id = %s
            """, (stud_no, org_id))
            membership = self.db_manager.cursor.fetchone()
            
            if not membership:
                print("✗ Student is not a member of this organization!")
                return
            
            query = """
                INSERT INTO payment (
                    amount, due_date, org_id, stud_no, 
                    payment_status, amount_paid, payment_date
                ) VALUES (%s, %s, %s, %s, 'Not Paid', 0, NULL)
            """
            
            self.db_manager.cursor.execute(query, (amount, due_date, org_id, stud_no))
            self.db_manager.connection.commit()
            print(f"✓ Fee added successfully!")
            
        except ValueError:
            print("✗ Invalid input. Please enter valid values.")
        except Error as e:
            print(f"✗ Error adding fee: {e}")

    def process_payment(self):
        """Process a payment"""
        print("\n=== Process Payment ===")
        try:
            # Search for student
            stud_no = self.search_student()
            if not stud_no:
                return
                
            # Show unpaid fees for the student with more details
            query = """
                SELECT 
                    p.payment_id, p.amount, p.amount_paid, p.due_date, 
                    p.payment_status, p.payment_date,
                    o.org_name,
                    DATEDIFF(CURRENT_DATE, p.due_date) as days_overdue
                FROM payment p
                JOIN organization o ON p.org_id = o.org_id
                WHERE p.stud_no = %s AND p.payment_status != 'Paid'
                ORDER BY p.due_date
            """
            
            self.db_manager.cursor.execute(query, (stud_no,))
            results = self.db_manager.cursor.fetchall()
            
            if not results:
                print("No unpaid fees found for this student!")
                return
                
            table_data = [[
                row['payment_id'],
                row['org_name'],
                row['amount'],
                row['amount_paid'] or 0,
                row['due_date'],
                row['payment_status'],
                row['payment_date'] or 'Not paid',
                row['days_overdue'] if row['days_overdue'] > 0 else 'Not overdue'
            ] for row in results]
            
            headers = ["Payment ID", "Organization", "Amount", "Amount Paid", 
                      "Due Date", "Status", "Payment Date", "Days Overdue"]
            print("\nUnpaid Fees:")
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            
            payment_id = int(input("\nEnter Payment ID to process: "))
            
            # Process the payment
            query = """
                SELECT p.*, s.firstname, s.lastname, o.org_name 
                FROM payment p
                JOIN student s ON p.stud_no = s.stud_no
                JOIN organization o ON p.org_id = o.org_id
                WHERE p.payment_id = %s AND p.payment_status != 'Paid'
            """
            
            self.db_manager.cursor.execute(query, (payment_id,))
            payment = self.db_manager.cursor.fetchone()
            
            if not payment:
                print("✗ Payment record not found or already paid!")
                return
            
            print("\nPayment Details:")
            print(f"Student: {payment['firstname']} {payment['lastname']}")
            print(f"Organization: {payment['org_name']}")
            print(f"Amount Due: {payment['amount']}")
            print(f"Amount Paid: {payment['amount_paid'] or 0}")
            print(f"Due Date: {payment['due_date']}")
            
            amount_paid = float(input("Enter amount to pay: "))
            payment_date = datetime.now().strftime('%Y-%m-%d')
            
            # Calculate new total paid amount
            new_amount_paid = (payment['amount_paid'] or 0) + amount_paid
            
            # Determine payment status
            if new_amount_paid >= payment['amount']:
                status = 'Paid'
            elif new_amount_paid > 0:
                status = 'Partial'
            else:
                status = 'Not Paid'
            
            update_query = """
                UPDATE payment 
                SET amount_paid = %s, payment_date = %s, payment_status = %s
                WHERE payment_id = %s
            """
            
            self.db_manager.cursor.execute(update_query, (new_amount_paid, payment_date, status, payment_id))
            self.db_manager.connection.commit()
            print("✓ Payment processed successfully!")
            
        except ValueError:
            print("✗ Invalid input. Please enter valid values.")
        except Error as e:
            print(f"✗ Error processing payment: {e}")

    def view_member_fees(self):
        """View all fees for a member"""
        try:
            # Search for student
            stud_no = self.search_student()
            if not stud_no:
                return
                
            # Use the GetMemberUnpaidFees stored procedure
            self.db_manager.cursor.callproc('GetMemberUnpaidFees', (stud_no,))
            results = self.db_manager.cursor.stored_results()
            results = next(results).fetchall()
            
            if results:
                # Convert results to list of lists for tabulate
                table_data = [[
                    row['stud_no'],
                    row['name'],
                    row['org_name'],
                    row['acad_year'],
                    row['semester'],
                    row['payment_status'],
                    row['due_date']
                ] for row in results]
                
                headers = ["Student No", "Name", "Organization", "Academic Year", 
                          "Semester", "Status", "Due Date"]
                print("\nMember Fees:")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
            else:
                print("No fees found for this member!")
                
        except Error as e:
            print(f"✗ Error viewing member fees: {e}")

    def view_org_fees(self):
        """View all fees for an organization"""
        try:
            # Show available organizations
            self.db_manager.cursor.execute("SELECT org_id, org_name FROM organization")
            orgs = self.db_manager.cursor.fetchall()
            
            # Convert dictionary results to list of lists for tabulate
            org_data = [[row['org_id'], row['org_name']] for row in orgs]
            
            print("\nAvailable Organizations:")
            print(tabulate(org_data, headers=["ID", "Name"], tablefmt="grid"))
            
            org_id = int(input("\nEnter Organization ID: "))
            semester = int(input("Enter semester (1 or 2): "))
            acad_year = input("Enter academic year (YYYY-YYYY): ")
            
            # Extract the first year from the academic year (e.g., "2024" from "2024-2025")
            batch_year = int(acad_year.split('-')[0])
            
            # Use the GetOrgMembersWithUnpaidFees stored procedure
            self.db_manager.cursor.callproc('GetOrgMembersWithUnpaidFees', (org_id, semester, batch_year))
            results = self.db_manager.cursor.stored_results()
            results = next(results).fetchall()
            
            if results:
                # Convert results to list of lists for tabulate
                table_data = [[
                    row['stud_no'],
                    row['name'],
                    row['payment_status'],
                    row['semester'],
                    row['acad_year'],
                    row['org_name']
                ] for row in results]
                
                headers = ["Student No", "Name", "Payment Status", "Semester", 
                          "Academic Year", "Organization"]
                print(f"\nFees for Organization {org_id}:")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
            else:
                print("No fees found for this organization!")
                
        except ValueError:
            print("✗ Invalid input. Please enter valid values.")
        except Error as e:
            print(f"✗ Error viewing organization fees: {e}")

    def generate_reports(self):
        """Generate financial reports"""
        while True:
            print("\n=== Financial Reports ===")
            print("1. Organization Fee Totals")
            print("2. Members with Highest Debt")
            print("3. Back to main menu")
            
            choice = input("Choose report type: ")
            
            if choice == '1':
                self.org_fee_totals_report()
            elif choice == '2':
                self.highest_debt_report()
            elif choice == '3':
                break
            else:
                print("Invalid choice!")

    def org_fee_totals_report(self):
        """Generate organization fee totals report"""
        try:
            # Show available organizations
            self.db_manager.cursor.execute("SELECT org_id, org_name FROM organization")
            orgs = self.db_manager.cursor.fetchall()
            
            org_data = [[row['org_id'], row['org_name']] for row in orgs]
            print("\nAvailable Organizations:")
            print(tabulate(org_data, headers=["ID", "Name"], tablefmt="grid"))
            
            org_id = int(input("\nEnter Organization ID: "))
            as_of_date = input("Enter as of date (YYYY-MM-DD): ")
            
            # Use the GetOrgFeeTotalsAsOfDate stored procedure
            self.db_manager.cursor.callproc('GetOrgFeeTotalsAsOfDate', (org_id, as_of_date))
            results = self.db_manager.cursor.stored_results()
            results = next(results).fetchall()
            
            if results:
                # Convert results to list of lists for tabulate
                table_data = [[
                    row['org_name'],
                    row['due_date'],
                    row['total_paid_fees'],
                    row['total_unpaid_fees']
                ] for row in results]
                
                headers = ["Organization", "Due Date", "Total Paid", "Total Unpaid"]
                print("\nOrganization Fee Totals:")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
            else:
                print("No data available for report!")
                
        except Error as e:
            print(f"✗ Error generating report: {e}")

    def highest_debt_report(self):
        """Generate members with highest debt report"""
        try:
            # Show available organizations
            self.db_manager.cursor.execute("SELECT org_id, org_name FROM organization")
            orgs = self.db_manager.cursor.fetchall()
            
            org_data = [[row['org_id'], row['org_name']] for row in orgs]
            print("\nAvailable Organizations:")
            print(tabulate(org_data, headers=["ID", "Name"], tablefmt="grid"))
            
            org_id = int(input("\nEnter Organization ID: "))
            semester = int(input("Enter semester (1 or 2): "))
            batch_year = input("Enter academic year (YYYY-YYYY): ")
            
            # Extract the first year from the academic year
            batch_year = int(batch_year.split('-')[0])
            
            # Use the GetOrgMembersWithHighestDebt stored procedure
            self.db_manager.cursor.callproc('GetOrgMembersWithHighestDebt', (org_id, semester, batch_year))
            results = self.db_manager.cursor.stored_results()
            results = next(results).fetchall()
            
            if results:
                # Convert results to list of lists for tabulate
                table_data = [[
                    row['stud_no'],
                    row['full_name'],
                    row['acad_year'],
                    row['semester'],
                    row['total_debt'],
                    row['org_name']
                ] for row in results]
                
                headers = ["Student No", "Name", "Academic Year", "Semester", 
                          "Total Debt", "Organization"]
                print("\nMembers with Highest Debt:")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
            else:
                print("No data available for report!")
                
        except ValueError:
            print("✗ Invalid input. Please enter valid values.")
        except Error as e:
            print(f"✗ Error generating report: {e}")
