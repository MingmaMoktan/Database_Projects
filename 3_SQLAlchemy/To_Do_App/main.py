import os
import sys

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
    print("Showed new item")

def create_new_item():
    print("Created new item")

def remove_item():
    print("Removed item")

def main():
    app()
    
if __name__ == "__main__":
    main()