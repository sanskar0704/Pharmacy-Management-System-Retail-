import sqlite3


def create_tables() -> None:
	"""
	Create database tables for the pharmacy management system.
	This script is intended to be run once to initialize pharmacy.db.
	"""

	connection = sqlite3.connect("pharmacy.db")
	cursor = connection.cursor()
	try:
		# Enable foreign keys for referential integrity
		cursor.execute("PRAGMA foreign_keys = ON;")

		# Create medicines table (add image_path column)
		cursor.execute(
			"""
			CREATE TABLE IF NOT EXISTS medicines (
				id INTEGER PRIMARY KEY,
				name TEXT NOT NULL,
				manufacturer TEXT,
				batch_no TEXT,
				expiry_date TEXT,
				quantity INTEGER NOT NULL DEFAULT 0,
				price REAL NOT NULL DEFAULT 0,
				image_path TEXT
			);
			"""
		)
		# Add image_path column if missing (for existing DBs)
		cols = cursor.execute("PRAGMA table_info(medicines)").fetchall()
		col_names = {c[1] for c in cols}
		if "image_path" not in col_names:
			cursor.execute("ALTER TABLE medicines ADD COLUMN image_path TEXT")

		# Seed sample medicines if none exist
		med_count = cursor.execute("SELECT COUNT(*) FROM medicines").fetchone()[0]
		if not med_count:
			medicines = [
				("Paracetamol 500mg", "Mankind", "BCH1001", "2026-12-31", 100, 12.5),
				("Cetrizine 10mg", "Mankind", "BCH1002", "2027-05-30", 50, 8.0),
				("Amoxicillin 250mg", "Mankind", "BCH1003", "2026-09-15", 75, 22.0),
				("Azithromycin 500mg", "Pfizer", "BCH2001", "2027-01-20", 60, 35.0),
				("Ibuprofen 400mg", "Cipla", "BCH2002", "2026-11-10", 80, 10.0),
				("Metformin 500mg", "Sun Pharma", "BCH2003", "2027-03-05", 90, 18.0),
				("Amlodipine 5mg", "Dr. Reddy's", "BCH2004", "2026-10-15", 70, 14.0),
				("Atorvastatin 10mg", "Zydus", "BCH2005", "2027-06-30", 65, 22.0),
				("Pantoprazole 40mg", "Alkem", "BCH2006", "2026-12-01", 85, 16.0),
				("Cetirizine 5mg", "Glenmark", "BCH2007", "2027-04-25", 55, 7.5),
			]
			for med in medicines:
				cursor.execute(
					"INSERT INTO medicines (name, manufacturer, batch_no, expiry_date, quantity, price) VALUES (?, ?, ?, ?, ?, ?)",
					med
				)
			print("Seeded 10 sample medicines.")

		connection.commit()
		# Create sales table
		cursor.execute(
			"""
			CREATE TABLE IF NOT EXISTS sales (
				id INTEGER PRIMARY KEY,
				customer_name TEXT,
				sale_date TEXT,
				total_amount REAL NOT NULL DEFAULT 0
			);
			"""
		)

		# Create sale_items table
		cursor.execute(
			"""
			CREATE TABLE IF NOT EXISTS sale_items (
				id INTEGER PRIMARY KEY,
				sale_id INTEGER NOT NULL,
				medicine_id INTEGER NOT NULL,
				quantity_sold INTEGER NOT NULL,
				price_per_item REAL NOT NULL,
				FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
				FOREIGN KEY (medicine_id) REFERENCES medicines(id)
			);
			"""
		)

		# Create users table
		cursor.execute(
			"""
			CREATE TABLE IF NOT EXISTS users (
				id INTEGER PRIMARY KEY,
				username TEXT UNIQUE NOT NULL,
				password_hash TEXT NOT NULL,
				role TEXT NOT NULL DEFAULT 'staff'
			);
			"""
		)

		# Ensure role column exists (for existing DBs created earlier)
		cols = cursor.execute("PRAGMA table_info(users)").fetchall()
		col_names = {c[1] for c in cols}
		if "role" not in col_names:
			cursor.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'staff'")

		connection.commit()

		# Create sales table
		cursor.execute(
			"""
			CREATE TABLE IF NOT EXISTS sales (
				id INTEGER PRIMARY KEY,
				customer_name TEXT,
				sale_date TEXT,
				total_amount REAL NOT NULL DEFAULT 0
			);
			"""
		)

		# Create sale_items table
		cursor.execute(
			"""
			CREATE TABLE IF NOT EXISTS sale_items (
				id INTEGER PRIMARY KEY,
				sale_id INTEGER NOT NULL,
				medicine_id INTEGER NOT NULL,
				quantity_sold INTEGER NOT NULL,
				price_per_item REAL NOT NULL,
				FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
				FOREIGN KEY (medicine_id) REFERENCES medicines(id)
			);
			"""
		)

		# Create users table
		cursor.execute(
			"""
			CREATE TABLE IF NOT EXISTS users (
				id INTEGER PRIMARY KEY,
				username TEXT UNIQUE NOT NULL,
				password_hash TEXT NOT NULL,
				role TEXT NOT NULL DEFAULT 'staff'
			);
			"""
		)

		# Ensure role column exists (for existing DBs created earlier)
		cols = cursor.execute("PRAGMA table_info(users)").fetchall()
		col_names = {c[1] for c in cols}
		if "role" not in col_names:
			cursor.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'staff'")

		connection.commit()
	finally:
		connection.close()


if __name__ == "__main__":
	create_tables()
	print("pharmacy.db initialized successfully.")


