import sqlite3
from typing import Any, Dict, List, Optional


DB_PATH = "pharmacy.db"


def get_db_connection() -> sqlite3.Connection:
	"""
	Return a new SQLite connection to pharmacy.db with row factory set for dict-like access.
	Each caller is responsible for closing the connection.
	"""
	conn = sqlite3.connect(DB_PATH)
	conn.row_factory = sqlite3.Row
	# Ensure FK constraints are enforced
	conn.execute("PRAGMA foreign_keys = ON;")
	return conn


def add_medicine(name: str, manufacturer: str, batch_no: str, expiry_date: str, quantity: int, price: float) -> int:
	"""Insert a new medicine and return its new id."""
	conn = get_db_connection()
	try:
		cursor = conn.cursor()
		cursor.execute(
			"""
			INSERT INTO medicines (name, manufacturer, batch_no, expiry_date, quantity, price)
			VALUES (?, ?, ?, ?, ?, ?)
			""",
			(name, manufacturer, batch_no, expiry_date, quantity, price),
		)
		conn.commit()
		return cursor.lastrowid
	finally:
		conn.close()


def get_all_medicines() -> List[Dict[str, Any]]:
	"""Return all medicines as a list of dicts."""
	conn = get_db_connection()
	try:
		rows = conn.execute(
			"SELECT id, name, manufacturer, batch_no, expiry_date, quantity, price FROM medicines ORDER BY name ASC"
		).fetchall()
		return [dict(row) for row in rows]
	finally:
		conn.close()


def update_medicine(medicine_id: int, name: str, manufacturer: str, batch_no: str, expiry_date: str, quantity: int, price: float) -> None:
	"""Update all editable fields for a medicine."""
	conn = get_db_connection()
	try:
		conn.execute(
			"""
			UPDATE medicines
			SET name = ?, manufacturer = ?, batch_no = ?, expiry_date = ?, quantity = ?, price = ?
			WHERE id = ?
			""",
			(name, manufacturer, batch_no, expiry_date, quantity, price, medicine_id),
		)
		conn.commit()
	finally:
		conn.close()


def delete_medicine(medicine_id: int) -> None:
	"""Delete a medicine by id."""
	conn = get_db_connection()
	try:
		conn.execute("DELETE FROM medicines WHERE id = ?", (medicine_id,))
		conn.commit()
	finally:
		conn.close()


def update_medicine_stock(medicine_id: int, new_quantity: int) -> None:
	"""Update stock quantity for a medicine."""
	conn = get_db_connection()
	try:
		conn.execute(
			"UPDATE medicines SET quantity = ? WHERE id = ?",
			(new_quantity, medicine_id),
		)
		conn.commit()
	finally:
		conn.close()


def get_medicine_by_id(medicine_id: int) -> Optional[Dict[str, Any]]:
	"""Return a medicine by id or None if not found."""
	conn = get_db_connection()
	try:
		row = conn.execute(
			"SELECT id, name, manufacturer, batch_no, expiry_date, quantity, price FROM medicines WHERE id = ?",
			(medicine_id,),
		).fetchone()
		return dict(row) if row else None
	finally:
		conn.close()


def record_sale(customer_name: str, sale_items: List[Dict[str, Any]]) -> int:
	"""
	Record a sale and reduce inventory accordingly.

	Args:
		customer_name: Name of the customer for the sale.
		sale_items: List of items with keys: medicine_id (int), quantity (int), price (float optional).
		If price is omitted, current medicine price will be used.

	Returns:
		The created sale id.
	"""
	conn = get_db_connection()
	try:
		cursor = conn.cursor()
		# Begin transaction
		cursor.execute("BEGIN")

		total_amount = 0.0
		resolved_items: List[Dict[str, Any]] = []

		for item in sale_items:
			medicine_id = int(item["medicine_id"]) if "medicine_id" in item else int(item["id"])  # allow id alias
			quantity = int(item["quantity"]) if "quantity" in item else int(item.get("quantity_sold", 0))
			if quantity <= 0:
				raise ValueError("Quantity must be greater than zero")

			med_row = cursor.execute(
				"SELECT id, name, quantity, price FROM medicines WHERE id = ?",
				(medicine_id,),
			).fetchone()
			if not med_row:
				raise ValueError(f"Medicine with id {medicine_id} not found")

			current_quantity = int(med_row["quantity"])  # type: ignore[index]
			if current_quantity < quantity:
				raise ValueError(f"Insufficient stock for medicine id {medicine_id}")

			price_per_item = float(item.get("price", med_row["price"]))  # type: ignore[index]
			line_total = price_per_item * quantity
			total_amount += line_total

			resolved_items.append(
				{
					"medicine_id": medicine_id,
					"quantity": quantity,
					"price_per_item": price_per_item,
				}
			)

		# Insert sale header
		from datetime import datetime
		sale_date = datetime.utcnow().isoformat()
		cursor.execute(
			"INSERT INTO sales (customer_name, sale_date, total_amount) VALUES (?, ?, ?)",
			(customer_name, sale_date, total_amount),
		)
		sale_id = cursor.lastrowid

		# Insert sale items and update stock
		for r_item in resolved_items:
			cursor.execute(
				"""
				INSERT INTO sale_items (sale_id, medicine_id, quantity_sold, price_per_item)
				VALUES (?, ?, ?, ?)
				""",
				(sale_id, r_item["medicine_id"], r_item["quantity"], r_item["price_per_item"]),
			)
			# Decrement stock
			cursor.execute(
				"UPDATE medicines SET quantity = quantity - ? WHERE id = ?",
				(r_item["quantity"], r_item["medicine_id"]),
			)

		conn.commit()
		return int(sale_id)
	except Exception:
		conn.rollback()
		raise
	finally:
		conn.close()





