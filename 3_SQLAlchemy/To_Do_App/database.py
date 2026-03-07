from sqlalchemy import create_engine, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, sessionmaker, mapped_column, Mapped, relationship
from pathlib import Path
from typing import List
from datetime import datetime


DB_PATH = Path("/home/david_salome/mygitfolder/Database_Projects/3_SQLAlchemy/To_Do_App/todo.db")
engine = create_engine(f"sqlite+pysqlite:///{DB_PATH}", echo=False)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    
    user_items: Mapped[List["User_Item"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Item(Base):
    __tablename__ = "items"
    
    item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user_items: Mapped["User_Item"] = relationship(back_populates="item", cascade="all, delete-orphan") 

class User_Item(Base):
    __tablename__ = "user_items"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.item_id"), primary_key=True)
    
    user: Mapped["User"] = relationship(back_populates="user_items")
    item: Mapped["Item"] = relationship(back_populates="user_items")

Base.metadata.create_all(engine)
Session = sessionmaker(engine)