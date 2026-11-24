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
- User registration and login.
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
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/AgronZz/web-store.git
cd web-store
```

### 2. Database Setup

1. Install and start MySQL Server.
2. Open MySQL Workbench.
3. Create a database named `web_store_db`.
4. Create the required tables and relationships.
5. Insert the initial roles and sample data.

### 3. Backend Setup

Create and activate a Python virtual environment:

```bash
python3 -m venv backend/venv
source backend/venv/bin/activate
```

Install the dependencies:

```bash
pip install -r backend/requirements.txt
```

Create your environment configuration:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and provide your own MySQL credentials and JWT secret key.

Start the Flask server:

```bash
cd backend
python app.py
```

The backend will run at:

```text
http://127.0.0.1:5000
```

### 4. Frontend Setup

Open a second terminal:

```bash
cd web-store/frontend
npm install
npm run dev
```

The frontend will run at the address displayed by Vite, normally:

```text
http://localhost:5173
```

## API Overview

The backend exposes REST API endpoints under `/api`.

| Resource | Endpoint | Operations |
|---|---|---|
| Authentication | `/api/users/login` | Login |
| Users | `/api/users/` | User management |
| Products | `/api/products/` | Product CRUD |
| Product Search | `/api/products/search` | Search and filters |
| Orders | `/api/orders/` | Create and retrieve orders |
| Customer Orders | `/api/orders/my-orders` | Customer order history |
| Order Management | `/api/orders/{id}/confirm` | Confirm order |
| Order Management | `/api/orders/{id}/cancel` | Cancel order |
| Order Status | `/api/orders/{id}/status` | Update order status |
| Reports | `/api/reports/` | Sales reports |

Protected endpoints require a valid JWT access token and appropriate user permissions.

## User Roles

| Role | Permissions |
|---|---|
| Admin | Full application and user management access |
| Advanced User | Product, order, and report management |
| Simple User | Browse products, place orders, and view personal order history |

## Security

- Passwords are stored as hashes.
- JWT tokens are used for authentication.
- Role-based authorization protects restricted endpoints.
- Database credentials and secret keys are stored in environment variables.
- Sensitive files such as `.env` are excluded from Git.

## Author

**Agron Berisha**

GitHub: [AgronZz](https://github.com/AgronZz)

Repository: [web-store](https://github.com/AgronZz/web-store)
