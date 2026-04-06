"""
seed.py
--------------------
Creates an e-commerce SQLite database (workshop.db) and seeds it with lots of data.

Requires:
  pip install sqlalchemy

Run:
  python db_optimization_seed.py

Output:
  workshop.db

Notes:
- Uses SQLAlchemy 2.0 Core inserts for speed.
- Creates indexes AFTER inserts.
- Uses SQLite PRAGMAs to speed up seeding (OK for generating disposable DB).
"""

from __future__ import annotations

import os
import random
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

from sqlalchemy import ( Boolean, DateTime, ForeignKey, Integer, String, Text, create_engine, text, Index)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import insert


# -----------------------
# Config (tune as needed)
# -----------------------

DB_PATH = "workshop.db"
DB_URL = f"sqlite:///{DB_PATH}"

RANDOM_SEED = 1337

# Keep these moderate if you want smaller distribution.
N_USERS = 30_000
ADDRESSES_PER_USER = (1, 3)  # min, max
N_CATEGORIES = 120
N_PRODUCTS = 12_000
N_ORDERS = 200_000
ITEMS_PER_ORDER = (2, 6)
N_EVENTS = 500_000  # audit/event rows (great for time-range queries)
PAYMENT_RATE = 0.82  # % of orders that have a payment row

BATCH = 20_000


# -----------------------
# ORM Models
# -----------------------

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class Address(Base):
    __tablename__ = "addresses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)  # ISO-ish
    street: Mapped[str] = mapped_column(String(255), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    shipping_address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # created/paid/shipped/cancelled/refunded
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    coupon_code: Mapped[str | None] = mapped_column(String(40), nullable=True)


class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price_cents: Mapped[int] = mapped_column(Integer, nullable=False)


class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(30), nullable=False)  # stripe/paypal/...
    status: Mapped[str] = mapped_column(String(20), nullable=False)    # pending/paid/failed/refunded
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)  # login/view/add_to_cart/checkout/...
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


# Helpful indexes (create after seeding)
INDEX_DEFS = [
    Index("idx_users_email", User.email),
    Index("idx_users_active", User.is_active),
    Index("idx_users_created_at", User.created_at),

    Index("idx_addresses_user_id", Address.user_id),
    Index("idx_addresses_country_city", Address.country, Address.city),
    Index("idx_addresses_user_default", Address.user_id, Address.is_default),

    Index("idx_products_sku", Product.sku),
    Index("idx_products_category", Product.category_id),
    Index("idx_products_price", Product.price_cents),

    # Index("idx_orders_user", Order.user_id),  # Removed: used in Exercise 6 to demonstrate indexing
    Index("idx_orders_created_at", Order.created_at),
    Index("idx_orders_status", Order.status),
    Index("idx_orders_address", Order.shipping_address_id),

    Index("idx_items_order", OrderItem.order_id),
    Index("idx_items_product", OrderItem.product_id),

    Index("idx_payments_order", Payment.order_id),
    Index("idx_payments_status_paid_at", Payment.status, Payment.paid_at),

    Index("idx_events_user_created_at", Event.user_id, Event.created_at),
    Index("idx_events_type_created_at", Event.event_type, Event.created_at),
]


# -----------------------
# Random data helpers
# -----------------------

def r_email(rng: random.Random) -> str:
    name = "".join(rng.choices(string.ascii_lowercase, k=10))
    domain = rng.choice(["example.com", "mail.com", "school.fi", "company.io"])
    return f"{name}@{domain}"


def r_name(rng: random.Random) -> str:
    first = rng.choice(["Aino", "Eetu", "Mika", "Salla", "Olli", "Iida", "Ville", "Noora", "Jari", "Laura", "Tomi"])
    last = rng.choice(["Korhonen", "Virtanen", "Mäkinen", "Nieminen", "Mäkelä", "Hämäläinen", "Laine", "Heikkinen"])
    return f"{first} {last}"


def r_street(rng: random.Random) -> str:
    roads = ["Main St", "Market Rd", "River Ave", "Pine St", "Oak Rd", "Central Blvd", "Station St", "School Rd"]
    return f"{rng.randint(1, 200)} {rng.choice(roads)}"


def r_postal(rng: random.Random) -> str:
    return f"{rng.randint(10000, 99999)}"


def r_text(rng: random.Random, words: int = 10) -> str:
    vocab = [
        "fast", "slow", "database", "query", "index", "python", "orm", "join", "filter",
        "cache", "optimize", "latency", "transaction", "sqlite", "sqlalchemy", "report",
        "analytics", "sale", "coupon", "shipping", "customer", "refund"
    ]
    return " ".join(rng.choices(vocab, k=words))


