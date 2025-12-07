from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS

from database import (
	add_medicine,
	get_all_medicines,
	update_medicine_stock,
	get_medicine_by_id,
	update_medicine,
	delete_medicine,
	record_sale,
    
	get_summary_stats,
	get_dashboard_stats,
	add_user,
	get_user_by_username,
	list_sales,
	get_sale_details,
)


app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)
app.secret_key = "development-secret-key-change-me"


@app.route("/")
def index() -> any:
	"""Serve the SPA."""
	return send_from_directory("static", "index.html")


@app.route("/about")
def about() -> any:
	"""Serve the About page."""
	return send_from_directory("static", "about.html")


@app.get("/api/medicines")
def api_get_medicines():
	if not session.get("user_id"):
		return jsonify({"success": False, "message": "Unauthorized"}), 401
	medicines = get_all_medicines()
	return jsonify({"success": True, "data": medicines})


@app.post("/api/medicines/add")
def api_add_medicine():
	if not session.get("user_id"):
		return jsonify({"success": False, "message": "Unauthorized"}), 401
	body = request.get_json(silent=True) or {}
	try:
		name = (body.get("name") or "").strip()
		manufacturer = (body.get("manufacturer") or "").strip()
		batch_no = (body.get("batch_no") or "").strip()
		expiry_date = (body.get("expiry_date") or "").strip()
		quantity = int(body.get("quantity", 0))
		price = float(body.get("price", 0))

		if not name:
			return jsonify({"success": False, "message": "Name is required"}), 400

		new_id = add_medicine(name, manufacturer, batch_no, expiry_date, quantity, price)
		return jsonify({"success": True, "message": "Medicine added", "id": new_id})
	except Exception as exc:
		return jsonify({"success": False, "message": str(exc)}), 400


@app.put("/api/medicines/<int:medicine_id>")
def api_update_medicine(medicine_id: int):
	if not session.get("user_id"):
		return jsonify({"success": False, "message": "Unauthorized"}), 401
	body = request.get_json(silent=True) or {}
	try:
		update_medicine(
			medicine_id,
			(body.get("name") or "").strip(),
			(body.get("manufacturer") or "").strip(),
			(body.get("batch_no") or "").strip(),
			(body.get("expiry_date") or "").strip(),
			int(body.get("quantity", 0)),
			float(body.get("price", 0)),
		)
		return jsonify({"success": True})
	except Exception as exc:
		return jsonify({"success": False, "message": str(exc)}), 400


@app.delete("/api/medicines/<int:medicine_id>")
def api_delete_medicine(medicine_id: int):
	if not session.get("user_id"):
		return jsonify({"success": False, "message": "Unauthorized"}), 401
	try:
		delete_medicine(medicine_id)
		return jsonify({"success": True})
	except Exception as exc:
		return jsonify({"success": False, "message": str(exc)}), 400


@app.post("/api/sales/create")
def api_create_sale():
	if not session.get("user_id"):
		return jsonify({"success": False, "message": "Unauthorized"}), 401
	body = request.get_json(silent=True) or {}
	try:
		customer_name = (body.get("customer_name") or "").strip()
		items = body.get("items") or body.get("sale_items") or []
		if not isinstance(items, list):
			return jsonify({"success": False, "message": "items must be a list"}), 400

		sale_id = record_sale(customer_name, items)
		return jsonify({"success": True, "message": "Sale recorded", "sale_id": sale_id})
	except Exception as exc:
		return jsonify({"success": False, "message": str(exc)}), 400





@app.get("/api/summary")
def api_summary():
	if not session.get("user_id"):
		return jsonify({"success": False, "message": "Unauthorized"}), 401
	stats = get_summary_stats()
	return jsonify({"success": True, "data": stats})


@app.get("/api/dashboard-stats")
def api_dashboard_stats():
	if not session.get("user_id"):
		return jsonify({"success": False, "message": "Unauthorized"}), 401
	stats = get_dashboard_stats()
	return jsonify({"success": True, "data": stats})


@app.get("/api/sales")
def api_list_sales():
	if not session.get("user_id"):
		return jsonify({"success": False, "message": "Unauthorized"}), 401
	return jsonify({"success": True, "data": list_sales()})


