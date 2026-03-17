from functionality import *   

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