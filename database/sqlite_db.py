import sqlite3
import os
from config.settings import settings
from utils.logger import app_logger
from utils.exceptions import DatabaseError

class SchoolERPDatabase:
    """Manages SQLite operations for the School ERP Admission tables."""
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.SQLITE_DB_PATH
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Returns dictionaries/row objects
            return conn
        except sqlite3.Error as e:
            app_logger.error(f"Failed to connect to SQLite database at {self.db_path}: {str(e)}")
            raise DatabaseError(f"Database connection failed: {str(e)}")

    def init_db(self):
        """Creates the tables and seeds them if they are empty."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # 1. Admissions Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Admissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                process_step TEXT NOT NULL,
                description TEXT NOT NULL,
                required_documents TEXT,
                age_criteria TEXT,
                last_date TEXT,
                academic_year TEXT
            );
            """)

            # 2. FeeStructure Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS FeeStructure (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grade TEXT NOT NULL,
                admission_fee REAL,
                tuition_fee_term REAL,
                activity_fee REAL,
                caution_deposit REAL,
                frequency TEXT
            );
            """)

            # 3. Transport Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Transport (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_name TEXT NOT NULL,
                coverage_areas TEXT,
                driver_name TEXT,
                driver_phone TEXT,
                term_fee REAL,
                availability_status TEXT
            );
            """)

            # 4. Facilities Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Facilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                facility_name TEXT NOT NULL,
                category TEXT,
                description TEXT
            );
            """)

            # 5. FAQs Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS FAQs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                category TEXT
            );
            """)

            # 6. Classes Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT NOT NULL,
                stream TEXT,
                teacher_in_charge TEXT
            );
            """)

            # 7. Availability Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Availability (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT NOT NULL,
                total_seats INTEGER,
                filled_seats INTEGER,
                vacant_seats INTEGER,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 8. CampusVisits Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS CampusVisits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_name TEXT NOT NULL,
                parent_email TEXT NOT NULL,
                parent_phone TEXT,
                visit_date TEXT NOT NULL,
                visit_time TEXT NOT NULL,
                status TEXT DEFAULT 'Scheduled',
                notes TEXT
            );
            """)

            # 9. Users Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                role TEXT DEFAULT 'Parent'
            );
            """)

            # 10. Feedback Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                rating INTEGER CHECK(rating BETWEEN 1 AND 5),
                comment TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            conn.commit()
            app_logger.info("Database schema initialized successfully.")
            
            # Seed data if empty
            self._seed_sample_data(cursor, conn)
            
        except sqlite3.Error as e:
            conn.rollback()
            app_logger.error(f"Error initializing SQLite database: {str(e)}")
            raise DatabaseError(f"Database setup failed: {str(e)}")
        finally:
            conn.close()

    def _seed_sample_data(self, cursor, conn):
        # Check if table Admissions is empty
        cursor.execute("SELECT COUNT(*) FROM Admissions")
        if cursor.fetchone()[0] == 0:
            app_logger.info("Seeding sample data for School ERP Database...")
            
            # Admissions seed
            cursor.execute("""
            INSERT INTO Admissions (process_step, description, required_documents, age_criteria, last_date, academic_year) VALUES
            ('Step 1: Online Application', 'Parents submit the application form on our website with basic student details.', 'Birth Certificate, Passport Photos', 'N/A', '2026-08-15', '2026-2027'),
            ('Step 2: Document Verification', 'School admission office reviews and validates all submitted credentials.', 'Previous school transcripts/report card, Transfer Certificate (TC), Aadhaar Card', 'N/A', '2026-08-20', '2026-2027'),
            ('Step 3: Interactive Session', 'An informal interaction for kindergarten students, or an entrance evaluation test for Grade 1 and above.', 'N/A', 'Grade 1: Must be 6+ years old as of 1st June', '2026-08-25', '2026-2027'),
            ('Step 4: Fee Payment', 'Upon approval, secure the seat by paying the non-refundable registration and first term admission fees.', 'Payment receipt, Signed admission agreement', 'N/A', '2026-08-31', '2026-2027');
            """)

            # FeeStructure seed
            cursor.execute("""
            INSERT INTO FeeStructure (grade, admission_fee, tuition_fee_term, activity_fee, caution_deposit, frequency) VALUES
            ('Nursery', 5000.0, 25000.0, 3000.0, 5000.0, 'Per Term (3 Terms per year)'),
            ('Kindergarten (KG)', 5000.0, 28000.0, 3000.0, 5000.0, 'Per Term (3 Terms per year)'),
            ('Grade 1', 10000.0, 35000.0, 5000.0, 10000.0, 'Per Term (3 Terms per year)'),
            ('Grade 2', 10000.0, 35000.0, 5000.0, 10000.0, 'Per Term (3 Terms per year)'),
            ('Grade 3', 10000.0, 38000.0, 5000.0, 10000.0, 'Per Term (3 Terms per year)'),
            ('Grade 4', 10000.0, 38000.0, 5000.0, 10000.0, 'Per Term (3 Terms per year)'),
            ('Grade 5', 10000.0, 42000.0, 6000.0, 10000.0, 'Per Term (3 Terms per year)'),
            ('Grade 6', 15000.0, 48000.0, 6000.0, 10000.0, 'Per Term (3 Terms per year)'),
            ('Grade 10', 20000.0, 55000.0, 8000.0, 15000.0, 'Per Term (3 Terms per year)');
            """)

            # Transport seed
            cursor.execute("""
            INSERT INTO Transport (route_name, coverage_areas, driver_name, driver_phone, term_fee, availability_status) VALUES
            ('Route A (Downtown)', 'Central Station, City Center, North Plaza, Metro Mall', 'John Doe', '+1-555-0199', 4500.0, 'Available'),
            ('Route B (Highlands)', 'Highland Hills, Valley View, Crestwood Estates, Oakridge', 'Robert Smith', '+1-555-0188', 5500.0, 'Available'),
            ('Route C (Eastside)', 'East Gate, Riverside, Harbour View, Coastal Road', 'David Wilson', '+1-555-0177', 5000.0, 'Limited Seats'),
            ('Route D (West End)', 'West Ridge, Sunset Boulevard, Green Meadows, Airport Road', 'Michael Brown', '+1-555-0166', 6000.0, 'Full');
            """)

            # Facilities seed
            cursor.execute("""
            INSERT INTO Facilities (facility_name, category, description) VALUES
            ('Smart Classrooms', 'Infrastructure', 'All classrooms are air-conditioned, spacious, and equipped with interactive digital smartboards and audio-visual setups.'),
            ('Science Labs', 'Academic', 'State-of-the-art laboratory setups for Physics, Chemistry, and Biology to foster hands-on practical learning.'),
            ('Robotics & STEM Lab', 'Academic', 'Equipped with 3D printers, Lego Mindstorms kits, and micro-controllers to build early coding and engineering skills.'),
            ('School Library', 'Academic', 'A collection of over 20,000 physical books, journals, audiobooks, and high-speed digital research terminals.'),
            ('Sports Complex', 'Athletics', 'Features an Olympic-size swimming pool, a synthetic running track, basketball courts, and a turf soccer field.'),
            ('Medical Room', 'Health', 'A fully-equipped medical clinic with two certified, full-time pediatric nurses on campus during school hours.'),
            ('Cafeteria', 'Dining', 'Serves certified nutritious, balanced vegetarian and non-vegetarian meals prepared in a strictly hygienic, licensed kitchen.');
            """)

            # FAQs seed
            cursor.execute("""
            INSERT INTO FAQs (question, answer, category) VALUES
            ('What is the teacher-to-student ratio?', 'Our teacher-to-student ratio is 1:15 in Kindergarten and 1:24 for Grades 1 through 10, ensuring personalized guidance for every child.', 'General'),
            ('Are extracurricular activities included in the term fee?', 'Standard co-curricular activities like music, fine arts, and physical education are included. Special clubs such as Robotics, Horse Riding, and Advanced Tennis have a nominal additional club fee.', 'Extracurricular'),
            ('Does the school offer boarding or hostel facilities?', 'No, our school is currently a day school only. We do not provide hostel or residential boarding facilities.', 'Facilities'),
            ('How is safety managed on campus?', 'We have 24/7 CCTV surveillance across all corridors and gates, mandatory RFID tracking for students, and highly trained security guards stationed at all entries.', 'Safety'),
            ('Is there a sibling discount on fees?', 'Yes, we offer a 10% sibling discount on the Tuition Fee for the second/youngest child currently enrolled in the school.', 'Fees');
            """)

            # Classes seed
            cursor.execute("""
            INSERT INTO Classes (class_name, stream, teacher_in_charge) VALUES
            ('Nursery - Section A', 'General', 'Mrs. Jane Carter'),
            ('Kindergarten - Section A', 'General', 'Mrs. Emily Watson'),
            ('Grade 1 - Section A', 'General', 'Mr. Alan Turing'),
            ('Grade 5 - Section A', 'General', 'Ms. Ada Lovelace'),
            ('Grade 10 - Science Section', 'Science', 'Dr. Richard Feynman');
            """)

            # Availability seed
            cursor.execute("""
            INSERT INTO Availability (class_name, total_seats, filled_seats, vacant_seats) VALUES
            ('Nursery', 40, 32, 8),
            ('Kindergarten (KG)', 50, 48, 2),
            ('Grade 1', 60, 52, 8),
            ('Grade 2', 60, 55, 5),
            ('Grade 3', 60, 58, 2),
            ('Grade 4', 60, 59, 1),
            ('Grade 5', 60, 45, 15),
            ('Grade 6', 60, 57, 3),
            ('Grade 10', 50, 49, 1);
            """)

            # Users seed
            cursor.execute("""
            INSERT INTO Users (username, email, role) VALUES
            ('admin_user', 'admin@greenwoodschool.edu', 'Administrator'),
            ('parent_test', 'parent@example.com', 'Parent');
            """)

            # Feedback seed
            cursor.execute("""
            INSERT INTO Feedback (user_email, rating, comment) VALUES
            ('parent1@example.com', 5, 'The chatbot was extremely quick to respond about the age criteria and term fees! Excellent tool.'),
            ('parent2@example.com', 4, 'Very helpful, but would love to also schedule visits directly from the app.');
            """)

            conn.commit()
            app_logger.info("Sample ERP database seeded successfully.")

    def query(self, sql: str, params: tuple = ()) -> list:
        """Executes a SELECT query and returns rows as dictionaries."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            app_logger.error(f"SQL execution error for: {sql}. Error: {str(e)}")
            raise DatabaseError(f"Query execution failed: {str(e)}")
        finally:
            conn.close()

    def execute(self, sql: str, params: tuple = ()) -> int:
        """Executes an INSERT, UPDATE, or DELETE query and returns the last row ID or affected row count."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            conn.commit()
            last_id = cursor.lastrowid
            affected = cursor.rowcount
            return last_id if last_id else affected
        except sqlite3.Error as e:
            conn.rollback()
            app_logger.error(f"SQL execution error for: {sql}. Error: {str(e)}")
            raise DatabaseError(f"Database write execution failed: {str(e)}")
        finally:
            conn.close()
            
    def get_all_admission_data_as_text(self) -> str:
        """Retrieves and concatenates all database information into structured context paragraphs for RAG grounding."""
        text_blocks = []
        
        # Admissions
        admissions = self.query("SELECT * FROM Admissions")
        text_blocks.append("--- SCHOOL ADMISSION PROCESS ---")
        for step in admissions:
            text_blocks.append(
                f"Step/Step Name: {step['process_step']}\n"
                f"Description: {step['description']}\n"
                f"Required Documents: {step['required_documents']}\n"
                f"Age Criteria: {step['age_criteria']}\n"
                f"Last Date to Apply: {step['last_date']}\n"
                f"Academic Year: {step['academic_year']}\n"
            )
            
        # Fees
        fees = self.query("SELECT * FROM FeeStructure")
        text_blocks.append("--- SCHOOL FEE STRUCTURE ---")
        for fee in fees:
            text_blocks.append(
                f"Grade: {fee['grade']}\n"
                f"Admission/Registration Fee: {fee['admission_fee']} USD (One-time, non-refundable)\n"
                f"Tuition Fee: {fee['tuition_fee_term']} USD per term\n"
                f"Activity Fee: {fee['activity_fee']} USD per term\n"
                f"Caution Deposit: {fee['caution_deposit']} USD (Refundable)\n"
                f"Payment Frequency: {fee['frequency']} (There are 3 terms per year)\n"
            )
            
        # Transport
        routes = self.query("SELECT * FROM Transport")
        text_blocks.append("--- SCHOOL TRANSPORT AND BUS ROUTES ---")
        for route in routes:
            text_blocks.append(
                f"Bus Route: {route['route_name']}\n"
                f"Coverage Areas: {route['coverage_areas']}\n"
                f"Driver Name: {route['driver_name']}\n"
                f"Driver Contact: {route['driver_phone']}\n"
                f"Term Bus Fee: {route['term_fee']} USD per term\n"
                f"Availability Status: {route['availability_status']}\n"
            )
            
        # Facilities
        facilities = self.query("SELECT * FROM Facilities")
        text_blocks.append("--- SCHOOL INFRASTRUCTURE AND FACILITIES ---")
        for f in facilities:
            text_blocks.append(
                f"Facility: {f['facility_name']} ({f['category']})\n"
                f"Details: {f['description']}\n"
            )
            
        # FAQs
        faqs = self.query("SELECT * FROM FAQs")
        text_blocks.append("--- FREQUENTLY ASKED QUESTIONS (FAQs) ---")
        for faq in faqs:
            text_blocks.append(
                f"Question: {faq['question']}\n"
                f"Answer: {faq['answer']}\n"
                f"Category: {faq['category']}\n"
            )
            
        # Seat Availability
        avail = self.query("SELECT * FROM Availability")
        text_blocks.append("--- GRADE SEAT AVAILABILITY ---")
        for av in avail:
            text_blocks.append(
                f"Grade/Class: {av['class_name']}\n"
                f"Total Intended Seats: {av['total_seats']}\n"
                f"Filled/Registered Seats: {av['filled_seats']}\n"
                f"Vacant/Open Seats Available: {av['vacant_seats']}\n"
            )
            
        return "\n".join(text_blocks)
