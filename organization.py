class OrganizationManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def manage_organizations(self):
        """Manage organizations"""
        while True:
            print("\n=== Organization Management ===")
            print("1. Add Organization")
            print("2. Update Organization")
            print("3. View Organization Details")
            print("4. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == '1':
                self.add_organization()
            elif choice == '2':
                self.update_organization()
            elif choice == '3':
                self.view_organization_details()
            elif choice == '4':
                break

    def add_organization(self):
        """Add a new organization"""
        org_name = input("Organization Name: ")
        year_established = input("Year Established (YYYY-MM-DD): ")
        
        query = "INSERT INTO organization (org_name, year_established) VALUES (%s, %s)"
        
        try:
            self.db_manager.cursor.execute(query, (org_name, year_established))
            self.db_manager.connection.commit()
            print("✓ Organization added successfully!")
        except Exception as e:
            print(f"✗ Error: {e}")

    def update_organization(self):
        """Update organization details"""
        org_id = input("Organization ID: ")
        new_name = input("New Organization Name: ")
        
        query = "UPDATE organization SET org_name = %s WHERE org_id = %s"
        
        try:
            self.db_manager.cursor.execute(query, (new_name, org_id))
            self.db_manager.connection.commit()
            print("✓ Organization updated successfully!")
        except Exception as e:
            print(f"✗ Error: {e}")

    def view_organization_details(self):
        """View organization details"""
        org_id = input("Organization ID: ")
        
        query = """SELECT o.*, COUNT(b.stud_no) as member_count 
                  FROM organization o 
                  LEFT JOIN belongs_to b ON o.org_id = b.org_id 
                  WHERE o.org_id = %s 
                  GROUP BY o.org_id"""
        
        try:
            self.db_manager.cursor.execute(query, (org_id,))
            result = self.db_manager.cursor.fetchone()
            
            if result:
                print(f"\nOrganization: {result['org_name']}")
                print(f"Established: {result['year_established']}")
                print(f"Total Members: {result['member_count']}")
            else:
                print("Organization not found.")
        except Exception as e:
            print(f"✗ Error: {e}")
