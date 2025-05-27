-- Merged SQL Setup: CMSC 127 PROJECT + TRIGGERS

-- Create user and database
CREATE OR REPLACE USER 'admin' IDENTIFIED BY 'admin';
CREATE OR REPLACE USER 'emman' IDENTIFIED BY 'emman';
CREATE OR REPLACE USER 'angelica' IDENTIFIED BY 'angelica';
CREATE OR REPLACE USER 'jerome' IDENTIFIED BY 'jerome';

DROP DATABASE IF EXISTS studentorg;
CREATE DATABASE IF NOT EXISTS studentorg;
USE studentorg;

GRANT ALL ON studentorg.* TO 'admin';
GRANT SELECT, INSERT, UPDATE, DELETE ON studentorg.* TO 'emman';
GRANT SELECT, INSERT, UPDATE, DELETE ON studentorg.* TO 'angelica';
GRANT SELECT, INSERT, UPDATE, DELETE ON studentorg.* TO 'jerome';

-- Disable foreign key checks temporarily
SET FOREIGN_KEY_CHECKS=0;

-- Drop existing tables if they exist
DROP TABLE IF EXISTS payment;
DROP TABLE IF EXISTS belongs_to;
DROP TABLE IF EXISTS organization;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS studentorg_log;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS=1;

-- Table Definitions
CREATE TABLE IF NOT EXISTS student (
    stud_no VARCHAR(10) PRIMARY KEY,
    firstname VARCHAR(50) NOT NULL,
    lastname VARCHAR(50) NOT NULL,
    degrprog VARCHAR(50),
    batch INT(4) NOT NULL,
    gender VARCHAR(1) NOT NULL,
    birthday DATE
);

CREATE TABLE IF NOT EXISTS organization (
    org_id INT(10) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    org_name VARCHAR(50) NOT NULL,
    year_established DATE NOT NULL
) AUTO_INCREMENT = 1001;

CREATE TABLE IF NOT EXISTS payment (
    payment_id INT(5) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    amount_paid DECIMAL(11,2),
    payment_date DATE DEFAULT NULL,
    payment_status VARCHAR(30) DEFAULT 'Not Paid',
    amount DECIMAL(11,2),
    due_date DATE NOT NULL,
    org_id INT(10) NOT NULL,
    stud_no VARCHAR(10) NOT NULL,
    CONSTRAINT organization_orgid_fk FOREIGN KEY (org_id) REFERENCES organization(org_id),
    CONSTRAINT student_studno_fk FOREIGN KEY (stud_no) REFERENCES student(stud_no)
) AUTO_INCREMENT = 1001;

CREATE TABLE IF NOT EXISTS belongs_to (
    stud_no VARCHAR(10),
    org_id INT(10),
    semester VARCHAR(1),
    acad_year VARCHAR(9),
    status VARCHAR(50),
    role VARCHAR(50),
    committee VARCHAR(50),
    batch_year INT(4),
    PRIMARY KEY(stud_no, org_id, semester, acad_year),
    CONSTRAINT belongs_studno_fk FOREIGN KEY(stud_no) REFERENCES student(stud_no),
    CONSTRAINT belongs_orgid_fk FOREIGN KEY(org_id) REFERENCES organization(org_id)
);

-- Log Table
CREATE TABLE IF NOT EXISTS studentorg_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_identifier VARCHAR(255),
    change_type VARCHAR(10) NOT NULL,
    change_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Triggers

DELIMITER //

-- Triggers for student
CREATE TRIGGER student_insert AFTER INSERT ON student
FOR EACH ROW BEGIN
    INSERT INTO studentorg_log (table_name, record_identifier, change_type)
    VALUES ('student', NEW.stud_no, 'INSERT');
END;
//

CREATE TRIGGER student_update AFTER UPDATE ON student
FOR EACH ROW BEGIN
    INSERT INTO studentorg_log (table_name, record_identifier, change_type)
    VALUES ('student', NEW.stud_no, 'UPDATE');
END;
//

CREATE TRIGGER student_delete AFTER DELETE ON student
FOR EACH ROW BEGIN
    INSERT INTO studentorg_log (table_name, record_identifier, change_type)
    VALUES ('student', OLD.stud_no, 'DELETE');
