from __future__ import annotations
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship, sessionmaker
from datetime import datetime


engine = create_engine("sqlite+pysqlite:///carDatabase.db", echo=True)

class Base(DeclarativeBase):
    pass

# Model for user
class User(Base):
    __tablename__ = "users"
    
    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(nullable=False)
    
    user_cars: Mapped[list['UserCar']] = relationship(back_populates="user", cascade="all, delete-orphan")

# Model for car
class Car(Base):
    __tablename__ = "cars"
    
    car_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    manufacturer:Mapped[str] = mapped_column(nullable=False)
    model:Mapped[str] = mapped_column(nullable=False)
    # So here we also need to know that if default=True attribute is given we don't need to add them as args in function
    is_sold:Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=None, nullable=True)
    
    # Python-side link: Car.invoices will return a list of Invoice objects
    invoice: Mapped[list["Invoice"]] = relationship(back_populates="car")
    user_cars: Mapped[list['UserCar']] = relationship(back_populates="car")
    
class UserCar(Base):
    __tablename__ = "user_cars"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.car_id"), primary_key=True)
    
    user: Mapped['User'] = relationship(back_populates="user_cars")
    car: Mapped['Car'] = relationship(back_populates="user_cars")
        
class Invoice(Base):
    __tablename__ = "invoices"
    
    invoice_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.car_id"), nullable=True)
    description: Mapped[str|None] = mapped_column(nullable=True)
    amount: Mapped[float] = mapped_column(nullable=False)
    is_paid: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=False)
    
    car: Mapped["Car"] = relationship(back_populates="invoice")
    
# Until now we have created the tables and schema but we have not created the database.
# So to create the database we need to do the following

Base.metadata.create_all(engine)

Session = sessionmaker(engine)