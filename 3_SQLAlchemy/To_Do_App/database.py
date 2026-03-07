from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, mapped_column, Mapped

engine = create_engine("sqlite+pysqlite:///todo.db", echo=False)

class Base(DeclarativeBase):
    pass

class Item(Base):
    __tablename__ = "items"
    
    item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=True)
    
Base.metadata.create_all(engine)
Session = sessionmaker(engine)