END;
//

-- Triggers for organization
CREATE TRIGGER organization_insert AFTER INSERT ON organization
FOR EACH ROW BEGIN
    INSERT INTO studentorg_log (table_name, record_identifier, change_type)
    VALUES ('organization', NEW.org_id, 'INSERT');
END;
//

CREATE TRIGGER organization_update AFTER UPDATE ON organization
FOR EACH ROW BEGIN
    INSERT INTO studentorg_log (table_name, record_identifier, change_type)
    VALUES ('organization', NEW.org_id, 'UPDATE');
END;
//

CREATE TRIGGER organization_delete AFTER DELETE ON organization
FOR EACH ROW BEGIN
    INSERT INTO studentorg_log (table_name, record_identifier, change_type)
    VALUES ('organization', OLD.org_id, 'DELETE');
END;
//

-- Triggers for payment
CREATE TRIGGER payment_insert AFTER INSERT ON payment
FOR EACH ROW BEGIN
    INSERT INTO studentorg_log (table_name, record_identifier, change_type)
    VALUES ('payment', NEW.payment_id, 'INSERT');
END;
//

CREATE TRIGGER payment_update AFTER UPDATE ON payment
FOR EACH ROW BEGIN
    INSERT INTO studentorg_log (table_name, record_identifier, change_type)
    VALUES ('payment', NEW.payment_id, 'UPDATE');
END;
//

CREATE TRIGGER payment_delete AFTER DELETE ON payment
FOR EACH ROW BEGIN
    INSERT INTO studentorg_log (table_name, record_identifier, change_type)
    VALUES ('payment', OLD.payment_id, 'DELETE');
END;
//

-- Triggers for belongs_to
CREATE TRIGGER belongs_to_insert AFTER INSERT ON belongs_to
FOR EACH ROW BEGIN
    INSERT INTO studentorg_log (table_name, record_identifier, change_type)
    VALUES ('belongs_to', CONCAT(NEW.stud_no, '-', NEW.org_id, '-', NEW.semester, '-', NEW.acad_year), 'INSERT');
END;
//

CREATE TRIGGER belongs_to_update AFTER UPDATE ON belongs_to
FOR EACH ROW BEGIN
    INSERT INTO studentorg_log (table_name, record_identifier, change_type)
    VALUES ('belongs_to', CONCAT(NEW.stud_no, '-', NEW.org_id, '-', NEW.semester, '-', NEW.acad_year), 'UPDATE');
END;
//

CREATE TRIGGER belongs_to_delete AFTER DELETE ON belongs_to
FOR EACH ROW BEGIN
    INSERT INTO studentorg_log (table_name, record_identifier, change_type)
    VALUES ('belongs_to', CONCAT(OLD.stud_no, '-', OLD.org_id, '-', OLD.semester, '-', OLD.acad_year), 'DELETE');
END;
//

DELIMITER ;

-- Helper Functions

DELIMITER //

CREATE FUNCTION GetSemesterEndDate (
    p_batch_year YEAR,
    p_semester TINYINT
)
RETURNS DATE
DETERMINISTIC
BEGIN
    DECLARE end_date DATE;
    CASE p_semester
        WHEN 1 THEN SET end_date = DATE(CONCAT(p_batch_year, '-12-31'));
        WHEN 2 THEN SET end_date = DATE(CONCAT(p_batch_year + 1, '-05-31'));
        ELSE SET end_date = NULL; 
    END CASE;
    RETURN end_date;
END //

DELIMITER ;

-- Stored Procedures for Reports

DELIMITER //

-- Report 1: View all members of the organization by role, status, gender, degree program, batch
DROP PROCEDURE IF EXISTS GetOrgMembersByRole;
CREATE PROCEDURE GetOrgMembersByRole (
    IN p_org_id INT
)
BEGIN
    SELECT
        s.stud_no,
        CONCAT(s.firstname, ' ', s.lastname) AS full_name,
        b.role,
        b.status,
        s.gender,
        s.degrprog,
        b.batch_year,
        b.committee,
        o.org_name,
        b.semester,
        b.acad_year
    FROM belongs_to b
    JOIN student s ON b.stud_no = s.stud_no
    JOIN organization o ON b.org_id = o.org_id
    WHERE b.org_id = p_org_id
    ORDER BY b.role, s.gender, b.committee;
