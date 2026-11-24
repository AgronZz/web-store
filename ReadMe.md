# URBANSTORE – Full-Stack Clothing Store

A full-stack e-commerce web application developed using **React, Flask, Python, and MySQL**.

URBANSTORE allows customers to browse clothing products, search and filter products, manage a shopping cart, and place orders. Administrators and advanced users can manage products, orders, and sales reports.

## Technologies

### Frontend
- React
- Vite
- JavaScript
- Axios
- CSS

### Backend
- Python
- Flask
- Flask REST API
- Flask-SQLAlchemy
- Flask-JWT-Extended
- PyMySQL

### Database
- MySQL

## Main Features

### Authentication and Authorization
- User login.
- JWT-based authentication.
- Password hashing.
- Three user roles:
  - Admin
  - Advanced User
  - Simple User
- Role-based access control.

### Product Management
- Create, read, update, and delete products.
- Product categories and brands.
- Product sizes and colors.
- Product search and combined filters.
- Product availability and stock calculation.
- Discounts.

### Shopping and Orders
- Product browsing.
- Shopping cart.
- Customer profiles.
- Order creation and checkout.
- Customer order history.
- Order confirmation and cancellation.
- Order status management.

### Reports
- Daily earnings.
- Monthly earnings.
- Top-selling products.

## Project Structure

```text
web-store/
│
├── backend/
│   ├── models/
│   ├── routes/
│   ├── app.py
│   ├── config.py
│   ├── extensions.py
│   ├── permissions.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── App.jsx
│   │   └── App.css
│   ├── package.json
│   └── vite.config.js
│
├── database/
│   └── web_store_db.sql
│
├── .gitignore
└── ReadMe.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/AgronZz/web-store.git
cd web-store
```

### 2. Database Setup

1. Install and start MySQL Server.
2. Open MySQL Workbench and connect to your MySQL server.
3. Navigate to **Server → Data Import**.
4. Select **Import from Self-Contained File**.
5. Browse to `database/web_store_db.sql` inside the project folder.
6. Select the appropriate target schema if requested. The SQL export includes the database creation statement for `web_store_db`.
7. Click **Start Import**.
8. After importing, refresh the Schemas panel and verify that `web_store_db` is available.

The SQL file contains the database structure, relationships, and sample data.

### 3. Backend Setup

Create and activate a Python virtual environment:

```bash
python3 -m venv backend/venv
source backend/venv/bin/activate
```

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Create your environment configuration:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and provide your own MySQL credentials and JWT secret key.

Example configuration:

```env
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=web_store_db
JWT_SECRET_KEY=your_secret_key
```

Start the Flask server:

```bash
cd backend
python app.py
```

The backend will run at:

`http://127.0.0.1:5000`

### 4. Frontend Setup

Open a second terminal from the project root:

```bash
cd web-store/frontend
npm install
npm run dev
```

The frontend will run at the address displayed by Vite, normally:

`http://localhost:5173`

## API Overview

The backend exposes REST API endpoints under `/api`.

| Resource | Endpoint | Operations |
|---|---|---|
| Authentication | `/api/users/login` | User login |
| Users | `/api/users/` | User management |
| Products | `/api/products/` | Product CRUD |
| Product Search | `/api/products/search` | Search and combined filters |
| Orders | `/api/orders/` | Create and retrieve orders |
| Customer Orders | `/api/orders/my-orders` | Retrieve personal order history |
| Order Management | `/api/orders/{id}/confirm` | Confirm order |
| Order Management | `/api/orders/{id}/cancel` | Cancel order |
| Order Status | `/api/orders/{id}/status` | Update order status |
| Daily Reports | `/api/reports/daily-earnings` | Daily earnings |
| Monthly Reports | `/api/reports/monthly-earnings` | Monthly earnings |
| Top Products | `/api/reports/top-products` | Best-selling products |

Protected endpoints require a valid JWT access token and appropriate user permissions.

## User Roles

| Role | Permissions |
|---|---|
| Admin | User management, product management, orders, and reports |
| Advanced User | Product management, orders, and reports |
| Simple User | Browse products, place orders, and view personal order history |

## Security

- Passwords are stored as hashes.
- JWT tokens are used for authentication.
- Role-based authorization protects restricted endpoints.
- Database credentials and secret keys are stored in environment variables.
- Sensitive files such as `.env` are excluded from Git.

## Author

**Agron Berisha**

GitHub: https://github.com/AgronZz

Repository: https://github.com/AgronZz/web-store