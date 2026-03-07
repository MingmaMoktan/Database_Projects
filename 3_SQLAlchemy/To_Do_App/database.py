from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, mapped_column, Mapped
from pathlib import Path

DB_PATH = Path("/home/david_salome/mygitfolder/Database_Projects/3_SQLAlchemy/To_Do_App/todo.db")

engine = create_engine(f"sqlite+pysqlite:///{DB_PATH}", echo=False)

class Base(DeclarativeBase):
    pass

class Item(Base):
    __tablename__ = "items"
    
    item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=True)
    
Base.metadata.create_all(engine)
Session = sessionmaker(engine)