END //

-- Report 2: View members with unpaid fees
DROP PROCEDURE IF EXISTS GetOrgMembersWithUnpaidFees;
CREATE PROCEDURE GetOrgMembersWithUnpaidFees (
    IN p_org_id INT,
    IN p_semester TINYINT,
    IN p_batch_year YEAR
)
BEGIN
    SELECT 
        s.stud_no,
        CONCAT(s.firstname, ' ', s.lastname) AS name,
        p.payment_status,
        b.semester,
        b.acad_year,
        o.org_name
    FROM payment p
    JOIN student s ON s.stud_no = p.stud_no
    JOIN organization o ON o.org_id = p.org_id
    JOIN belongs_to b ON b.stud_no = p.stud_no AND b.org_id = p.org_id
    WHERE p.payment_status = 'Unpaid'
      AND b.semester = p_semester
      AND b.acad_year = p_batch_year
      AND o.org_id = p_org_id;
END //

-- Report 3: View member's unpaid fees
DROP PROCEDURE IF EXISTS GetMemberUnpaidFees;
CREATE PROCEDURE GetMemberUnpaidFees (
    IN p_stud_no VARCHAR(10)
)
BEGIN
    SELECT
        s.stud_no,
        CONCAT(s.firstname, ' ', s.lastname) AS name,
        o.org_name,
        b.acad_year,
        b.semester,
        p.payment_status,
        p.due_date
    FROM payment p
    JOIN student s ON p.stud_no = s.stud_no
    JOIN organization o ON p.org_id = o.org_id
    JOIN belongs_to b ON b.stud_no = s.stud_no AND b.org_id = o.org_id
    WHERE p.payment_status = 'Unpaid'
      AND s.stud_no = p_stud_no;
END //

-- Report 4: View executive committee members
DROP PROCEDURE IF EXISTS GetExecutiveCommitteeMembers;
CREATE PROCEDURE GetExecutiveCommitteeMembers (
    IN p_org_id INT,
    IN p_acad_year VARCHAR(9)
)
BEGIN
    SELECT
        s.stud_no,
        CONCAT(s.firstname, ' ', s.lastname) AS name,
        b.acad_year,
        b.semester,
        b.committee,
        o.org_name
    FROM belongs_to b
    JOIN student s ON b.stud_no = s.stud_no
    JOIN organization o ON b.org_id = o.org_id
    WHERE b.committee = 'Executive'
      AND b.acad_year = p_acad_year
      AND o.org_id = p_org_id;
END //

-- Report 5: View organization role history
DROP PROCEDURE IF EXISTS GetOrgRoleHistory;
CREATE PROCEDURE GetOrgRoleHistory (
    IN p_org_id INT,
    IN p_role VARCHAR(50)
)
BEGIN
    SELECT
        s.stud_no,
        CONCAT(s.firstname, ' ', s.lastname) AS name,
        b.role,
        b.acad_year,
        b.semester,
        o.org_name
    FROM belongs_to b
    JOIN student s ON b.stud_no = s.stud_no
    JOIN organization o ON b.org_id = o.org_id
    WHERE b.role = p_role
      AND o.org_id = p_org_id
    ORDER BY b.acad_year DESC, b.semester DESC;
END //

-- Report 6: View late payments
DROP PROCEDURE IF EXISTS GetOrgLatePaymentsBySemester;
CREATE PROCEDURE GetOrgLatePaymentsBySemester (
    IN p_org_id INT,
    IN p_semester TINYINT,
    IN p_batch_year YEAR
)
BEGIN
    SELECT
        s.stud_no,
        CONCAT(s.firstname, ' ', s.lastname) AS name,
        (p.amount - p.amount_paid) AS `Late Payment`,
        CONCAT(b.acad_year, ' --- ', b.semester, ' sem') AS `AY-SEM`,
        o.org_name
    FROM payment p
    JOIN student s ON p.stud_no = s.stud_no
    JOIN organization o ON p.org_id = o.org_id
    JOIN belongs_to b ON b.stud_no = p.stud_no AND b.org_id = p.org_id AND b.semester = p_semester AND b.acad_year = p_batch_year
    WHERE p.payment_status = 'Partial'
      AND o.org_id = p_org_id
    ORDER BY b.acad_year DESC, b.semester DESC;
