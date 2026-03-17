import os
import sys
from database import *
from sqlalchemy import select, delete
import hashlib

# I have also tried to implement the password hashing for the practice in this assignment.
def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()

# Registering the user
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

# If the user exists then logging in the user
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

# Todo menu        
def todo_menu(user_id: int):
    while True:
        print('''
              ToDo Dashboard
                Select an option:
                1. View ToDo Items
                2. Add ToDo Item
                3. Delete ToDo Item
                4. Share a Note
                5. Logout
              ''')
        option = input("Option: ")
        if option == "1":
            view_items(user_id)
        elif option == "2":
            add_item(user_id)
        elif option == "3":
            delete_item(user_id)
        elif option == "4":
            share_note(user_id)
        elif option == "5":
            print("Logging out...")
            break
        else:
            print("Invalid option. Please try again.")

# Viewing the items
def view_items(user_id: int):
    with Session() as session:
        stmt = select(User).where(User.user_id==user_id)
        user = session.scalar(stmt)
        if not user or not user.user_item:
            print("No items found.")
            return
        
        print("Viewing your personal notes:")
        my_notes = [ui for ui in user.user_item if ui.is_owner]
        if not my_notes:
            print("No personal notes created.")
        else:
            for ui in my_notes:
                print(f"{ui.item_id} {ui.item.title} - {ui.item.description} (Created at: {ui.item.created_at})")
        
        print("Viewing your shared notes:")
        shared_notes = [ui for ui in user.user_item if not ui.is_owner]
        if not shared_notes:
            print("No personal notes created.")
        else:
            for ui in shared_notes:
                owner_stmt = select(User_Item).where(
                    User_Item.item_id == ui.item_id, 
                    User_Item.is_owner == True
                )
                
                owner_link = session.scalar(owner_stmt)
                sharer_name = owner_link.user.name if owner_link else "Unknown"
                print(f"{ui.item_id} {ui.item.title} - {ui.item.description} (Created at: {ui.item.created_at}) (shared by: {sharer_name})")
        

# Adding the todo items            
def add_item(user_id: int):
    with Session() as session:
        title = input("Title:")
        description = input("Description:")
        
        new_item = Item(title=title, description=description)
        
        user_link = User_Item(user_id=user_id, item=new_item, is_owner=True) # Here we mention the owner of the note by setting the is_owner=True
        session.add(user_link)
        session.commit()
        print("ToDo item added successfully!")

# Deleting the todo items
def delete_item(user_id: int):
    view_items(user_id)
    item_id = int(input("Enter the ID of the item to delete: "))
    with Session() as session:
        link = session.scalar(
            select(User_Item).where(User_Item.user_id == user_id, User_Item.item_id == item_id)
        )
        if not link:
            print("Item not found.")
            return

        if link.is_owner:
            # Delete the actual item for all
            session.delete(link.item)
            print("Note deleted for you and everyone you shared it with.")
        else:
            # Or just unlink
            session.delete(link)
            print("Note removed from your shared list.")
        
        session.commit()


def share_note(user_id: int):
    view_items(user_id)
    note_id = int(input("Enter the ID of the note to share: "))
    receipient_name = input("Username of person whom note is shared: ")
    
    with Session() as session:
        stmt_re = select(User).where(User.name==receipient_name)
        recipient = session.scalar(stmt_re)
        if not recipient:
            print("Recipient not found.")
            return
        
        stmt_ow = select(User_Item).where(
            User_Item.item_id==note_id,
            User_Item.user_id==user_id,
            User_Item.is_owner==True
        )
        
        owner = session.scalar(stmt_ow)
        if not owner:
            print("Owner does not exist")
            return
        # Creating the link
        try:
            new_share = User_Item(user_id=recipient.user_id, item_id=note_id, is_owner=False)
            session.add(new_share)
            session.commit()
            print(f"Success! Note shared with {receipient_name}.")
        except Exception:
            print("Note is already shared with this user.")