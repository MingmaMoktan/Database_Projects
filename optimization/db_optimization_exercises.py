"""
exercises.py
----------------
Intentionally slow SQLAlchemy database functions to optimize.
Version 1.0.0 of the exercise.

Workflow:
1) On top of each exercise function, change the run_xx to True (it will time the function + show number of SQL queries executed)
2) Take a note of the time spent in the provided comment slots
3) Create optimized versions
4) Record optimized time in the provided comment slots

Requires:
  pip install sqlalchemy

Run:
  python db_optimization_exercises.py

Assumes:
  workshop.db exists (created by db_optimization_seed.py)
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

from sqlalchemy import ( Boolean, DateTime, ForeignKey, Integer, String, Text, create_engine, select, func, text)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy import event

# Change this line in exercises.py
DB_URL = "sqlite:////home/david_salome/mygitfolder/Database_Projects/optimization/workshop.db"

# -----------------------
# ORM Models (must match seeder)
# DO NOT EDIT!
# -----------------------

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[Any] = mapped_column(DateTime, nullable=False)


class Address(Base):
    __tablename__ = "addresses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)
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
    created_at: Mapped[Any] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
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
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    paid_at: Mapped[Any] = mapped_column(DateTime, nullable=True)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[Any] = mapped_column(DateTime, nullable=False)




# -----------------------
# EXERCISES (bad functions to optimize)
# -----------------------

# Rules / Workflow:
# - Don’t change what the function returns. Only change HOW it does it.
# - Aim to reduce both time and query count.
# - Change the "run_xx" variable to True to measure its performance
# - Use SQL WHERE / JOIN / GROUP BY / LIMIT.
# - Fix N+1 with joins


# ----
# Exercise 1) Python filtering instead of SQL
# ----
run_01 = False
def bad_01_active_user_emails_python_filter(session: Session) -> List[str]:
    """
    Task: Return emails of active users.
    Bad pattern: loads ALL users, filters in Python.

    Original run time and queries:  0.2684s   queries=1
    Optimized run time and queries:  0.0566s   queries=1
    Run time improvement = ((original-optimized) / original) * 100 = 72%
    """

    # Original code (comment this out with ''' ''')
    # stmt = select(User)
    # users = session.scalars(stmt).all()
    # active_users = []
    # for user in users:
    #     if user.is_active:
    #         active_users.append(user)
    # return active_users

    # Your Optimized Solution
    stmt = select(User.email).where(User.is_active==True)
    users = session.scalars(stmt).all()
    return len(users)
    
# ----
# Exercise 2) Fetching too many columns
# ----
run_02 = False
def bad_02_user_list_fetch_whole_objects(session: Session) -> List[Tuple[int, str]]:
    """
    Task: Return (id, email) for the first 50_000 users ordered by id.
    Bad pattern: loads full ORM entities when only two columns needed.
    
    Original run time and queries: 0.2560s   queries=1
    Optimized run time and queries: 0.0596s   queries=1
    Run time improvement = ((original-optimized) / original) * 100 = 68%
    """

    # Original code (comment this out with ''' ''')
    # stmt = select(User).order_by(User.id).limit(50_000)
    # users = session.execute(stmt).scalars().all()
    # return_users = []
    # for user in users:
    #     return_users.append((user.id, user.email))
    # return return_users

    # Your Optimized Solution
    stmt = select(User.id, User.email).order_by(User.id).limit(50_000)
    users = session.execute(stmt).all()
    return users

# ----
# Exercise 3) Aggregation in Python
# ----
run_03 = False
def bad_03_total_revenue_python_sum(session: Session) -> int:
    """
    Task: Calculate the total revenue in ALL order_items: for each order item, calculate qty * unit_price_cents, sum that all up
    Bad pattern: load all rows then sum in Python.

    Original run time and queries: 1.3776s   queries=1
    Optimized run time and queries: 0.036s (1 query)
    Run time improvement = ((original-optimized) / original) * 100 = 98%
    """

    # Original code (comment this out with ''' ''')
    # stmt = select(OrderItem.qty, OrderItem.unit_price_cents)
    # items = session.execute(stmt).all()
    # return sum(qty * price for qty, price in items)
    
    # Your Optimized Solution
    stmt = select(func.sum(OrderItem.qty*OrderItem.unit_price_cents))
    item = session.scalar(stmt)
    print(f'The total revenue is {item}')
    return item
    

# ----
# Exercise 4) Fetching records individually from database in a loop
# ----
run_04 = False
def bad_04_fetch_products_by_ids_in_loop(session: Session) -> List[str]:
    """
    Task: Find 300 products (ordered by Product.id in ascending order) and return their SKU numbers in a list
    Bad pattern: one query per id.

    Original run time and queries: 0.0423s   queries=301
    Optimized run time and queries: 0.0087s (1 query)
    Run time improvement = ((original-optimized) / original) * 100 = 95%
    """
    
    # Original code (comment this out with ''' ''')
    stmt = select(Product.id).order_by(Product.id.asc()).limit(300)
    product_ids = session.execute(stmt).scalars().all()
    skus = []
    for pid in product_ids:
        sku = session.execute(select(Product.sku).where(Product.id == pid)).scalar_one()
        skus.append(sku)
    return skus

    # Your Optimized Solution


# ----
# Exercise 5) Existence check done the slow way
# ----
run_05 = True
def bad_05_check_user_email_exists_slow(session: Session) -> bool:
    """
    Task: Return True if any active user has an email ending with 'school.fi' (domain check).
    Bad pattern: loads lots of rows, does string check in Python.

    Original run time and queries: 0.0416s   queries=1
    Optimized run time and queries: 0.0567s   queries=1
    Run time improvement = ((original-optimized) / original) * 100 = 91%
    """

    # Original code (comment this out with ''' ''')
    # stmt = select(User.email, User.is_active)
    # users = session.execute(stmt).all()
    # for email, active in users:
    #     if active and email.endswith("school.fi"):
    #         return True
    # return False

    # Your Optimized Solution
    stmt = select(User.id).where(User.is_active==True,User.email.like('%school.fi'))
    user = session.scalar(stmt)
    return True if user else False

# ----
# Exercise 6) Missing index on foreign key used in IN clause
# ----
run_06 = False
def bad_06_count_orders_without_index(session: Session) -> int:
    """
    Task: Count orders for the first 5000 users (user_ids 1-5000).
    Bad pattern: query without index on user_id column - requires full table scan for IN clause.
    Solution: Add index: CREATE INDEX idx_orders_user_id ON orders(user_id)
    
    This query benefits greatly from an index because it needs to match many user_ids.
    Without an index, the database must scan every row. With an index, it can quickly
    find matching rows for each user_id.
    
    Original run time and queries: 0.0342s   queries=1
    Optimized run time and queries: 0.0274s   queries=2
    Run time improvement = ((original-optimized) / original) * 100 = 75%
    """

    # In this exercise, you can see the answer below and can test the search with and without index

    # Drop index to clean up
    '''
    session.execute(text("DROP INDEX IF EXISTS idx_orders_user_id"))
    session.commit()
    '''
    

    # Create index if it doesn't exist (Run with this and leave uncommented after testing the drop index above)
    
    '''session.execute(text("CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)"))
    session.commit()'''
    
    
    # Get first 5000 user IDs and find their orders
    user_ids = list(range(1, 5001))
    stmt = select(func.count()).select_from(Order).where(Order.user_id.in_(user_ids))
    result = int(session.execute(stmt).scalar_one())
    return result


# ----
# Exercise 7) N+1: users -> orders
# ----
run_07 = False
def bad_07_users_with_order_counts_n_plus_one(session: Session) -> List[Tuple[int, int]]:
    """
    Task: Return (user_id, order_count) for 3,000 users who have at least one order.

    Bad pattern:
    - One query to fetch user ids
    - One COUNT query per user (N+1)

    Hint: order_count is the occurrence of orders with that user_id, use group by
    Hint 2: To calculate the amount of orders inside the select: func.count(Order.id).label("order_count")

    Original run time and queries: 28.2320s   queries=3037
    Optimized run time: 0.0061s (1 query)
    Run time improvement = ((original-optimized) / original) * 100 = 96%
    """

    # Original code (comment this out with ''' ''')
    stmt = select(User.id).order_by(User.id)
    user_ids = session.execute(stmt).scalars().all()
    out: List[Tuple[int, int]] = []
    for uid in user_ids:
        cnt = session.execute(select(func.count(Order.id)).where(Order.user_id == uid)).scalar_one()
        if cnt > 0:
            out.append((uid, int(cnt)))
        if len(out) >= 3_000:
            break
    return out

    # Your Optimized Solution (1 query!)


# ----
# Exercise 8) Sorting in Python instead of SQL, N+1
# ----
run_08 = False
def bad_08_top_customers_by_orders_python_sort(session: Session) -> List[Tuple[int, int]]:
    """
    Task: Return top 10 users with the highest amount (count) of orders,
          in a list containing tuple of (user_id, order_count) by number of orders.
          For example: [ (1, 73), (231, 71) ... ]
    Bad pattern: compute counts in N+1 style then sort in Python.

    Original run time and queries: 1.15s (15001 queries)
    Optimized run time and queries: 0.012s (1 query)
    Run time improvement = ((original-optimized) / original) * 100 = 99%
    """

    # Original code (comment this out with ''' ''')
    stmt = select(User.id)
    user_ids = session.execute(stmt).scalars().all()
    counts: List[Tuple[int, int]] = []
    for uid in user_ids:
        cnt = session.execute(select(func.count()).select_from(Order).where(Order.user_id == uid)).scalar_one()
        counts.append((uid, int(cnt)))
    counts.sort(key=lambda x: x[1], reverse=True)
    return counts[:10]

    # Your Optimized Solution











# -----------------------
# Timing + query counting
# DO NOT EDIT!
# -----------------------

@dataclass
class RunResult:
    name: str
    seconds: float
    queries: int


class QueryCounter:
    def __init__(self) -> None:
        self.count = 0

    def reset(self) -> None:
        self.count = 0

    def before_cursor_execute(self, conn, cursor, statement, parameters, context, executemany):
        self.count += 1


def timed(session_factory: Callable[[], Session], fn: Callable[[Session], Any], repeats: int = 3) -> RunResult:
    total = 0.0
    qc = session_factory.__dict__.get("_query_counter")  # type: ignore[attr-defined]
    if qc is None:
        raise RuntimeError("QueryCounter missing on session factory")

    for _ in range(repeats):
        with session_factory() as s:
            qc.reset()
            t0 = time.perf_counter()
            fn(s)
            t1 = time.perf_counter()
            total += (t1 - t0)

    return RunResult(fn.__name__, total / repeats, qc.count)


def make_session_factory():
    engine = create_engine(DB_URL, future=True)

    qc = QueryCounter()
    event.listen(engine, "before_cursor_execute", qc.before_cursor_execute)

    def _factory() -> Session:
        return Session(engine)

    # stash counter for timed()
    _factory.__dict__["_query_counter"] = qc  # type: ignore[attr-defined]
    return _factory

# -----------------------
# Runner
# DO NOT EDIT!
# -----------------------

def main() -> None:
    session_factory = make_session_factory()

    # Quick sanity check DB exists
    with session_factory() as s:
        n_users = s.execute(select(func.count()).select_from(User)).scalar_one()
        print(f"DB connected. users={int(n_users):,}")

    FUNCTIONS: List[Tuple[bool, Callable[[Session], Any], str]] = [
        (run_01,  bad_01_active_user_emails_python_filter),
        (run_02,  bad_02_user_list_fetch_whole_objects),
        (run_03,  bad_03_total_revenue_python_sum),
        (run_04,  bad_04_fetch_products_by_ids_in_loop),
        (run_05,  bad_05_check_user_email_exists_slow),
        (run_06,  bad_06_count_orders_without_index),
        (run_07,  bad_07_users_with_order_counts_n_plus_one),
        (run_08,  bad_08_top_customers_by_orders_python_sort),
    ]

    repeats = 1 # Can be increased to run the function multiple twices and to calculate the average of the execution time
    print(f"\nRunning enabled functions (repeats={repeats})...\n")

    results: List[RunResult] = []
    for enabled, fn in FUNCTIONS:
        if not enabled:
            continue
        res = timed(session_factory, fn, repeats=repeats)
        results.append(res)
        print(f"{res.name:<45}  {res.seconds:>8.4f}s   queries={res.queries}")


if __name__ == "__main__":
    main()