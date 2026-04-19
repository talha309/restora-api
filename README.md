# 🍽️ Restora API

> A full-featured Restaurant Management REST API built with FastAPI & PostgreSQL — handling orders, tables, reservations, menu, inventory, and an AI-powered hotel assistant.

---

## 🚀 Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Authentication | JWT (python-jose + passlib/bcrypt) |
| Validation | Pydantic v2 |
| AI Assistant | LangChain + LangGraph + Google Gemini |
| Vector Store | FAISS |
| Embeddings | Google Generative AI Embeddings |

---

## 📁 Project Structure

```
restora-api/
│
├── main.py                      ← FastAPI app entry point
│
├── db/
│   └── database.py              ← DB connection, engine, get_db()
│
├── models/
│   ├── user_model.py            ← User table
│   ├── menu_model.py            ← Category + MenuItem tables
│   ├── table_model.py           ← Table + Reservation tables
│   ├── order_model.py           ← Order + OrderItem tables
│   └── inventory_model.py       ← InventoryItem table
│
├── schemas/
│   ├── user_schema.py
│   ├── menu_schema.py
│   ├── table_schema.py
│   ├── order_schema.py
│   └── inventory_schema.py
│
├── routes/
│   ├── auth_routes.py           ← /auth
│   ├── menu_routes.py           ← /menu
│   ├── table_routes.py          ← /tables + /reservations
│   ├── order_routes.py          ← /orders
│   ├── inventory_routes.py      ← /inventory
│   └── chat_routes.py           ← /chat (AI Assistant)
│
├── utils/
│   └── auth_util.py             ← JWT + password hashing
│
├── ai_rag/
│   └── rag_agent.py             ← LangGraph RAG agent (Gemini)
│
├── data.txt                     ← Hotel/restaurant knowledge base
├── alembic/                     ← Database migrations
├── alembic.ini
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/restora-api.git
cd restora-api
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/restora_db
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GOOGLE_API_KEY=your_google_api_key_here
```

### 5. Run database migrations
```bash
alembic upgrade head
```

### 6. Start the server
```bash
uvicorn main:app --reload
```

Server runs at → `http://127.0.0.1:8000`

API Docs at → `http://127.0.0.1:8000/docs`

---

## 🔐 Authentication

Restora API uses **JWT Bearer Token** authentication.

### Register
```http
POST /auth/register
```
```json
{
    "username": "john",
    "email": "john@example.com",
    "password": "secret123",
    "role": "admin"
}
```

### Login
```http
POST /auth/login
```
```json
{
    "email": "john@example.com",
    "password": "secret123"
}
```

Use the returned `access_token` as `Bearer Token` in all protected requests.

---

## 👥 Roles & Permissions

| Feature | Admin | Waiter | Kitchen |
|---------|:-----:|:------:|:-------:|
| Manage Menu | ✅ | ❌ | ❌ |
| View Menu | ✅ | ✅ | ✅ |
| Manage Tables | ✅ | ✅ | ❌ |
| Manage Reservations | ✅ | ✅ | ❌ |
| Place Orders | ✅ | ✅ | ❌ |
| View Orders | ✅ | Own only | Active only |
| Cancel Orders | ✅ | ✅ | ❌ |
| Manage Inventory | ✅ | ✅ | ❌ |
| Delete anything | ✅ | ❌ | ❌ |

---

## 🔌 API Endpoints

### 🔐 Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login → get JWT token |

### 🍕 Menu
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/menu/` | Get all menu items |
| GET | `/menu/{id}` | Get single item |
| POST | `/menu/` | Create item (admin) |
| PUT | `/menu/{id}` | Update item (admin) |
| PATCH | `/menu/{id}/availability` | Toggle available/unavailable |
| DELETE | `/menu/{id}` | Delete item (admin) |
| GET | `/menu/categories` | Get all categories |
| POST | `/menu/categories` | Create category (admin) |
| PUT | `/menu/categories/{id}` | Update category (admin) |
| DELETE | `/menu/categories/{id}` | Delete category (admin) |

### 🪑 Tables & Reservations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tables/` | Get all tables |
| GET | `/tables/{id}` | Get single table |
| POST | `/tables/` | Create table (admin/waiter) |
| PUT | `/tables/{id}` | Update table (admin/waiter) |
| DELETE | `/tables/{id}` | Delete table (admin) |
| GET | `/tables/reservations` | Get all reservations |
| POST | `/tables/reservations` | Create reservation |
| PATCH | `/tables/reservations/{id}` | Confirm / Cancel |
| DELETE | `/tables/reservations/{id}` | Delete reservation |

### 🧾 Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/orders/` | Get orders (role filtered) |
| GET | `/orders/{id}` | Get single order |
| GET | `/orders/table/{table_id}` | Get active orders by table |
| POST | `/orders/` | Place new order |
| PATCH | `/orders/{id}/status` | Update order status |
| DELETE | `/orders/{id}` | Delete order (admin) |

### 📦 Inventory
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/inventory/` | Get all items |
| GET | `/inventory/{id}` | Get single item |
| POST | `/inventory/` | Add new item |
| PUT | `/inventory/{id}` | Update item details |
| PATCH | `/inventory/{id}/increment` | Add stock |
| PATCH | `/inventory/{id}/decrement` | Deduct stock |
| GET | `/inventory/alerts/low-stock` | Low stock alerts |
| DELETE | `/inventory/{id}` | Delete item (admin) |

### 🤖 AI Chat Assistant
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat/query` | Ask AI assistant anything |

```json
{
    "query": "What are the hotel amenities?",
    "thread_id": "1"
}
```

---

## ⚙️ Order Flow

```
1. Waiter places order        → POST /orders/
2. Table auto → "occupied"
3. Kitchen sees order         → status: "pending"
4. Kitchen updates            → status: "preparing"
5. Kitchen updates            → status: "ready"
6. Waiter marks               → status: "served"
7. Table auto → "available"
```

---

## 🤖 AI Assistant

The `/chat/query` endpoint is powered by a **RAG (Retrieval-Augmented Generation)** agent built with **LangGraph + Google Gemini**.

- Loads knowledge from `data.txt`
- Splits and embeds using **Google Generative AI Embeddings**
- Stores vectors in **FAISS** for fast retrieval
- Maintains **conversation memory** per `thread_id`
- Uses **Gemini 2.5 Flash** for response generation

---

## 📦 Requirements

```txt
fastapi
uvicorn
sqlalchemy
psycopg2-binary
alembic
python-jose[cryptography]
passlib[bcrypt]
pydantic[email]
python-dotenv
langchain
langchain-community
langchain-google-genai
langgraph
faiss-cpu
```

Install all:
```bash
pip install -r requirements.txt
```

---

## 🧪 Postman Testing

Import the collection and set these environment variables:

```
base_url  →  http://127.0.0.1:8000
token     →  (auto-saved after login)
```

Add this script to Login request → **Scripts → After response**:
```javascript
const response = pm.response.json();
if (response.access_token) {
    pm.environment.set("token", response.access_token);
    console.log("✅ Token saved!");
}
```

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">
  Built with ❤️ using FastAPI + PostgreSQL + Google Gemini
</div>
