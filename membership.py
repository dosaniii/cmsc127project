from datetime import datetime
from tabulate import tabulate
from mysql.connector import Error

class MembershipManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def manage_membership(self):
        """Manage organization memberships"""
        while True:
            print("\n=== Manage Organization Membership ===")
            print("1. Add new member")
            print("2. Add member to organization")
            print("3. Update member role/status")
            print("4. Remove member from organization")
            print("5. View organization members")
            print("6. Search members")
            print("7. Back to main menu")
            
            choice = input("Choose option: ")
            
            if choice == '1':
                self.add_new_member()
            elif choice == '2':
                self.add_member_to_org()
            elif choice == '3':
                self.update_member_role()
            elif choice == '4':
                self.remove_member_from_org()
            elif choice == '5':
                self.view_org_members()
            elif choice == '6':
                self.search_members()
            elif choice == '7':
                break
            else:
                print("Invalid choice!")

    def add_new_member(self):
        """Add a new member to the system"""
        print("\n=== Add New Member ===")
        try:
            stud_no = input("Student Number: ")
            firstname = input("First Name: ")
            lastname = input("Last Name: ")
            degrprog = input("Degree Program: ")
            batch = int(input("Batch Year: "))
            gender = input("Gender (M/F): ").upper()
            birthday = input("Birthday (YYYY-MM-DD): ")
            
            query = """INSERT INTO student (stud_no, firstname, lastname, degrprog, batch, gender, birthday) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            values = (stud_no, firstname, lastname, degrprog, batch, gender, birthday)
            
            self.db_manager.cursor.execute(query, values)
            self.db_manager.connection.commit()
            print(f"✓ Member added successfully!")
            
            # Ask if they want to add this member to an organization
            add_to_org = input("\nWould you like to add this member to an organization? (yes/no): ")
            if add_to_org.lower() == 'yes':
                self.add_member_to_org(stud_no)
            
        except ValueError:
            print("✗ Invalid input. Please enter valid values.")
        except Error as e:
            print(f"✗ Error adding new member: {e}")

    def add_member_to_org(self, stud_no: str | None = None):
        """Add a member to an organization"""
        try:
            if stud_no is None:
                # show existing members
                print("\nExisting Members:")
                self.db_manager.cursor.execute("SELECT stud_no, firstname, lastname FROM student ORDER BY stud_no")
                members = self.db_manager.cursor.fetchall()
                
                if not members:
                    print("✗ No members found! Please add a member first.")
                    return
                
                print(tabulate(members, headers=["Student No", "First Name", "Last Name"], tablefmt="grid"))
                stud_no = input("\nEnter Student Number: ")
            
            # check if member exists
            self.db_manager.cursor.execute("SELECT firstname, lastname FROM student WHERE stud_no = %s", (stud_no,))
            member = self.db_manager.cursor.fetchone()
            
            if not member:
                print("✗ Member not found! Please add the member first.")
                return
            
            # Show available organizations
            self.db_manager.cursor.execute("SELECT org_id, org_name FROM organization")
            orgs = self.db_manager.cursor.fetchall()
            
            if not orgs:
                print("✗ No organizations available! Please add an organization first.")
                return
            
            print("\nAvailable Organizations:")
            print(tabulate(orgs, headers=["ID", "Name"], tablefmt="grid"))
            
            org_id = int(input("\nEnter Organization ID: "))
            
            # check if organization exists
            self.db_manager.cursor.execute("SELECT org_name FROM organization WHERE org_id = %s", (org_id,))
            org = self.db_manager.cursor.fetchone()
            
            if not org:
                print("✗ Organization not found!")
                return
            
            # check if member is already in this organization for the same semester and academic year
            semester = input("Semester (1 or 2): ")
            acad_year = input("Academic Year (YYYY-YYYY): ")
            
            self.db_manager.cursor.execute("""SELECT stud_no FROM belongs_to 
                                            WHERE stud_no = %s AND org_id = %s 
                                            AND semester = %s AND acad_year = %s""",
                                         (stud_no, org_id, semester, acad_year))
            existing = self.db_manager.cursor.fetchone()
            
            if existing:
                print("✗ Member is already in this organization for the specified semester and academic year!")
                return
            
            committee = input("Committee (optional): ") or None
            role = input("Role (e.g., Member, Secretary, President): ")
            status = input("Status (Active/Inactive/Alumni): ").strip()
            batch_year = int(input("Batch Year: "))
            
            query = """INSERT INTO belongs_to (stud_no, org_id, semester, acad_year, 
                      status, role, committee, batch_year) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            values = (stud_no, org_id, semester, acad_year, status, role, committee, batch_year)
            
            self.db_manager.cursor.execute(query, values)
            self.db_manager.connection.commit()
            print(f"✓ Member {member[0]} {member[1]} added to {org[0]} successfully!")
            
        except ValueError:
            print("✗ Invalid input. Please enter valid values.")
        except Error as e:
            print(f"✗ Error adding member to organization: {e}")

    def update_member_role(self):
        """Update member's role or status in an organization"""
        try:
            # show existing members
            print("\nExisting Members:")
            self.db_manager.cursor.execute("SELECT stud_no, firstname, lastname FROM student ORDER BY stud_no")
            members = self.db_manager.cursor.fetchall()
            
            if not members:
                print("✗ No members found!")
                return
            
            print(tabulate(members, headers=["Student No", "First Name", "Last Name"], tablefmt="grid"))
            stud_no = input("\nEnter Student Number: ")
            
            # show available organizations
            print("\nAvailable Organizations:")
            self.db_manager.cursor.execute("SELECT org_id, org_name FROM organization")
            orgs = self.db_manager.cursor.fetchall()
            
            if not orgs:
                print("✗ No organizations available!")
                return
            
            print(tabulate(orgs, headers=["ID", "Name"], tablefmt="grid"))
            org_id = int(input("\nEnter Organization ID: "))
            
            semester = input("Semester: ")
            acad_year = input("Academic Year (YYYY-YYYY): ")
            
            # check if membership exists
            query = """SELECT b.role, b.status, s.firstname, s.lastname, o.org_name 
                      FROM belongs_to b
                      JOIN student s ON b.stud_no = s.stud_no
                      JOIN organization o ON b.org_id = o.org_id
                      WHERE b.stud_no = %s AND b.org_id = %s 
                      AND b.semester = %s AND b.acad_year = %s"""
            self.db_manager.cursor.execute(query, (stud_no, org_id, semester, acad_year))
            result = self.db_manager.cursor.fetchone()
            
            if not result:
                print("✗ Membership record not found!")
                return
            
            print(f"\nCurrent membership details for {result[2]} {result[3]} in {result[4]}:")
            print(f"Current role: {result[0]}")
            print(f"Current status: {result[1]}")
            
            new_role = input("New role (press Enter to keep current): ") or result[0]
            new_status = input("New status (Active/Inactive/Alumni): ").strip()
            
            update_query = """UPDATE belongs_to SET role = %s, status = %s 
                             WHERE stud_no = %s AND org_id = %s 
                             AND semester = %s AND acad_year = %s"""
            self.db_manager.cursor.execute(update_query, 
                                         (new_role, new_status, stud_no, org_id, semester, acad_year))
            self.db_manager.connection.commit()
            print("✓ Member role/status updated successfully!")
            
        except ValueError:
            print("✗ Invalid input.")
        except Error as e:
            print(f"✗ Error updating member role: {e}")

    def remove_member_from_org(self):
        """Remove a member from an organization"""
        try:
            # show existing members
            print("\nExisting Members:")
            self.db_manager.cursor.execute("SELECT stud_no, firstname, lastname FROM student ORDER BY stud_no")
            members = self.db_manager.cursor.fetchall()
            
            if not members:
                print("✗ No members found!")
                return
            
            print(tabulate(members, headers=["Student No", "First Name", "Last Name"], tablefmt="grid"))
            stud_no = input("\nEnter Student Number: ")
            
            # show available organizations
            print("\nAvailable Organizations:")
            self.db_manager.cursor.execute("SELECT org_id, org_name FROM organization")
            orgs = self.db_manager.cursor.fetchall()
            
            if not orgs:
                print("✗ No organizations available!")
                return
            
            print(tabulate(orgs, headers=["ID", "Name"], tablefmt="grid"))
            org_id = int(input("\nEnter Organization ID: "))
            
            semester = input("Semester: ")
            acad_year = input("Academic Year (YYYY-YYYY): ")
            
            # Check if membership exists and get details
            query = """SELECT s.firstname, s.lastname, o.org_name 
                      FROM belongs_to b
                      JOIN student s ON b.stud_no = s.stud_no
                      JOIN organization o ON b.org_id = o.org_id
                      WHERE b.stud_no = %s AND b.org_id = %s 
                      AND b.semester = %s AND b.acad_year = %s"""
            self.db_manager.cursor.execute(query, (stud_no, org_id, semester, acad_year))
            result = self.db_manager.cursor.fetchone()
            
            if not result:
                print("✗ Membership record not found!")
                return
            
            confirm = input(f"Are you sure you want to remove {result[0]} {result[1]} from {result[2]}? (yes/no): ")
            if confirm.lower() == 'yes':
                delete_query = """DELETE FROM belongs_to 
                                WHERE stud_no = %s AND org_id = %s 
                                AND semester = %s AND acad_year = %s"""
                self.db_manager.cursor.execute(delete_query, (stud_no, org_id, semester, acad_year))
                self.db_manager.connection.commit()
                print("✓ Member removed from organization successfully!")
            else:
                print("Remove operation cancelled.")
                
        except ValueError:
            print("✗ Invalid input.")
        except Error as e:
            print(f"✗ Error removing member from organization: {e}")

    def view_org_members(self):
        """View all members of an organization"""
        try:
            # show available organizations
            self.db_manager.cursor.execute("SELECT org_id, org_name FROM organization")
            orgs = self.db_manager.cursor.fetchall()
            
            if not orgs:
                print("✗ No organizations available!")
                return
            
            print("\nAvailable Organizations:")
            print(tabulate(orgs, headers=["ID", "Name"], tablefmt="grid"))
            
            org_id = int(input("\nEnter Organization ID: "))
            
            # check if organization exists
            self.db_manager.cursor.execute("SELECT org_name FROM organization WHERE org_id = %s", (org_id,))
            org = self.db_manager.cursor.fetchone()
            
            if not org:
                print("✗ Organization not found!")
                return
            
            query = """SELECT s.stud_no, s.firstname, s.lastname, b.role, b.status, 
                             b.committee, b.batch_year, b.semester, b.acad_year
                      FROM student s
                      JOIN belongs_to b ON s.stud_no = b.stud_no
                      WHERE b.org_id = %s
                      ORDER BY b.acad_year DESC, b.semester DESC"""
            
            self.db_manager.cursor.execute(query, (org_id,))
            results = self.db_manager.cursor.fetchall()
            
            if results:
                headers = ["Student No", "First Name", "Last Name", "Role", "Status", 
                          "Committee", "Batch Year", "Semester", "Academic Year"]
                print(f"\nMembers of {org[0]}:")
                print(tabulate(results, headers=headers, tablefmt="grid"))
            else:
                print(f"No members found for {org[0]}!")
                
        except ValueError:
            print("✗ Invalid organization ID.")
        except Error as e:
            print(f"✗ Error viewing organization members: {e}")

    def search_members(self):
        """Search for members"""
        print("\n=== Search Members ===")
        print("1. Search by name")
        print("2. Search by student number")
        print("3. Search by degree program")
        print("4. View all members")
        print("5. Back to main menu")
        
        choice = input("Choose search option: ")
        
        if choice == '5':
            return
        
        try:
            if choice == '1':
                name = input("Enter name (partial match allowed): ")
                query = "SELECT * FROM student WHERE firstname LIKE %s OR lastname LIKE %s"
                self.db_manager.cursor.execute(query, (f"%{name}%", f"%{name}%"))
            elif choice == '2':
                stud_no = input("Enter student number: ")
                query = "SELECT * FROM student WHERE stud_no = %s"
                self.db_manager.cursor.execute(query, (stud_no,))
            elif choice == '3':
                degrprog = input("Enter degree program: ")
                query = "SELECT * FROM student WHERE degrprog LIKE %s"
                self.db_manager.cursor.execute(query, (f"%{degrprog}%",))
            elif choice == '4':
                query = "SELECT * FROM student"
                self.db_manager.cursor.execute(query)
            else:
                print("Invalid choice!")
                return
            
            results = self.db_manager.cursor.fetchall()
            
            if results:
                headers = ["Student No", "First Name", "Last Name", "Degree Program", 
                          "Batch", "Gender", "Birthday"]
                print("\nSearch Results:")
                print(tabulate(results, headers=headers, tablefmt="grid"))
            else:
                print("No members found!")
                
        except ValueError:
            print("✗ Invalid input.")
        except Error as e:
            print(f"✗ Error searching members: {e}")
