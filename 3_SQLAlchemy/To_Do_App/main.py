import os
import sys

items = []
current_item_id = 0


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
    if len(items) == 0:
        print("No items to show")
    else:
        for item in items:
            print(f'{item["id"]}. {item["name"]}')

def create_new_item():
    global current_item_id
    current_item_id += 1
    name = input("Enter name of the item: ")
    item = {
        "id": current_item_id,
        "name": name
    }
    items.append(item)
    print("Created new item")

def remove_item():
    if len(items) <= 0:
        print("No items to remove")
        print("Add some items first")
    else:
        print("Which item do you want to remove?")
        id = int(input())
        
        found_index = None # We are defining this because we need the index to remove the item from the list.
        
        for index, item in enumerate(items): # We fetch index based on id and we will use it to remove the item from the list.
            if item["id"] == id:
                found_index = index
        if index is not None:
            items.pop(found_index)
            print("Item was removed")
        else:
            print("Item with given id was not found")

def main():
    app()
    
if __name__ == "__main__":
    main()