@app.get("/api/sales/<int:sale_id>")
def api_sale_details(sale_id: int):
	if not session.get("user_id"):
		return jsonify({"success": False, "message": "Unauthorized"}), 401
	try:
		return jsonify({"success": True, "data": get_sale_details(sale_id)})
	except Exception as exc:
		return jsonify({"success": False, "message": str(exc)}), 404


@app.post("/api/register")
def api_register():
	body = request.get_json(silent=True) or {}
	from werkzeug.security import generate_password_hash
	try:
		# Only admin can register new users
		if not session.get("user_id") or session.get("role") != "admin":
			return jsonify({"success": False, "message": "Forbidden"}), 403
		username = (body.get("username") or "").strip()
		password = body.get("password") or ""
		role = (body.get("role") or "staff").strip() or "staff"
		if not username or not password:
			return jsonify({"success": False, "message": "Username and password are required"}), 400
		password_hash = generate_password_hash(password)
		user_id = add_user(username, password_hash, role)
		return jsonify({"success": True, "user_id": user_id})
	except Exception as exc:
		return jsonify({"success": False, "message": str(exc)}), 400


@app.post("/api/login")
def api_login():
	body = request.get_json(silent=True) or {}
	from werkzeug.security import check_password_hash
	username = (body.get("username") or "").strip()
	password = body.get("password") or ""
	user = get_user_by_username(username)
	if not user or not check_password_hash(user["password_hash"], password):
		return jsonify({"success": False, "message": "Invalid credentials"}), 401
	session["user_id"] = int(user["id"])  # type: ignore[index]
	session["role"] = user.get("role", "staff")
	return jsonify({"success": True})


@app.get("/api/logout")
def api_logout():
	session.clear()
	return jsonify({"success": True})


@app.get("/api/check_session")
def api_check_session():
	return jsonify({"success": True, "logged_in": bool(session.get("user_id"))})


# Dev-only admin reset helper (only for local educational use)
@app.post("/api/reset-admin")
def api_reset_admin():
	try:
		body = request.get_json(silent=True) or {}
		username = (body.get("username") or "admin").strip() or "admin"
		password = body.get("password") or "admin123"
		from werkzeug.security import generate_password_hash
		user = get_user_by_username(username)
		phash = generate_password_hash(password)
		if user:
			# Update existing
			from database import get_db_connection
			conn = get_db_connection()
			try:
				conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (phash, user["id"]))
				conn.commit()
			finally:
				conn.close()
		else:
			add_user(username, phash)
		return jsonify({"success": True, "message": "Admin credentials set."})
	except Exception as exc:
		return jsonify({"success": False, "message": str(exc)}), 400


@app.get("/api/debug-user")
def api_debug_user():
	# Dev helper: return user record (excluding hash characters count only)
	try:
		username = (request.args.get("username") or "admin").strip() or "admin"
		user = get_user_by_username(username)
		if not user:
			return jsonify({"success": True, "exists": False})
		return jsonify({
			"success": True,
			"exists": True,
			"id": user["id"],
			"username": user["username"],
			"password_hash_len": len(user["password_hash"]) if user.get("password_hash") else 0
		})
	except Exception as exc:
		return jsonify({"success": False, "message": str(exc)}), 400


@app.post("/api/debug-login")
def api_debug_login():
	"""Dev helper: diagnose credential check for a username/password."""
	body = request.get_json(silent=True) or {}
	from werkzeug.security import check_password_hash
	username = (body.get("username") or "").strip()
	password = body.get("password") or ""
	user = get_user_by_username(username)
	if not user:
		return jsonify({
			"success": True,
			"user_exists": False,
			"received_username_len": len(username),
			"received_password_len": len(password),
		})
	stored_hash = user.get("password_hash")
	check = False
	try:
		check = check_password_hash(stored_hash, password)
	except Exception as exc:
		return jsonify({
			"success": False,
			"error": str(exc),
			"user_exists": True,
			"hash_prefix": stored_hash[:12] if stored_hash else None,
		})
	return jsonify({
		"success": True,
		"user_exists": True,
		"hash_prefix": stored_hash[:12] if stored_hash else None,
		"check_result": check,
		"received_username_len": len(username),
		"received_password_len": len(password),
	})


if __name__ == "__main__":
	app.run(host="127.0.0.1", port=5000, debug=True)


