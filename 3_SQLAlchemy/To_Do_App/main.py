import os
import sys
from database import *
from sqlalchemy import select, delete
import hashlib

# I have also tried to implement the password hashing for the practice in this assignment.
def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()

def register_user():
    print("Register to create new account")
    name = input("Username: ")
    password = input("Password: ")
    
    hashed_password = hash_password(password)
    
    with Session() as session:
        stmt = select(User).where(User.name == name)
        user = session.scalar(stmt)
        if user:
            print("Username already exists. Please choose a different username.")
            return
        new_user = User(name=name, password=hashed_password)
        session.add(new_user)
        session.commit()
        print("Registration successful! You can now log in.")


def login():
    print("Login")
    name = input("Username: ")
    password = input("Password: ")
    
    hashed_password = hash_password(password)
    
    with Session() as session:
        stmt = select(User).where(User.name == name, User.password == hashed_password)
        user = session.scalar(stmt)
        if user:
            print("Login successful!")
            return user.user_id
        else:
            print("Invalid username or password.")
            return None
        
def todo_menu(user_id: int):
    while True:
        print('''
              ToDo Dashboard
                Select an option:
                1. View ToDo Items
                2. Add ToDo Item
                3. Delete ToDo Item
                4. Logout
              ''')
        option = input("Option: ")
        if option == "1":
            view_items(user_id)
        elif option == "2":
            add_item(user_id)
        elif option == "3":
            delete_item(user_id)
        elif option == "4":
            print("Logging out...")
            break
        else:
            print("Invalid option. Please try again.")

def view_items(user_id: int):
    with Session() as session:
        stmt = select(User).where(User.user_id==user_id)
        user = session.scalar(stmt)
        if not user:
            print("User not found.")
            return
        if not user.user_item:
            print("No ToDo items found.")
            return
        print("Your ToDo Items:")
        for ui in user.user_item:
            print(f"{ui.item_id} {ui.item.title} - {ui.item.description} (Created at: {ui.item.created_at})")
            
def add_item(user_id: int):
    with Session() as session:
        title = input("Title:")
        description = input("Description:")
        
        new_item = Item(title=title, description=description)
        
        user_link = User_Item(user_id=user_id, item=new_item)
        session.add(user_link)
        session.commit()
        print("ToDo item added successfully!")

def delete_item(user_id: int):
    print('''
          Delete Options
          1. Delete one item
          2. Delete all items
          ''')
    option = input ("Option: ")
    if option == "1":
        with Session() as session:
            item_id = input("Enter the ID of the item to delete: ")
            stmt = select(User_Item).where(User_Item.user_id == user_id, User_Item.item_id == item_id)
            
            user_item = session.scalar(stmt)
            
            if user_item:
                session.delete(user_item.item)
                session.commit()
                print("ToDo item deleted successfully!")
            else:
                print("Item not found or does not belong to you.")
    
    elif option == "2":
        with Session() as session:
            # This fetches the item_id of all items linked to the user
            stmt1 = select(User_Item.item_id).where(User_Item.user_id == user_id)
            
            # This then deletes all the items for the user_id by matching the item_id with the user_id
            stmt2 = delete(Item).where(Item.item_id.in_(stmt1))
            session.execute(stmt2)
            session.commit()
            print("All ToDo items deleted successfully!")
    

def main():
    while True:
        print('''
              Welcome to ToDo APP
              Select an option:
                1. Register
                2. Login
                3. Exit
              ''')
        option = input("Option: ")
        if option == "1":
            register_user()
        elif option == "2":
            uid = login()
            if uid:
                todo_menu(uid)
        elif option == "3":
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()