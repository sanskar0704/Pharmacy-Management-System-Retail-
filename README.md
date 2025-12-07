# Pharmacy Management System

A comprehensive web-based Pharmacy Management System built with Flask and SQLite, designed to streamline pharmacy operations including inventory management, sales billing, and transaction tracking.

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

## ✨ Features

- **📦 Inventory Management** - Add, update, and track medicines with batch numbers, expiry dates, and stock quantities
- **💰 Point of Sale (POS) Billing** - Fast and efficient billing system with real-time stock updates
- **📊 Sales Records** - Complete sales history with detailed transaction records and customer information
- **📈 Dashboard Analytics** - Real-time KPIs including total medicines, stock units, low stock alerts, and daily sales
- **🔐 User Authentication** - Secure login system with role-based access (admin/staff)
- **⚠️ Stock Management** - Automatic inventory deduction on sales with low stock warnings
- **🔍 Search & Filter** - Quick search functionality for medicines and sales records
- **📄 Export Functionality** - Export sales data to CSV format

## 🛠 Technology Stack

- **Backend**: Python 3.x, Flask (RESTful API)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Security**: Session-based authentication with password hashing (Werkzeug)
- **CORS**: Flask-CORS for cross-origin resource sharing

## 📦 Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "pharmacy management sys py"
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python init_db.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser and navigate to `http://127.0.0.1:5000`
   - Default admin credentials (if using reset-admin endpoint):
     - Username: `admin`
     - Password: `admin123`

## 🚀 Usage

### Initial Setup

1. Start the Flask server by running `python app.py`
2. Navigate to the login page
3. Use the admin credentials to log in
4. Start managing your pharmacy operations!

### Key Operations

- **Dashboard**: View real-time statistics and quick access to all modules
- **Medicines**: Add new medicines, update stock, and manage inventory
- **Billing**: Process sales transactions with automatic stock updates
- **Sales**: View sales history, filter by date, and export reports
- **About**: Learn more about the project and developer

### Managing Medicines

1. Navigate to the **Medicines** page
2. Fill in the medicine details (name, manufacturer, batch number, expiry date, quantity, price)
3. Click **Add Medicine** to add to inventory
4. View all medicines in the table below

### Processing Sales

1. Go to the **Billing** page
2. Enter customer details (optional)
3. Search for medicines and add them to the bill
4. Review the bill and click **Finalize Sale**
5. Stock is automatically updated upon sale completion

## 📁 Project Structure

```
pharmacy-management-sys-py/
│
├── app.py                 # Main Flask application
├── database.py            # Database operations and queries
├── init_db.py             # Database initialization script
├── requirements.txt       # Python dependencies
├── LICENSE                # MIT License
├── README.md             # This file
│
├── static/                # Static files (frontend)
│   ├── index.html        # Dashboard page
│   ├── login.html        # Login page
│   ├── medicines.html    # Medicine management page
│   ├── billing.html      # Billing/POS page
│   ├── sales.html        # Sales records page
│   ├── about.html        # About page
│   ├── manage.html       # Management page
│   ├── style.css         # Main stylesheet
│   ├── login.css         # Login page styles
│   ├── script.js         # Main JavaScript file
│   └── login.js          # Login page JavaScript
│
└── pharmacy.db           # SQLite database (created after initialization)
```

## 🔌 API Endpoints

### Authentication
- `POST /api/login` - User login
- `GET /api/logout` - User logout
- `GET /api/check_session` - Check current session status
- `POST /api/register` - Register new user (admin only)

### Medicines
- `GET /api/medicines` - Get all medicines
- `POST /api/medicines/add` - Add new medicine
- `PUT /api/medicines/<id>` - Update medicine
- `DELETE /api/medicines/<id>` - Delete medicine

### Sales
- `POST /api/sales/create` - Create new sale
- `GET /api/sales` - Get all sales
- `GET /api/sales/<id>` - Get sale details

### Statistics
- `GET /api/summary` - Get summary statistics
- `GET /api/dashboard-stats` - Get dashboard statistics

## 📸 Screenshots

_Add screenshots of your application here_

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Sanskar Surag**

- Full-stack developer passionate about creating efficient and user-friendly applications
- Developed and maintained this Pharmacy Management System

## 🙏 Acknowledgments

- Flask community for the excellent framework
- All contributors and users of this project

---

**© 2025 Sanskar Surag. All rights reserved.**

Pharmacy Management System - Developed by Sanskar Surag