def get_summary_stats() -> Dict[str, Any]:
	"""Return high-level dashboard metrics."""
	conn = get_db_connection()
	try:
		cursor = conn.cursor()
		# Total medicines
		total_medicines = cursor.execute("SELECT COUNT(*) FROM medicines").fetchone()[0]
		# Total stock units
		total_units = cursor.execute("SELECT COALESCE(SUM(quantity), 0) FROM medicines").fetchone()[0]
		# Low stock (<=5 units)
		low_stock = cursor.execute("SELECT COUNT(*) FROM medicines WHERE quantity <= 5").fetchone()[0]
		# Sales today revenue
		from datetime import datetime
		today_prefix = datetime.utcnow().date().isoformat()
		sales_today = cursor.execute(
			"SELECT COALESCE(SUM(total_amount), 0) FROM sales WHERE substr(sale_date,1,10) = ?",
			(today_prefix,),
		).fetchone()[0]
		# Total sales count
		sales_count = cursor.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
		return {
			"total_medicines": int(total_medicines),
			"total_units": int(total_units or 0),
			"low_stock": int(low_stock or 0),
			"sales_today": float(sales_today or 0.0),
			"sales_count": int(sales_count or 0),
		}
	finally:
		conn.close()


def get_dashboard_stats() -> Dict[str, Any]:
	"""Return overall dashboard KPIs: total revenue, low stock (< 10), total medicines."""
	conn = get_db_connection()
	try:
		cursor = conn.cursor()
		total_revenue = cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM sales").fetchone()[0]
		low_stock_count = cursor.execute("SELECT COUNT(*) FROM medicines WHERE quantity < 10").fetchone()[0]
		total_medicines = cursor.execute("SELECT COUNT(*) FROM medicines").fetchone()[0]
		return {
			"total_revenue": float(total_revenue or 0.0),
			"low_stock_count": int(low_stock_count or 0),
			"total_medicines": int(total_medicines or 0),
		}
	finally:
		conn.close()


def add_user(username: str, password_hash: str, role: str = 'staff') -> int:
	"""Create a new user and return id."""
	conn = get_db_connection()
	try:
		cursor = conn.cursor()
		cursor.execute(
			"INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
			(username, password_hash, role),
		)
		conn.commit()
		return cursor.lastrowid
	finally:
		conn.close()


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
	"""Get a user by username, or None."""
	conn = get_db_connection()
	try:
		row = conn.execute(
			"SELECT id, username, password_hash, role FROM users WHERE username = ?",
			(username,),
		).fetchone()
		return dict(row) if row else None
	finally:
		conn.close()


def list_sales() -> List[Dict[str, Any]]:
	"""Return minimal list of sales for listing view."""
	conn = get_db_connection()
	try:
		rows = conn.execute(
			"SELECT id, customer_name, sale_date, total_amount FROM sales ORDER BY sale_date DESC"
		).fetchall()
		return [dict(row) for row in rows]
	finally:
		conn.close()


def get_sale_details(sale_id: int) -> Dict[str, Any]:
	"""Return sale header and line items."""
	conn = get_db_connection()
	try:
		cursor = conn.cursor()
		head = cursor.execute(
			"SELECT id, customer_name, sale_date, total_amount FROM sales WHERE id = ?",
			(sale_id,),
		).fetchone()
		if not head:
			raise ValueError("Sale not found")
		items = cursor.execute(
			"""
			SELECT si.id, si.medicine_id, m.name as medicine_name, si.quantity_sold, si.price_per_item,
			       (si.quantity_sold * si.price_per_item) AS line_total
			FROM sale_items si
			JOIN medicines m ON m.id = si.medicine_id
			WHERE si.sale_id = ?
			ORDER BY si.id ASC
			""",
			(sale_id,),
		).fetchall()
		return {"header": dict(head), "items": [dict(r) for r in items]}
	finally:
		conn.close()


