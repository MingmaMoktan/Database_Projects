import pandas as pd
import os

# Set to False to disable printing out the dataframe, columns and results.
# Coderunner will set this to False while running your code
# to test out your functions without having any unnecessary prints.
debugMode = True

# Load the data from the table into a pandas DataFrame
from sqlite3 import connect
engine = connect(':memory:')
df = pd.read_csv('sales_data.csv', encoding='UTF-8')
df.to_sql('sales', engine)

if debugMode:
  # Print all data in the dataframe
  print("DATAFRAME:")
  print(df)
  # Print all columns of the dataframe
  columns = ""
  for column in df:
    columns += f",{column}"
  print("COLUMNS OF THE DATAFRAME:")
  print(columns[1:])

def getOneRow() -> pd.DataFrame:
  # Get the first row
  sql = "SELECT * FROM sales LIMIT 1"
  df = pd.read_sql_query(sql, engine)
  # Print the column and their data one by one
  for column in df:
    print(f"{column}: {df[column][0]}")
if debugMode:
  print("EXAMPLE DATA:")
  print(getOneRow())
  

########################
# EXERCISES START HERE #
########################

def assignment1() -> pd.DataFrame:
  '''
    Get columns ORDERNUMBER, CUSTOMERNAME and order by CUSTOMERNAME in ascending order.
    Limit results to 5.
    Return back the resulting dataframe.
  '''
  sql = "SELECT ORDERNUMBER, CUSTOMERNAME FROM sales ORDER BY CUSTOMERNAME ASC LIMIT 5"
  df = pd.read_sql_query(sql, engine)
  return df

if debugMode:
  print(f"{os.linesep}--------------")
  print("ASSIGNMENT 1:")
  print("EXPECTED OUTPUT:")
  print("   ORDERNUMBER    CUSTOMERNAME")
  print("0        10306  AV Stores, Co.")
  print("1        10306  AV Stores, Co.")
  print("2        10306  AV Stores, Co.")
  print("3        10332  AV Stores, Co.")
  print("4        10332  AV Stores, Co.")
  print("YOUR OUTPUT:")
  print(assignment1())

def assignment2() -> pd.DataFrame:
  '''
    Get the total amount of sales operations made in year 2005
    NOTE: NOT sum, just the amount of sales
    Year should be contained within column YEAR the amount of sales in column TOTAL_SALES
    Return back the resulting dataframe.
  '''
  sql = "SELECT YEAR_ID as YEAR, COUNT(*) AS TOTAL_SALES FROM sales WHERE YEAR_ID = 2005 GROUP BY YEAR_ID"
  df = pd.read_sql_query(sql, engine)
  return df

if debugMode:
  print(f"{os.linesep}--------------")
  print("ASSIGNMENT 2:")
  print("EXPECTED OUTPUT:")
  print("   YEAR  TOTAL_SALES")
  print("0  2005          478")
  print("YOUR OUTPUT:")
  print(assignment2())

def assignment3(year : int) -> pd.DataFrame:
  '''
    This is the same as assignment2 but return back the amount of sales made in the year
    given as a parameter for this function.
  '''
  sql = f"SELECT YEAR_ID as YEAR, COUNT(*) AS TOTAL_SALES FROM sales WHERE YEAR_ID = {year} GROUP BY YEAR_ID"
  df = pd.read_sql_query(sql, engine)
  return df

if debugMode:
  print(f"{os.linesep}--------------")
  print("ASSIGNMENT 3:")
  print("EXPECTED OUTPUT WITH YEAR SET TO 2003:")
  print("   YEAR  TOTAL_SALES")
  print("0  2003         1000")
  print("YOUR OUTPUT:")
  print(assignment3(2003))

def assignment4() -> pd.DataFrame:
  '''
    Get the amount of money made in each year.
    You can get the amount by SUMming up PRICEEACH * QUANTITYORDERED
    Column YEAR should contain the year and column TOTAL_MONEY the total money made in that year.
    Sort the results by TOTAL_MONEY in descending order.
    Limit the results to 3
    Return back the dataframe.
  '''
  sql = """
  SELECT YEAR_ID as YEAR, SUM(PRICEEACH * QUANTITYORDERED) AS TOTAL_MONEY
  FROM sales
  GROUP BY YEAR_ID
  ORDER BY TOTAL_MONEY DESC
  LIMIT 3
  """
  df = pd.read_sql_query(sql, engine)
  return df

if debugMode:
  print(f"{os.linesep}--------------")
  print("ASSIGNMENT 4:")
  print("EXPECTED OUTPUT:")
  print("   YEAR  TOTAL_MONEY")
  print("0  2004   3913700.87")
  print("1  2003   2898149.94")
  print("2  2005   1479035.98")
  print("YOUR OUTPUT:")
  print(assignment4())

def assignment5(itemName : str, year : int) -> pd.DataFrame:
  '''
    Get the amount of money made from given item during the given year.
    From the original data, use column PRODUCTCODE for the item, for example "S10_1678".
    Column YEAR should contain the year, ITEM the name of the item (PRODUCTCODE), and column TOTAL_MONEY the money made from sales that year.
    TOTAL_MONEY is the same as in assignment4 (SUMming up PRICEEACH * QUANTITYORDERED)
    Return back the resulting dataframe.
  '''
  sql = f"""
  SELECT YEAR_ID as YEAR, PRODUCTCODE AS ITEM, SUM(PRICEEACH * QUANTITYORDERED) AS TOTAL_MONEY
  FROM sales
  WHERE PRODUCTCODE = '{itemName}' AND YEAR_ID = {year}
  GROUP BY YEAR_ID, PRODUCTCODE
  """
  df = pd.read_sql_query(sql, engine)
  return df

if debugMode:
  print(f"{os.linesep}--------------")
  print("ASSIGNMENT 5:")
  print("EXPECTED OUTPUT WITH ITEM 'S10_1678' AND YEAR 2003:")
  print("   YEAR      ITEM  TOTAL_MONEY")
  print("0  2003  S10_1678     31114.01")
  print("YOUR OUTPUT:")
  print(assignment5("S10_1678", 2003))