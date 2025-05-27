from datetime import datetime
from tabulate import tabulate

class MembershipManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def manage_membership(self):
        """Manage student memberships"""
        while True:
            print("\n=== Membership Management ===")
            print("1. Add Member to Organization")
            print("2. Update Member Status")
            print("3. View Member Details")
            print("4. View Organization Members")
            print("5. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-5): ")
            
            if choice == '1':
                self.add_member()
            elif choice == '2':
                self.update_member_status()
            elif choice == '3':
                self.view_member_details()
            elif choice == '4':
                org_id = input("Organization ID: ")
                self.view_org_members(org_id)
            elif choice == '5':
                break

    def add_member(self):
        """Add a new member to an organization"""
        stud_no = input("Student Number: ")
        #checks if student number exists
        query_check_student = "SELECT stud_no FROM student WHERE stud_no = %s"
        self.db_manager.cursor.execute(query_check_student, (stud_no,))
        if not self.db_manager.cursor.fetchone():
            print(f"✗ Student number {stud_no} does not exist. Please add the student first.")
            return
        org_id = input("Organization ID: ")
        #checks if organization exists
        query_check_org = "SELECT org_id FROM organization WHERE org_id = %s"
        self.db_manager.cursor.execute(query_check_org, (org_id,))
        if not self.db_manager.cursor.fetchone():
            print(f"✗ Organization ID {org_id} does not exist. Please add the organization first.")
            return

        semester = input("Semester (1/2): ")
        acad_year = input("Academic Year (YYYY-YYYY): ")
        status = input("Status (Active/Inactive/Alumni): ")
        role = input("Role: ")
        committee = input("Committee: ")

        query = """INSERT INTO belongs_to (stud_no, org_id, semester, acad_year, status, role, committee, batch_year)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (stud_no, org_id, semester, acad_year, status, role, committee, datetime.now().year)

        try:
            self.db_manager.cursor.execute(query, values)
            self.db_manager.connection.commit()
            print("✓ Member added successfully!")
        except Exception as e:
            print(f"✗ Error: {e}")


    def update_member_status(self):
        """Update a member's status"""
        stud_no = input("Student Number: ")
        org_id = input("Organization ID: ")
        new_status = input("New Status: ")
        
        query = """UPDATE belongs_to SET status = %s 
                WHERE stud_no = %s AND org_id = %s"""
        
        try:
            self.db_manager.cursor.execute(query, (new_status, stud_no, org_id))
            self.db_manager.connection.commit()
            print("✓ Status updated successfully!")
        except Exception as e:
            print(f"✗ Error: {e}")

    def view_member_details(self):
        """View member details"""
        stud_no = input("Student Number: ")
        
        query = """SELECT s.*, b.*, o.org_name 
                  FROM student s 
                  JOIN belongs_to b ON s.stud_no = b.stud_no 
                  JOIN organization o ON b.org_id = o.org_id 
                  WHERE s.stud_no = %s"""
        
        try:
            self.db_manager.cursor.execute(query, (stud_no,))
            results = self.db_manager.cursor.fetchall()
            
            if results:
                for row in results:
                    print(f"\nStudent: {row['firstname']} {row['lastname']}")
                    print(f"Organization: {row['org_name']}")
                    print(f"Role: {row['role']}")
                    print(f"Status: {row['status']}")
                    print(f"Committee: {row['committee']}")
            else:
                print("No records found.")
        except Exception as e:
            print(f"✗ Error: {e}")

    def view_org_members(self, org_id):
        """View all members of an organization"""
        query = """SELECT s.stud_no, 
                         CONCAT(s.firstname, ' ', s.lastname) AS full_name,
                         b.role, b.status, s.gender, s.degrprog,
                         b.batch_year, b.committee, o.org_name,
                         b.semester, b.acad_year
                  FROM student s
                  JOIN belongs_to b ON s.stud_no = b.stud_no
                  JOIN organization o ON b.org_id = o.org_id
                  WHERE b.org_id = %s
                  ORDER BY b.role, s.lastname, s.firstname"""
        
        try:
            self.db_manager.cursor.execute(query, (org_id,))
            results = self.db_manager.cursor.fetchall()
            
            if results:
                # Convert results to list of lists for tabulate
                table_data = [[
                    row['stud_no'],
                    row['full_name'],
                    row['role'],
                    row['status'],
                    row['gender'],
                    row['degrprog'],
                    row['batch_year'],
                    row['committee'],
                    row['org_name'],
                    row['semester'],
                    row['acad_year']
                ] for row in results]
                
                headers = ["Student No", "Name", "Role", "Status", "Gender", 
                          "Degree Program", "Batch Year", "Committee", 
                          "Organization", "Semester", "Academic Year"]
                print("\nOrganization Members:")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
                print(f"\nTotal members: {len(results)}")
            else:
                print("No members found in this organization!")
                
        except Exception as e:
            print(f"✗ Error viewing organization members: {e}")
