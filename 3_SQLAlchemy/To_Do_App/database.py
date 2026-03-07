from sqlalchemy import create_engine, ForeignKey
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
    
    items: Mapped[List["Todo_Item"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Todo_Item(Base):
    __tablename__ = "items"
    
    item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now, nullable=True)
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="items")
    
    
Base.metadata.create_all(engine)
Session = sessionmaker(engine)