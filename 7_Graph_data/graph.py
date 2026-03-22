import argparse
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, UniqueConstraint, select
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column

engine = create_engine("sqlite+pysqlite:///graph.db")

class Base(DeclarativeBase):
    pass

class Node(Base):
    __tablename__ = 'nodes'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True, index=True)
    
class Relationship(Base):
    __tablename__ = 'relationship'
    id: Mapped[int] = mapped_column(primary_key=True)
    from_id: Mapped[int] = mapped_column(ForeignKey('nodes.id'))
    to_id: Mapped[int] = mapped_column(ForeignKey('nodes.id'))
    type: Mapped[str] = mapped_column(index=True)
    __table_args__ = (UniqueConstraint('from_id', 'to_id', 'type'),)
    
Base.metadata.create_all(engine)
Session = sessionmaker(engine)

def main():
    # Setting up Parser
    parser = argparse.ArgumentParser(description="Simple Graph Relationships")
    parser.add_argument('--add-node', action='store_true')
    parser.add_argument('--add-relationship', action='store_true')
    parser.add_argument('--routes-from')
    parser.add_argument('--title')
    parser.add_argument('--from', dest='f')
    parser.add_argument('--to')
    parser.add_argument('--type')
    parser.add_argument('--list-nodes', action='store_true')
    args = parser.parse_args()

    with Session() as session:
        def get_node(title):
            stmt = select(Node).where(Node.title == title)
            result = session.scalars(stmt).first()
            if result is None:
                result = Node(title=title)
                session.add(result)
                session.commit()
            return result

        # This will add the node
        if args.add_node:
            if not args.title:
                print("Error: --title is required.")
                return
            
            stmt = select(Node).where(Node.title == args.title)
            if session.scalars(stmt).first():
                print(f"Node '{args.title}' already exists.")
            else:
                session.add(Node(title=args.title))
                session.commit()

        # This will add relationship
        elif args.add_relationship:
            if not all([args.f, args.to, args.type]):
                print("Error: --from, --to, and --type are required.")
                return
            
            # This will automatically create the node if doesn't exist
            u = get_node(args.f)
            v = get_node(args.to)
            
            # Checking the relationship
            rel_stmt = select(Relationship).where(
                Relationship.from_id == u.id, 
                Relationship.to_id == v.id, 
                Relationship.type == args.type
            )
            if not session.scalars(rel_stmt).first():
                session.add(Relationship(from_id=u.id, to_id=v.id, type=args.type))
                session.commit()

        # Listing the routes
        elif args.routes_from:
            stmt = select(Node).where(Node.title == args.routes_from)
            node = session.scalars(stmt).first()
            
            if not node:
                print(f"Error: Node '{args.routes_from}' does not exist.")
            else:
                rel_stmt = select(Relationship).where(Relationship.from_id == node.id)
                for rel in session.scalars(rel_stmt):
                    # Fetch target node title
                    target = session.get(Node, rel.to_id)
                    print(f"{node.title} -[{rel.type}]-> {target.title}")
                    
        elif args.list_nodes:
            # Select all nodes and order them alphabetically
            stmt = select(Node).order_by(Node.title)
            nodes = session.scalars(stmt).all()
            
            if not nodes:
                print("The database is empty.")
            else:
                print("Nodes in database:")
                for node in nodes:
                    print(f"- {node.title} (ID: {node.id})")


if __name__ == "__main__":
    main() 