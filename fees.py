from datetime import datetime

class FeesManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def manage_fees(self):
        """Manage organization fees"""
        while True:
            print("\n=== Fee Management ===")
            print("1. Add Fee")
            print("2. Update Payment")
            print("3. View Payment Status")
            print("4. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == '1':
                self.add_fee()
            elif choice == '2':
                self.update_payment()
            elif choice == '3':
                self.view_payment_status()
            elif choice == '4':
                break

    def add_fee(self):
        """Add a new fee"""
        stud_no = input("Student Number: ")
        org_id = input("Organization ID: ")
        amount = float(input("Amount: "))
        due_date = input("Due Date (YYYY-MM-DD): ")
        
        query = """INSERT INTO payment (amount, due_date, org_id, stud_no) 
                  VALUES (%s, %s, %s, %s)"""
        
        try:
            self.db_manager.cursor.execute(query, (amount, due_date, org_id, stud_no))
            self.db_manager.connection.commit()
            print("✓ Fee added successfully!")
        except Exception as e:
            print(f"✗ Error: {e}")

    def update_payment(self):
        """Update payment status"""
        payment_id = input("Payment ID: ")
        amount_paid = float(input("Amount Paid: "))
        payment_date = datetime.now().strftime('%Y-%m-%d')
        
        query = """UPDATE payment 
                  SET amount_paid = %s, payment_date = %s, 
                      payment_status = CASE 
                          WHEN amount_paid = amount THEN 'Paid'
                          WHEN amount_paid > 0 THEN 'Partial'
                          ELSE 'Not Paid'
                      END
                  WHERE payment_id = %s"""
        
        try:
            self.db_manager.cursor.execute(query, (amount_paid, payment_date, payment_id))
            self.db_manager.connection.commit()
            print("✓ Payment updated successfully!")
        except Exception as e:
            print(f"✗ Error: {e}")

    def view_payment_status(self):
        """View payment status"""
        stud_no = input("Student Number: ")
        
        query = """SELECT p.*, o.org_name 
                  FROM payment p 
                  JOIN organization o ON p.org_id = o.org_id 
                  WHERE p.stud_no = %s"""
        
        try:
            self.db_manager.cursor.execute(query, (stud_no,))
            results = self.db_manager.cursor.fetchall()
            
            if results:
                for row in results:
                    print(f"\nOrganization: {row['org_name']}")
                    print(f"Amount: {row['amount']}")
                    print(f"Amount Paid: {row['amount_paid']}")
                    print(f"Status: {row['payment_status']}")
                    print(f"Due Date: {row['due_date']}")
            else:
                print("No payment records found.")
        except Exception as e:
            print(f"✗ Error: {e}")
