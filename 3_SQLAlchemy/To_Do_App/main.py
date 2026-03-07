import os
import sys
from database import *
from sqlalchemy import select

def app():
    print("Welcome to To-Do App! version 1.0")
    while True:
        print('''
              What do you want to do today?
              1. View todo items
              2. Create new todo item
              3. Remove item
              4. Exit
              ''')
        
        selection = input()
        
        if selection == "1": show_items()
        elif selection == "2": create_new_item()
        elif selection == "3": remove_item()
        elif selection == "4": sys.exit("Goodbye!")

def show_items():
    print("Here are all your items: ")
    with Session() as session:
        stmt = select(Item)
        items = session.scalars(stmt).all()
        if len(items)<=0:
            print("No items to show")
        else:
            for item in items:
                print(f"{item.item_id}: {item.name}")

def create_new_item():
    print("Name for the item:")
    name = input()
    with Session() as session:
        new_item = Item(name=name)
        session.add(new_item)
        session.commit()
        
        
def remove_item():
    print("Give ID to remove item:")
    id = input()
    with Session() as session:
        stmt = select(Item).where(Item.item_id == id)
        item = session.scalar(stmt)
        if item is None:
            print("No such item")
        else:
            session.delete(item)
            session.commit()
            print(f"Item with id {id} removed")

def main():
    app()
    
if __name__ == "__main__":
    main()