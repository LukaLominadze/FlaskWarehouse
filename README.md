# FlaskWarehouse

A web-based warehouse management system built with Flask. Manage products, suppliers, stock movements, and generate inventory reports through a clean web interface or REST API.
See my hosted version here -- https://warehouse.kabada.org

## Features

- **Product Management** - Full CRUD with search, category filtering, pagination, and CSV import
- **Supplier Management** - Track suppliers with contact info, country, and lead times
- **Stock Tracking** - Record stock-in and stock-out movements with cost, reference, and destination
- **Low Stock Alerts** - Automatic alerts when product stock falls below minimum thresholds
- **Exchange Rates** - Manage currency exchange rates and convert between currencies
- **Reports** - Inventory turnover analysis and top-moving products
- **User Authentication** - Registration, login, session-based auth with 30-day sessions
- **Admin Panel** - User management with role-based access control (create, edit, delete, reset password, toggle admin)
- **REST API** - Full JSON API for all operations (products, suppliers, stock, reports, exchange rates)

## Supported Platforms

- Linux (tested on Ubuntu, Debian)

## Requirements

- Python 3.x

## Setup

```bash
git clone https://github.com/LukaLominadze/FlaskWarehouse
cd FlaskWarehouse
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask create-admin
python run.py
```

### Environment Variables

Edit `.env` to configure:

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `you-will-never-guess` | Secret key for session signing |
| `DATABASE_URL` | `sqlite:///app.db` | Database connection string |
| `DEBUG` | `False` | Enable debug mode |

## Usage

After setup, the app runs at `http://127.0.0.1:5000`.

| Page | URL | Description |
|---|---|---|
| Dashboard | `/dashboard` | Overview with low stock alerts, inventory value, product count |
| Products | `/products` | List, search, filter by category |
| Suppliers | `/suppliers` | List, search, filter by country |
| Stock In | `/stock-in` | Record incoming stock |
| Stock Out | `/stock-out` | Record outgoing stock |
| Alerts | `/alerts` | Products below minimum stock |
| Exchange Rates | `/exchange-rates` | Manage currency rates |
| Reports | `/reports` | Inventory turnover and top products |
| Admin | `/admin` | User management (admin only) |

### CLI Commands

```bash
flask create-admin    # Create an admin user interactively
flask promote-user    # Promote an existing user to admin
```

### API

The REST API is available at `/api` with the following endpoints:

| Endpoint | Methods | Description |
|---|---|---|
| `/api/status` | GET | Health check |
| `/api/products` | GET, POST | List/create products |
| `/api/products/<id>` | GET, PUT, DELETE | Get/update/delete a product |
| `/api/products/import` | POST | Import products from CSV |
| `/api/products/<id>/movements` | GET | Stock movement history |
| `/api/stock-in` | POST | Record stock-in |
| `/api/stock-out` | POST | Record stock-out |
| `/api/alerts` | GET | Low stock products |
| `/api/inventory-value` | GET | Total inventory value |
| `/api/suppliers` | GET, POST | List/create suppliers |
| `/api/suppliers/<id>` | PUT, DELETE | Update/delete a supplier |
| `/api/exchange-rates` | GET, POST | Get/update exchange rates |
| `/api/convert` | GET | Convert currency |
| `/api/reports/turnover` | GET | Inventory turnover report |
| `/api/reports/top-products` | GET | Top moving products |

## License

[Apache License 2.0](LICENSE)