END //

-- Report 7: View membership activity percentage
DROP PROCEDURE IF EXISTS GetOrgMembershipActivityPercentage;
CREATE PROCEDURE GetOrgMembershipActivityPercentage (
    IN p_org_id INT,
    IN p_num_semesters INT
)
BEGIN
    SELECT
        (SUM(status = 'Active') / COUNT(*)) * 100 AS "Percentage of active members",
        (SUM(status IN ('Inactive', 'Alumni')) / COUNT(*)) * 100 AS "Percentage of inactive/alumni members",
        acad_year,
        semester
    FROM belongs_to
    WHERE org_id = p_org_id
    GROUP BY acad_year, semester
    ORDER BY acad_year DESC, semester DESC
    LIMIT p_num_semesters;
END //

-- Report 8: View alumni records
DROP PROCEDURE IF EXISTS GetOrgAlumniMembers;
CREATE PROCEDURE GetOrgAlumniMembers (
    IN p_org_id INT,
    IN p_as_of_date DATE
)
BEGIN
    SELECT
        s.stud_no,
        CONCAT(s.firstname, ' ', s.lastname) AS name,
        CONCAT(b.role, ', ', b.committee, ', ', b.semester, ' sem') AS 'Alumni Record',
        o.org_name
    FROM belongs_to b
    JOIN student s ON b.stud_no = s.stud_no
    JOIN organization o ON b.org_id = o.org_id
    WHERE b.status = 'Alumni'
      AND b.org_id = p_org_id
      AND STR_TO_DATE(CONCAT(SUBSTRING_INDEX(b.acad_year, '-', 1), '-', IF(b.semester = '1', '06-01', '11-30')), '%Y-%m-%d') <= p_as_of_date
    ORDER BY b.acad_year DESC, b.semester DESC;
END //

-- Report 9: View total fees
DROP PROCEDURE IF EXISTS GetOrgFeeTotalsAsOfDate;
CREATE PROCEDURE GetOrgFeeTotalsAsOfDate (
    IN p_org_id INT,
    IN p_as_of_date DATE
)
BEGIN
    SELECT
        o.org_name,
        p.due_date,
        SUM(CASE
            WHEN p.payment_status = 'Paid' THEN p.amount_paid
            WHEN p.payment_status = 'Partial' THEN p.amount_paid
            ELSE 0
        END) AS total_paid_fees,
        SUM(CASE
            WHEN p.payment_status = 'Unpaid' THEN p.amount
            WHEN p.payment_status = 'Partial' THEN (p.amount - p.amount_paid)
            ELSE 0
        END) AS total_unpaid_fees
    FROM payment p
    JOIN organization o ON o.org_id = p.org_id
    WHERE p.org_id = p_org_id
    GROUP BY o.org_name;
END //

-- Report 10: View members with highest debt
DROP PROCEDURE IF EXISTS GetOrgMembersWithHighestDebt;
CREATE PROCEDURE GetOrgMembersWithHighestDebt (
    IN p_org_id INT,
    IN p_semester TINYINT,
    IN p_batch_year YEAR
)
BEGIN
    SELECT
        s.stud_no,
        CONCAT(s.firstname, ' ', s.lastname) AS full_name,
        b.acad_year,
        b.semester,
        p.amount - p.amount_paid AS total_debt,
        o.org_name
    FROM payment p
    JOIN student s ON p.stud_no = s.stud_no
    JOIN organization o ON p.org_id = o.org_id
    JOIN belongs_to b ON p.stud_no = b.stud_no AND p.org_id = b.org_id
    WHERE p.payment_status != 'Paid'
      AND b.acad_year = p_batch_year
      AND b.semester = p_semester
      AND p.org_id = p_org_id
    ORDER BY total_debt DESC;
END //

DELIMITER ; 