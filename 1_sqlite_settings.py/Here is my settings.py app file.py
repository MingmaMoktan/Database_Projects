import sqlite3

connection : sqlite3.Connection = sqlite3.connect("settings.db")

cursor : sqlite3.Cursor = connection.cursor()

cursor.execute('''
               CREATE TABLE IF NOT EXISTS setting (
                   settingId INTEGER PRIMARY KEY AUTOINCREMENT,
                   setting_name TEXT,
                   setting_Info TEXT
               )
               ''')
menu = '''
          What do you want to do?
            1. Store setting
            2. View all settings
            3. View setting
            4. Delete setting
            5. Exit
          '''

while True:
    print(menu)
    input_number = [1,2,3,4,5]
    # Input handling
    try:
        user_input = int(input())
        if user_input not in input_number:
            continue
    except ValueError:
        continue
    # Exit option
    if user_input==5:
        print("Exit")
        break
    # Option 1 Store Setting.
    if user_input==1:
        key = input("What is the key to the setting?")
        value = input("What is the value to the setting?")
        cursor.execute("SELECT setting_name FROM setting WHERE setting_name = ?", (key,))
        result = cursor.fetchone()
        if result:
            cursor.execute('''
                    UPDATE setting 
                    SET setting_info = ? 
                    WHERE setting_name = ?
                ''', (value, key))
            connection.commit()
        else:
            cursor.execute('''
                       INSERT INTO setting (setting_name, setting_info)
                       VALUES (?, ?)
                       ''', (key, value))
            connection.commit()
        continue
    
    # 2 Option 2 View all settings
    elif user_input==2:
        cursor.execute("SELECT * FROM setting")
        all_settings = cursor.fetchall()
        if not all_settings:
            print("No settings found.")
        else:
            for row in all_settings:
                print(f"{row[1]}:, {row[2]}")
        continue
    
    # Option 3 View setting
    elif user_input==3:
        key = input("What setting do you want to view?")
        cursor.execute('''SELECT * FROM setting WHERE setting_name = ?''', (key,))
        result = cursor.fetchone()
        if not result:
            print("Setting does not exist.")
        else:
            print(f"{result[1]}:, {result[2]}")
        continue
    
    # Option 4 Delete setting
    elif user_input==4:
        key = input("What setting do you want to delete?")
        cursor.execute('''SELECT * FROM setting WHERE setting_name = ?''', (key,))
        result = cursor.fetchone()
        if result:
            cursor.execute("DELETE FROM setting WHERE setting_name=?", (key,))
            connection.commit()
        else:
            print("The setting does not exist.")
        continue

cursor.close()
connection.close()