def chunked(seq: List[Dict[str, Any]], size: int) -> List[List[Dict[str, Any]]]:
    return [seq[i:i + size] for i in range(0, len(seq), size)]


# -----------------------
# Seeding
# -----------------------

def main() -> None:
    rng = random.Random(RANDOM_SEED)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    engine = create_engine(DB_URL, future=True)

    # SQLite seed speed PRAGMAs (safe enough for generating a DB file)
    with engine.begin() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON;"))
        conn.execute(text("PRAGMA journal_mode=WAL;"))
        conn.execute(text("PRAGMA synchronous=OFF;"))
        conn.execute(text("PRAGMA temp_store=MEMORY;"))

    # Create tables
    Base.metadata.create_all(engine)

    # Use deterministic time ranges
    users_base = datetime(2023, 1, 1)
    orders_base = datetime(2024, 1, 1)
    now = datetime(2025, 12, 31)

    statuses = ["created", "paid", "shipped", "cancelled", "refunded"]
    status_weights = [18, 40, 25, 12, 5]

    payment_providers = ["stripe", "paypal", "klarna", "adyen"]
    payment_statuses = ["pending", "paid", "failed", "refunded"]
    payment_status_weights = [10, 78, 8, 4]

    event_types = ["login", "view_product", "add_to_cart", "checkout", "search", "logout"]

    # Make a pool of "heavy" users to create skew (more realistic + more interesting perf)
    heavy_users = [rng.randint(1, N_USERS) for _ in range(max(2000, N_USERS // 30))]

    # We'll also store default address per user for convenience when creating orders
    default_address_for_user: Dict[int, int] = {}

    # -----------------
    # Seed categories
    # -----------------
    print(f"Seeding categories: {N_CATEGORIES:,}")
    category_rows: List[Dict[str, Any]] = []
    for cid in range(1, N_CATEGORIES + 1):
        parent = None
        if cid > 10 and rng.random() < 0.55:
            parent = rng.randint(1, min(cid - 1, 10))  # keep some shallow parents
        category_rows.append({"id": cid, "name": f"Category {cid}", "parent_id": parent})

    with engine.begin() as conn:
        conn.execute(insert(Category), category_rows)

    # -----------------
    # Seed products
    # -----------------
    print(f"Seeding products: {N_PRODUCTS:,}")
    product_rows: List[Dict[str, Any]] = []
    adjectives = ["Super", "Mega", "Ultra", "Budget", "Pro", "Eco", "Premium", "Mini", "Max"]
    nouns = ["Widget", "Gadget", "Thing", "Item", "Tool", "Device", "Accessory", "Kit", "Pack"]

    for pid in range(1, N_PRODUCTS + 1):
        product_rows.append({
            "id": pid,
            "sku": f"SKU-{pid:07d}",
            "name": f"{rng.choice(adjectives)} {rng.choice(nouns)} {pid}",
            "category_id": rng.randint(1, N_CATEGORIES),
            "price_cents": rng.randint(199, 199_99),
        })

    with engine.begin() as conn:
        for batch in chunked(product_rows, BATCH):
            conn.execute(insert(Product), batch)

    # -----------------
    # Seed users + addresses
    # -----------------
    print(f"Seeding users: {N_USERS:,} and addresses...")
    user_rows: List[Dict[str, Any]] = []
    address_rows: List[Dict[str, Any]] = []

    cities = ["Helsinki", "Tampere", "Turku", "Oulu", "Espoo", "Vantaa", "Pori", "Rauma", "Kuopio", "Jyväskylä"]
    countries = ["FI", "SE", "NO", "EE", "DE"]

    address_id = 1
    for uid in range(1, N_USERS + 1):
        created = users_base + timedelta(days=rng.randint(0, 900), seconds=rng.randint(0, 86399))
        user_rows.append({
            "id": uid,
            "email": r_email(rng),
            "full_name": r_name(rng),
            "is_active": rng.random() > 0.07,
            "created_at": created,
        })

        n_addr = rng.randint(*ADDRESSES_PER_USER)
        default_idx = rng.randint(1, n_addr)
        for i in range(1, n_addr + 1):
            row = {
                "id": address_id,
                "user_id": uid,
                "city": rng.choice(cities),
                "country": rng.choice(countries),
                "street": r_street(rng),
                "postal_code": r_postal(rng),
                "is_default": (i == default_idx),
            }
            address_rows.append(row)
            if row["is_default"]:
                default_address_for_user[uid] = address_id
            address_id += 1

    with engine.begin() as conn:
        for batch in chunked(user_rows, BATCH):
            conn.execute(insert(User), batch)
        for batch in chunked(address_rows, BATCH):
            conn.execute(insert(Address), batch)

    # -----------------
    # Seed orders + items + payments
    # -----------------
    print(f"Seeding orders: {N_ORDERS:,}, items, and payments...")
    order_rows: List[Dict[str, Any]] = []
    item_rows: List[Dict[str, Any]] = []
    payment_rows: List[Dict[str, Any]] = []

    order_id = 1
    item_id = 1
    payment_id = 1

    # Coupon pool for some orders
    coupons = ["SAVE10", "SAVE15", "FREESHIP", "WELCOME", "STUDENT5", None, None, None, None]

    def choose_user() -> int:
        if rng.random() < 0.28:
            return rng.choice(heavy_users)
        return rng.randint(1, N_USERS)

    with engine.begin() as conn:
        while order_id <= N_ORDERS:
            order_rows.clear()
            item_rows.clear()
            payment_rows.clear()

            batch_end = min(order_id + BATCH - 1, N_ORDERS)
            for oid in range(order_id, batch_end + 1):
                uid = choose_user()
                created = orders_base + timedelta(days=rng.randint(0, 700), seconds=rng.randint(0, 86399))
                status = rng.choices(statuses, weights=status_weights, k=1)[0]
                note = None if rng.random() < 0.78 else r_text(rng, words=12)
                coupon = rng.choice(coupons)

                ship_addr = default_address_for_user.get(uid)
                if ship_addr is None:
                    ship_addr = rng.randint(1, address_id - 1)

                order_rows.append({
                    "id": oid,
                    "user_id": uid,
                    "shipping_address_id": ship_addr,
                    "created_at": created,
                    "status": status,
                    "note": note,
                    "coupon_code": coupon,
                })

                # Items
                n_items = rng.randint(*ITEMS_PER_ORDER)
                for _ in range(n_items):
                    pid = rng.randint(1, N_PRODUCTS)
                    qty = rng.randint(1, 4)
                    unit_price = rng.randint(199, 199_99)
                    item_rows.append({
                        "id": item_id,
                        "order_id": oid,
                        "product_id": pid,
                        "qty": qty,
                        "unit_price_cents": unit_price,
                    })
                    item_id += 1

                # Payments for most orders
                if rng.random() < PAYMENT_RATE:
                    p_status = rng.choices(payment_statuses, weights=payment_status_weights, k=1)[0]
                    paid_at = None
                    if p_status == "paid":
                        paid_at = created + timedelta(minutes=rng.randint(1, 180))
                    elif p_status == "refunded":
                        paid_at = created + timedelta(days=rng.randint(1, 90))

                    amount = sum(r["qty"] * r["unit_price_cents"] for r in item_rows[-n_items:])

                    payment_rows.append({
                        "id": payment_id,
                        "order_id": oid,
                        "provider": rng.choice(payment_providers),
                        "status": p_status,
                        "paid_at": paid_at,
                        "amount_cents": amount,
                    })
                    payment_id += 1

            conn.execute(insert(Order), order_rows)
            conn.execute(insert(OrderItem), item_rows)
            if payment_rows:
                conn.execute(insert(Payment), payment_rows)

            order_id = batch_end + 1
            if (order_id - 1) % (BATCH * 5) == 0:
                print(f"  inserted orders: {order_id - 1:,}")

    # -----------------
    # Seed events
    # -----------------
    print(f"Seeding events: {N_EVENTS:,}")
    event_rows: List[Dict[str, Any]] = []
    event_id = 1
    with engine.begin() as conn:
        while event_id <= N_EVENTS:
            event_rows.clear()
            batch_end = min(event_id + BATCH - 1, N_EVENTS)
            for eid in range(event_id, batch_end + 1):
                uid = choose_user()
                created = users_base + timedelta(days=rng.randint(0, (now - users_base).days), seconds=rng.randint(0, 86399))
                event_rows.append({
                    "id": eid,
                    "user_id": uid,
                    "event_type": rng.choice(event_types),
                    "created_at": created,
                })
            conn.execute(insert(Event), event_rows)
            event_id = batch_end + 1

    # -----------------
    # Create indexes after seeding
    # -----------------
    print("Creating indexes...")
    with engine.begin() as conn:
        for idx in INDEX_DEFS:
            idx.create(bind=conn, checkfirst=True)

        # Help SQLite planner
        conn.execute(text("ANALYZE;"))

    print(f"Done. Created and seeded {DB_PATH}")


if __name__ == "__main__":
    main()