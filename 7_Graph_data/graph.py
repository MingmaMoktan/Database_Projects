from __future__ import annotations
from sqlalchemy import create_engine, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship, sessionmaker
from datetime import datetime

engine = create_engine("sqlite+pysqlite:///graph.db", echo=True)
Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class Node(Base):
    __tablename__ = 'nodes'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    
    # Relationship as from adn to for convenience
    

class Relationship(Base):
    __tablename__ = 'relationships'
    id: Mapped = mapped_column(primary_key=True, autoincrement=True)
    from_node_id: Mapped[int] = mapped_column(ForeignKey('nodes.id'), nullable=False)
    to_node_id: Mapped[int] = mapped_column(ForeignKey('nodes.id'), nullable=False)
    type: Mapped[str] = mapped_column(index=True, nullable=False)
    
    