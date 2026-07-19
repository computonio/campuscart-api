# CampusCart API

A backend API for a marketplace where students can buy and sell used items — textbooks, calculators, cycles, and similar — within their college or hostel. Built with FastAPI and PostgreSQL.

## Why I built this

I wanted to work with backend concepts beyond basic CRUD — authentication, role-based permissions, and a request/approval flow between two different users. It's also something genuinely useful: every semester, students end up trying to sell old textbooks through hostel WhatsApp groups, which makes it hard to track who wants what.

## What it does

- Users sign up as either a **buyer** or a **seller**
- Sellers can create listings (title, description, category, price)
- Buyers can browse listings and send a request to buy an item
- Sellers can accept or reject requests on their own listings
- When a request is accepted, the listing is automatically marked as sold
- All actions are protected with JWT authentication, and certain actions are restricted by role — for example, only sellers can create listings

## Stack

- **FastAPI** for the API
- **PostgreSQL** for the database, with **SQLAlchemy** as the ORM
- **JWT** (PyJWT) for authentication and **bcrypt** for password hashing
- **Docker Compose** to run the app and database together without a local Postgres install

## Project structure

```
app/
├── main.py            # app entrypoint, wires up routers
├── database.py         # SQLAlchemy engine/session
├── models.py            # User, Listing, PurchaseRequest tables
├── schemas.py            # Pydantic request/response models
├── security.py            # password hashing + JWT
├── deps.py                 # get_current_user, require_role()
└── routers/
    ├── auth.py                # /auth/register, /auth/login
    ├── listings.py             # /listings CRUD
    └── requests.py              # purchase request workflow
```

## Running it

```bash
docker compose up --build
```

Then visit `http://localhost:8000/docs` for a full interactive UI (Swagger), where you can register, log in, and call every endpoint directly from the browser.

It can also be run locally with SQLite instead of Postgres, without Docker:

```bash
python -m venv venv
venv\Scripts\python.exe -m pip install fastapi "uvicorn[standard]" sqlalchemy pyjwt bcrypt python-multipart "pydantic[email]" python-dotenv
$env:DATABASE_URL="sqlite:///./dev.db"
$env:SECRET_KEY="devsecret123"
venv\Scripts\python.exe -m uvicorn app.main:app --reload
```
(commands above are for Windows PowerShell; on macOS/Linux use `source venv/bin/activate` and `export` instead of `$env:`)

## Endpoints

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/auth/register` | Public | Register as a buyer or seller |
| POST | `/auth/login` | Public | Log in and receive a token |
| POST | `/listings/` | Seller | Create a new listing |
| GET | `/listings/` | Any authenticated user | Browse listings (filter by category/price) |
| GET | `/listings/mine` | Seller | View your own listings |
| PUT | `/listings/{id}` | Owning seller | Edit a listing |
| DELETE | `/listings/{id}` | Owning seller | Delete a listing |
| POST | `/listings/{id}/requests` | Buyer | Request to buy an item |
| GET | `/listings/{id}/requests` | Owning seller | View requests on a listing |
| GET | `/requests/me` | Buyer | View your own requests |
| PUT | `/requests/{id}` | Owning seller | Accept or reject a request |

## How the authentication works

On login, the server issues a signed JWT containing the user's ID. This token is sent with every subsequent request as a header, and the server validates it and identifies the user before processing the request. This is what enforces the role restrictions — for instance, if a buyer attempts to call the "create listing" endpoint, the server checks their role from the token and rejects the request.
