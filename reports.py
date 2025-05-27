"""
Advanced reports module for the Student Organization Management System
"""

from mysql.connector import Error
from tabulate import tabulate
from datetime import datetime

class AdvancedReports:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def advanced_reports_menu(self):
        """Advanced reports menu with all 10 reporting features"""
        while True:
            print("\n" + "=" * 70)
            print("                    ADVANCED REPORTS")
            print("=" * 70)
            print("1.  View members by role, status, gender, degree program, batch")
            print("2.  View members with unpaid fees for specific semester/year")
            print("3.  View member's unpaid fees across all organizations")
            print("4.  View executive committee members for specific year")
            print("5.  View all Presidents (or any role) by year (chronological)")
            print("6.  View late payments for specific semester/year")
            print("7.  View active vs inactive members percentage (last n semesters)")
            print("8.  View alumni members as of specific date")
            print("9.  View total unpaid/paid fees as of specific date")
            print("10. View members with highest debt for specific semester")
            print("11. Back to main menu")
            
            choice = input("\nEnter your choice (1-11): ")
            
            if choice == '1':
                self.view_members_by_criteria()
            elif choice == '2':
                self.view_unpaid_fees_by_semester()
            elif choice == '3':
                self.view_member_unpaid_fees()
            elif choice == '4':
                self.view_executive_committee()
            elif choice == '5':
                self.view_role_history()
            elif choice == '6':
                self.view_late_payments()
            elif choice == '7':
                self.view_active_inactive_percentage()
            elif choice == '8':
                self.view_alumni_members()
            elif choice == '9':
                self.view_fees_summary_by_date()
            elif choice == '10':
                self.view_highest_debt()
            elif choice == '11':
                break
            else:
                print("Invalid choice! Please try again.")
    
    def view_members_by_criteria(self):
        """1. View all members of the organization by role, status, gender, degree program, batch"""
        print("\n=== View Members by Criteria ===")
        try:
            # Show available organizations
            self.db.cursor.execute("SELECT org_id, org_name FROM organization")
            orgs = self.db.cursor.fetchall()
            
            print("\nAvailable Organizations:")
            for org in orgs:
                print(f"{org['org_id']}. {org['org_name']}")
            
            org_id = int(input("Organization ID: "))
            
            print("\nFilter options (press Enter to skip any filter):")
            role_filter = input("Role (e.g., President, Secretary, Member): ")
            status_filter = input("Status (e.g., Active, Inactive): ")
            gender_filter = input("Gender (M/F): ")
            degprog_filter = input("Degree Program: ")
            batch_filter = input("Batch Year: ")
            
            # Build dynamic query
            base_query = """SELECT s.stud_no, s.firstname, s.lastname, s.gender, s.degrprog,
                                  b.role, b.status, b.committee, b.batch_year, b.semester
                           FROM student s
                           JOIN belongs_to b ON s.stud_no = b.stud_no
                           WHERE b.org_id = %s"""
            
            params = [org_id]
            
            if role_filter:
                base_query += " AND b.role LIKE %s"
                params.append(f"%{role_filter}%")
            if status_filter:
                base_query += " AND b.status LIKE %s"
                params.append(f"%{status_filter}%")
            if gender_filter:
                base_query += " AND s.gender = %s"
                params.append(gender_filter.upper())
            if degprog_filter:
                base_query += " AND s.degrprog LIKE %s"
                params.append(f"%{degprog_filter}%")
            if batch_filter:
                base_query += " AND b.batch_year = %s"
                params.append(int(batch_filter))
            
            base_query += " ORDER BY b.batch_year DESC, b.semester DESC, b.role, s.lastname, s.firstname"
            
            self.db.cursor.execute(base_query, params)
            results = self.db.cursor.fetchall()
            
            if results:
                # Convert dictionary results to list of lists
                table_data = [[
                    row['stud_no'],
                    row['firstname'],
                    row['lastname'],
                    row['gender'],
                    row['degrprog'],
                    row['role'],
                    row['status'],
                    row['committee'],
                    row['batch_year'],
                    row['semester']
                ] for row in results]
                
                headers = ["Student No", "First Name", "Last Name", "Gender", "Degree Program", 
                          "Role", "Status", "Committee", "Batch Year", "Semester"]
                print(f"\nMembers of Organization {org_id} (Filtered Results):")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
                print(f"\nTotal members found: {len(results)}")
            else:
                print("No members found matching the criteria!")
                
        except ValueError:
            print("✗ Invalid input.")
        except Error as e:
            print(f"✗ Error viewing members: {e}")
    
    def view_unpaid_fees_by_semester(self):
        """2. View members with unpaid fees for specific semester/year"""
        print("\n=== Members with Unpaid Fees by Semester ===")
        try:
            # Show available organizations
            self.db.cursor.execute("SELECT org_id, org_name FROM organization")
            orgs = self.db.cursor.fetchall()
            
            print("\nAvailable Organizations:")
            for org in orgs:
                print(f"{org['org_id']}. {org['org_name']}")
            
            org_id = int(input("Organization ID: "))
            acad_year = input("Academic Year (YYYY-YYYY): ")
            semester = int(input("Semester (1 or 2): "))
            
            # Direct query for more detailed information
            query = """SELECT s.stud_no, 
                             CONCAT(s.firstname, ' ', s.lastname) AS name,
                             p.payment_status,
                             p.amount,
                             p.amount_paid,
                             p.due_date,
                             DATEDIFF(CURRENT_DATE, p.due_date) as days_overdue,
                             b.semester,
                             b.acad_year,
                             o.org_name
                      FROM payment p
                      JOIN student s ON s.stud_no = p.stud_no
                      JOIN organization o ON o.org_id = p.org_id
                      JOIN belongs_to b ON b.stud_no = p.stud_no AND b.org_id = p.org_id
                      WHERE p.payment_status = 'Unpaid'
                        AND b.semester = %s
                        AND b.acad_year = %s
                        AND o.org_id = %s
                      ORDER BY days_overdue DESC, p.due_date ASC"""
            
            self.db.cursor.execute(query, (semester, acad_year, org_id))
            results = self.db.cursor.fetchall()
            
            if results:
                # Convert dictionary results to list of lists
                table_data = [[
                    row['stud_no'],
                    row['name'],
                    row['payment_status'],
                    row['amount'],
                    row['amount_paid'],
                    row['due_date'],
                    row['days_overdue'],
                    row['semester'],
                    row['acad_year'],
                    row['org_name']
                ] for row in results]
                
                headers = ["Student No", "Name", "Status", "Amount", "Amount Paid", 
                          "Due Date", "Days Overdue", "Semester", "Academic Year", "Organization"]
                print(f"\nMembers with Unpaid Fees - {acad_year}, Semester {semester}:")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
                
                total_unpaid = sum(float(row['amount']) - float(row['amount_paid'] or 0) for row in results)
                print(f"\nSummary:")
                print(f"Total members with unpaid fees: {len(results)}")
                print(f"Total unpaid amount: ₱{total_unpaid:.2f}")
            else:
                print("No unpaid fees found for this semester!")
                
        except ValueError:
            print("✗ Invalid input.")
        except Error as e:
            print(f"✗ Error viewing unpaid fees: {e}")
    
    def view_member_unpaid_fees(self):
        """3. View member's unpaid fees across all organizations"""
        print("\n=== Member's Unpaid Fees (All Organizations) ===")
        try:
            stud_no = input("Student Number: ")
            
            # Direct query for detailed fee information
            query = """SELECT s.stud_no,
                             CONCAT(s.firstname, ' ', s.lastname) AS name,
                             o.org_name,
                             p.amount,
                             p.amount_paid,
                             p.payment_status,
                             p.due_date,
                             DATEDIFF(CURRENT_DATE, p.due_date) as days_overdue,
                             b.acad_year,
                             b.semester
                      FROM payment p
                      JOIN student s ON p.stud_no = s.stud_no
                      JOIN organization o ON p.org_id = o.org_id
                      JOIN belongs_to b ON b.stud_no = s.stud_no AND b.org_id = o.org_id
                      WHERE p.payment_status = 'Unpaid'
                        AND s.stud_no = %s
                      ORDER BY p.due_date ASC"""
            
            self.db.cursor.execute(query, (stud_no,))
            results = self.db.cursor.fetchall()
            
            if results:
                # Convert dictionary results to list of lists
                table_data = [[
                    row['stud_no'],
                    row['name'],
                    row['org_name'],
                    row['amount'],
                    row['amount_paid'],
                    row['payment_status'],
                    row['due_date'],
                    row['days_overdue'],
                    row['acad_year'],
                    row['semester']
                ] for row in results]
                
                headers = ["Student No", "Name", "Organization", "Amount", "Amount Paid",
                          "Status", "Due Date", "Days Overdue", "Academic Year", "Semester"]
                print(f"\nUnpaid Fees for Student {stud_no}:")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
                
                total_debt = sum(float(row['amount']) - float(row['amount_paid'] or 0) for row in results)
                print(f"\nSummary:")
                print(f"Total unpaid fees: {len(results)}")
                print(f"Total debt: ₱{total_debt:.2f}")
            else:
                print("No unpaid fees found for this student!")
                
        except Error as e:
            print(f"✗ Error viewing member unpaid fees: {e}")
    
    def view_executive_committee(self):
        """4. View executive committee members for specific year"""
        print("\n=== Executive Committee Members ===")
        try:
            # Show available organizations
            self.db.cursor.execute("SELECT org_id, org_name FROM organization")
            orgs = self.db.cursor.fetchall()
            
            print("\nAvailable Organizations:")
            for org in orgs:
                print(f"{org['org_id']}. {org['org_name']}")
            
            org_id = int(input("Organization ID: "))
            acad_year = input("Academic Year (YYYY-YYYY): ")
            
            # Direct query for executive committee
            query = """SELECT s.stud_no,
                             CONCAT(s.firstname, ' ', s.lastname) AS name,
                             b.role,
                             b.committee,
                             b.semester,
                             b.acad_year,
                             o.org_name
                      FROM belongs_to b
                      JOIN student s ON b.stud_no = s.stud_no
                      JOIN organization o ON b.org_id = o.org_id
                      WHERE b.org_id = %s
                        AND b.acad_year = %s
                        AND b.role IN ('President', 'Vice President', 'Secretary', 'Treasurer', 'Auditor')
                      ORDER BY 
                        CASE b.role
                            WHEN 'President' THEN 1
                            WHEN 'Vice President' THEN 2
                            WHEN 'Secretary' THEN 3
                            WHEN 'Treasurer' THEN 4
                            WHEN 'Auditor' THEN 5
                            ELSE 6
                        END,
                        b.semester"""
            
            self.db.cursor.execute(query, (org_id, acad_year))
            results = self.db.cursor.fetchall()
            
            if results:
                # Convert dictionary results to list of lists
                table_data = [[
                    row['stud_no'],
                    row['name'],
                    row['role'],
                    row['committee'],
                    row['semester'],
                    row['acad_year'],
                    row['org_name']
                ] for row in results]
                
                headers = ["Student No", "Name", "Role", "Committee", "Semester", 
                          "Academic Year", "Organization"]
                print(f"\nExecutive Committee Members for {acad_year}:")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
                print(f"\nTotal executive members: {len(results)}")
            else:
                print("No executive committee members found!")
                
        except Error as e:
            print(f"✗ Error viewing executive committee: {e}")
    
    def view_role_history(self):
        """5. View all Presidents (or any role) by year (chronological)"""
        print("\n=== Role History (Chronological) ===")
        try:
            # Show available organizations
            self.db.cursor.execute("SELECT org_id, org_name FROM organization")
            orgs = self.db.cursor.fetchall()
            
            print("\nAvailable Organizations:")
            for org in orgs:
                print(f"{org['org_id']}. {org['org_name']}")
            
            org_id = int(input("Organization ID: "))
            role = input("Role to search (e.g., President, Secretary): ")
            
            # Direct query for role history
            query = """SELECT s.stud_no,
                             CONCAT(s.firstname, ' ', s.lastname) AS name,
                             b.role,
                             b.acad_year,
                             b.semester,
                             b.committee,
                             o.org_name
                      FROM belongs_to b
                      JOIN student s ON b.stud_no = s.stud_no
                      JOIN organization o ON b.org_id = o.org_id
                      WHERE b.org_id = %s
                        AND b.role LIKE %s
                      ORDER BY b.acad_year DESC, b.semester DESC"""
            
            self.db.cursor.execute(query, (org_id, f"%{role}%"))
            results = self.db.cursor.fetchall()
            
            if results:
                # Convert dictionary results to list of lists
                table_data = [[
                    row['stud_no'],
                    row['name'],
                    row['role'],
                    row['acad_year'],
                    row['semester'],
                    row['committee'],
                    row['org_name']
                ] for row in results]
                
                headers = ["Student No", "Name", "Role", "Academic Year", "Semester", 
                          "Committee", "Organization"]
                print(f"\nHistory of {role} positions (Most Recent First):")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
                print(f"\nTotal records found: {len(results)}")
            else:
                print(f"No {role} positions found!")
                
        except Error as e:
            print(f"✗ Error viewing role history: {e}")
    
    def view_late_payments(self):
        """6. View late payments for specific semester/year"""
        print("\n=== Late Payments Report ===")
        try:
            # Show available organizations
            self.db.cursor.execute("SELECT org_id, org_name FROM organization")
            orgs = self.db.cursor.fetchall()
            
            print("\nAvailable Organizations:")
            for org in orgs:
                print(f"{org['org_id']}. {org['org_name']}")
            
            org_id = int(input("Organization ID: "))
            acad_year = input("Academic Year (YYYY-YYYY): ")
            semester = int(input("Semester (1 or 2): "))
            
            # Direct query for late payments
            query = """SELECT s.stud_no,
                             CONCAT(s.firstname, ' ', s.lastname) AS name,
                             p.amount - COALESCE(p.amount_paid, 0) as late_payment,
                             CONCAT(b.acad_year, ' - ', b.semester) as ay_sem,
                             p.due_date,
                             p.payment_date,
                             DATEDIFF(p.payment_date, p.due_date) as days_late,
                             o.org_name
                      FROM payment p
                      JOIN student s ON p.stud_no = s.stud_no
                      JOIN organization o ON p.org_id = o.org_id
                      JOIN belongs_to b ON b.stud_no = p.stud_no AND b.org_id = p.org_id
                      WHERE p.org_id = %s
                        AND b.acad_year = %s
                        AND b.semester = %s
                        AND p.payment_status = 'Partial'
                        AND p.payment_date > p.due_date
                      ORDER BY days_late DESC, p.payment_date DESC"""
            
            self.db.cursor.execute(query, (org_id, acad_year, semester))
            results = self.db.cursor.fetchall()
            
            if results:
                # Convert dictionary results to list of lists
                table_data = [[
                    row['stud_no'],
                    row['name'],
                    row['late_payment'],
                    row['ay_sem'],
                    row['due_date'],
                    row['payment_date'],
                    row['days_late'],
                    row['org_name']
                ] for row in results]
                
                headers = ["Student No", "Name", "Late Payment", "AY-SEM", "Due Date",
                          "Payment Date", "Days Late", "Organization"]
                print(f"\nLate Payments - {acad_year}, Semester {semester}:")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
                
                total_late = sum(float(row['late_payment']) for row in results)
                avg_late_days = sum(row['days_late'] for row in results) / len(results)
                
                print(f"\nSummary:")
                print(f"Total late payments: {len(results)}")
                print(f"Total late payment amount: ₱{total_late:.2f}")
                print(f"Average days late: {avg_late_days:.1f}")
            else:
                print("No late payments found for this semester!")
                
        except Error as e:
            print(f"✗ Error viewing late payments: {e}")
    
    def view_active_inactive_percentage(self):
        """7. View active vs inactive members percentage (last n semesters)"""
        print("\n=== Active vs Inactive Members Percentage ===")
        try:
            # Show available organizations
            self.db.cursor.execute("SELECT org_id, org_name FROM organization")
            orgs = self.db.cursor.fetchall()
            
            print("\nAvailable Organizations:")
            for org in orgs:
                print(f"{org['org_id']}. {org['org_name']}")
            
            org_id = int(input("Organization ID: "))
            n_semesters = int(input("Number of semesters to analyze: "))
            
            # Direct query for membership activity
            query = """SELECT 
                         acad_year,
                         semester,
                         COUNT(*) as total_members,
                         SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active_members,
                         SUM(CASE WHEN status IN ('Inactive', 'Alumni') THEN 1 ELSE 0 END) as inactive_members
                      FROM belongs_to
                      WHERE org_id = %s
                      GROUP BY acad_year, semester
                      ORDER BY acad_year DESC, semester DESC
                      LIMIT %s"""
            
            self.db.cursor.execute(query, (org_id, n_semesters))
            results = self.db.cursor.fetchall()
            
            if results:
                table_data = []
                for row in results:
                    total = row['total_members']
                    active = row['active_members']
                    inactive = row['inactive_members']
                    
                    active_pct = (active / total * 100) if total > 0 else 0
                    inactive_pct = (inactive / total * 100) if total > 0 else 0
                    
                    table_data.append([
                        f"{active_pct:.1f}%",
                        f"{inactive_pct:.1f}%",
                        row['acad_year'],
                        row['semester']
                    ])
                
                headers = ["Active %", "Inactive/Alumni %", "Academic Year", "Semester"]
                print(f"\nActive vs Inactive Analysis (Last {n_semesters} semesters):")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
                
                # Overall summary
                total_all = sum(row['total_members'] for row in results)
                active_all = sum(row['active_members'] for row in results)
                
                if total_all > 0:
                    overall_active_pct = (active_all / total_all * 100)
                    print(f"\nOverall Summary ({n_semesters} semesters):")
                    print(f"Average active percentage: {overall_active_pct:.1f}%")
                    print(f"Average inactive percentage: {100 - overall_active_pct:.1f}%")
            else:
                print("No membership data found!")
                
        except Error as e:
            print(f"✗ Error viewing active/inactive percentage: {e}")
    
    def view_alumni_members(self):
        """8. View alumni members as of specific date"""
        print("\n=== Alumni Members Report ===")
        try:
            # Show available organizations
            self.db.cursor.execute("SELECT org_id, org_name FROM organization")
            orgs = self.db.cursor.fetchall()
            
            print("\nAvailable Organizations:")
            for org in orgs:
                print(f"{org['org_id']}. {org['org_name']}")
            
            org_id = int(input("Organization ID: "))
            as_of_date = input("As of date (YYYY-MM-DD): ")
            
            # Direct query for alumni members
            query = """SELECT s.stud_no,
                             CONCAT(s.firstname, ' ', s.lastname) AS name,
                             CONCAT(b.role, ', ', b.committee, ', ', b.semester, ' sem') AS alumni_record,
                             o.org_name
                      FROM belongs_to b
                      JOIN student s ON b.stud_no = s.stud_no
                      JOIN organization o ON b.org_id = o.org_id
                      WHERE b.org_id = %s
                        AND b.status = 'Alumni'
                        AND STR_TO_DATE(CONCAT(SUBSTRING_INDEX(b.acad_year, '-', 1), '-', 
                                             IF(b.semester = '1', '06-01', '11-30')), '%Y-%m-%d') <= %s
                      ORDER BY b.acad_year DESC, b.semester DESC"""
            
            self.db.cursor.execute(query, (org_id, as_of_date))
            results = self.db.cursor.fetchall()
            
            if results:
                # Convert dictionary results to list of lists
                table_data = [[
                    row['stud_no'],
                    row['name'],
                    row['alumni_record'],
                    row['org_name']
                ] for row in results]
                
                headers = ["Student No", "Name", "Alumni Record", "Organization"]
                print(f"\nAlumni Members as of {as_of_date}:")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
                print(f"\nTotal alumni: {len(results)}")
            else:
                print("No alumni members found!")
                
        except Error as e:
            print(f"✗ Error viewing alumni members: {e}")
    
    def view_fees_summary_by_date(self):
        """9. View total unpaid/paid fees as of specific date"""
        print("\n=== Fees Summary by Date ===")
        try:
            # Show available organizations
            self.db.cursor.execute("SELECT org_id, org_name FROM organization")
            orgs = self.db.cursor.fetchall()
            
            print("\nAvailable Organizations:")
            for org in orgs:
                print(f"{org['org_id']}. {org['org_name']}")
            
            org_id = int(input("Organization ID: "))
            as_of_date = input("As of date (YYYY-MM-DD): ")
            
            # Direct query for fees summary
            query = """SELECT o.org_name,
                             p.due_date,
                             SUM(CASE WHEN p.payment_status = 'Paid' THEN p.amount_paid ELSE 0 END) as total_paid,
                             SUM(CASE WHEN p.payment_status = 'Unpaid' THEN p.amount ELSE 0 END) as total_unpaid
                      FROM payment p
                      JOIN organization o ON o.org_id = p.org_id
                      WHERE p.org_id = %s
                        AND p.due_date <= %s
                      GROUP BY o.org_name, p.due_date"""
            
            self.db.cursor.execute(query, (org_id, as_of_date))
            results = self.db.cursor.fetchall()
            
            if results:
                # Convert dictionary results to list of lists
                table_data = [[
                    row['org_name'],
                    row['due_date'],
                    row['total_paid'],
                    row['total_unpaid']
                ] for row in results]
                
                headers = ["Organization", "Due Date", "Total Paid", "Total Unpaid"]
                print(f"\nFees Summary as of {as_of_date}:")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
                
                total_paid = sum(float(row['total_paid'] or 0) for row in results)
                total_unpaid = sum(float(row['total_unpaid'] or 0) for row in results)
                
                print(f"\nSummary:")
                print(f"Total paid amount: ₱{total_paid:.2f}")
                print(f"Total unpaid amount: ₱{total_unpaid:.2f}")
                print(f"Total amount: ₱{total_paid + total_unpaid:.2f}")
            else:
                print("No fee data found!")
                
        except Error as e:
            print(f"✗ Error viewing fees summary: {e}")
    
    def view_highest_debt(self):
        """10. View members with highest debt for specific semester"""
        print("\n=== Members with Highest Debt ===")
        try:
            # Show available organizations
            self.db.cursor.execute("SELECT org_id, org_name FROM organization")
            orgs = self.db.cursor.fetchall()
            
            print("\nAvailable Organizations:")
            for org in orgs:
                print(f"{org['org_id']}. {org['org_name']}")
            
            org_id = int(input("Organization ID: "))
            acad_year = input("Academic Year (YYYY-YYYY): ")
            semester = int(input("Semester (1 or 2): "))
            
            # Direct query for highest debt
            query = """SELECT s.stud_no,
                             CONCAT(s.firstname, ' ', s.lastname) AS name,
                             b.acad_year,
                             b.semester,
                             SUM(p.amount - COALESCE(p.amount_paid, 0)) as total_debt,
                             o.org_name
                      FROM payment p
                      JOIN student s ON p.stud_no = s.stud_no
                      JOIN organization o ON p.org_id = o.org_id
                      JOIN belongs_to b ON p.stud_no = b.stud_no AND p.org_id = b.org_id
                      WHERE p.org_id = %s
                        AND b.acad_year = %s
                        AND b.semester = %s
                        AND p.payment_status != 'Paid'
                      GROUP BY s.stud_no, s.firstname, s.lastname, b.acad_year, b.semester, o.org_name
                      ORDER BY total_debt DESC"""
            
            self.db.cursor.execute(query, (org_id, acad_year, semester))
            results = self.db.cursor.fetchall()
            
            if results:
                # Convert dictionary results to list of lists
                table_data = [[
                    row['stud_no'],
                    row['name'],
                    row['acad_year'],
                    row['semester'],
                    row['total_debt'],
                    row['org_name']
                ] for row in results]
                
                headers = ["Student No", "Name", "Academic Year", "Semester", "Total Debt", "Organization"]
                print(f"\nMembers with Highest Debt - {acad_year}, Semester {semester}:")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
                
                highest_debt = float(results[0]['total_debt'])
                total_debt = sum(float(row['total_debt']) for row in results)
                
                print(f"\nSummary:")
                print(f"Highest debt amount: ₱{highest_debt:.2f}")
                print(f"Total debt in system: ₱{total_debt:.2f}")
                print(f"Total members with debt: {len(results)}")
            else:
                print("No unpaid fees found for this semester!")
                
        except Error as e:
            print(f"✗ Error viewing highest debt: {e}")