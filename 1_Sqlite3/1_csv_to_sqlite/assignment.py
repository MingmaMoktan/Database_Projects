# Create a script that
# 1. Reads contents of the files users.csv, purchases.csv and purchaseParts.csv
# 2. Creates a new database called purchases.db
# 3. Creates tables for each of the csv files called: users, purchases and purchaseParts
# 4. Inserts the data for each of the tables
# 5. Finally, join data from all the 3 tables and print it all out. Order the data by "users.email" ascending.
#    Expected output should be like this:
#      (3, 'danny@boy.com', 1, 3, 1, 1, 'Poster')
#      (3, 'danny@boy.com', 2, 3, 2, 2, 'Nail Clipper')
#      (5, 'f51wt@mymail.com', 4, 5, 5, 4, 'Monitor')
#      (5, 'f51wt@mymail.com', 4, 5, 6, 4, 'Keyboard')
#      (2, 'my@mail.com', 3, 2, 3, 3, 'Laptop')
#      (2, 'my@mail.com', 3, 2, 4, 3, 'Monitor')

# Note that the CSV files contains the data format and constraints inside the title.

# Other requirements:
# You need to dynamically create the tables and their content. You CANNOT just do if statements to check for name of the file and then create the table and insert the data manually.
# You NEED to write the script yourself, you cannot use any pre-created library other than sqlite3
# You need to create a function called dropAndCreateTable that accepts the name of the table and table fields in some format. That function needs to drop the table first if it exists (DROP TABLE IF EXISTS tableName) and then needs to create the passed table with the fields given. Note that neither of the DROP TABLE or CREATE TABLE commands work with the ? substitution.
# You need to create a function called insertData that accepts the name of the table and table data in some format. That function needs to insert the passed data into the given table.

import sqlite3 # For communicating with sqlite databases

database = "purchases.db"
filenames = [ "users.csv", "purchases.csv", "purchaseParts.csv"]

connection = sqlite3.connect(database) # Initialize connection to database, we could also use the parameter :memory:
cursor = connection.cursor() # Fetch cursor from connection

def dropAndCreateTable(tableName, tableFields):
  # Drop table if it exists
  droptableSQL = "DROP TABLE IF EXISTS " + tableName
  cursor.execute(droptableSQL)
  connection.commit()
  # Create table
  createtableSQL = "CREATE TABLE " + tableName + " (" + tableFields + ")"
  cursor.execute(createtableSQL)
  connection.commit()
  
def insertData(tableName, tableData):
  # Prepare SQL statement for inserting data
  placeholders = ",".join(["?"] * len(tableData))
  insertSQL = "INSERT INTO " + tableName + " VALUES (" + placeholders + ")"
  cursor.execute(insertSQL, tableData)
  connection.commit()


# Loop through all the files
for filename in filenames:
  file = open(filename, "r") # Open a file
  lines = file.readlines() # Lines of the file are now stored here
  # print("File: " + filename)
  index = 0 # Create index variable so we can determine if it is header or actual data for the table

  # Loop through lines inside the files
  for line in lines:
    tableName = filename.replace(".csv", "") # Name of the current table
    # print("Table name: " + tableName)
    # print("line: " + line)
    # print("index: " + str(index))
    
    # If index is 0, this is header for the table. In this case, we need to split the columns by comma
    if index == 0:
      tableFields = line.strip() # Remove whitespace and replace newline characters
      dropAndCreateTable(tableName, tableFields) # Drop and create the table using the function dropAndCreateTable(...)
    else:
      tableData = line.strip().split(",") # Split the data by comma
      insertData(tableName, tableData) # Insert the data into the corresponding table using function insertData(...)
    # and drop + create the table using the function dropAndCreateTable(...)
    # If index is 1, this is data for a table. Use function insertData(...) to insert the data into the
    # corresponding table

    index = index + 1

# Part 2: We just need to create a JOIN statement to get all the results and then loop them and 

joinSQL ="""
SELECT users.userId, users.email, purchases.purchaseId, purchases.userId, purchaseParts.purchasePartId, purchaseParts.purchaseId, purchaseParts.item 
FROM users
JOIN purchases ON users.userId = purchases.userId
JOIN purchaseParts ON purchases.purchaseId = purchaseParts.purchaseId
ORDER BY users.email ASC
"""

cursor.execute(joinSQL)
results = cursor.fetchall() # Fetch all results

# print out the results
for row in results:
    print(row)
    
# Close the connection
connection.close()