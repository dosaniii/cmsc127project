# Student Organization Management System (SOMS)

## Setup Instructions

### 1. Database Setup

1. Install MariaDB/MySQL if not already installed
2. Open MySQL command line as root:
   ```bash
   mysql -u root -p
   ```
3. Run these commands:
   ```sql
   CREATE DATABASE IF NOT EXISTS studentorg;
   CREATE USER 'admin' IDENTIFIED BY 'admin';
   GRANT ALL PRIVILEGES ON studentorg.* TO 'admin';
   FLUSH PRIVILEGES;
   exit;
   ```
4. Import the database schema:
   ```bash
   mysql -u admin -p studentorg < SOMS.sql
   ```
   Password: admin

### 2. Python Setup

1. Install Python 3.x if not already installed
2. Install required packages:
   ```bash
   pip install mysql-connector-python
   ```

### 3. Running the Application

1. Make sure MariaDB/MySQL is running
2. Run the main application:
   ```bash
   python main.py
   ```

## File Structure

- `SOMS.sql` - Database schema and initial data
- `database.py` - Database connection management
- `data_management.py` - Data operations
- `main.py` - Main application file

## Database Credentials

- Database: studentorg
- Username: admin
- Password: admin
- Host: localhost
- Port: 3306

## Troubleshooting

If you encounter any issues:

1. Make sure MariaDB/MySQL is running
2. Verify database credentials in database.py
3. Check if all required Python packages are installed
4. Ensure you have proper permissions to access the database
