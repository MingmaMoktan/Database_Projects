from pyspark.sql import DataFrame
from pyspark.sql import SparkSession

debugMode = True

class NotImplementedYet:
  def show():
    print("Not implemented yet")

# Create the Spark session
spark: SparkSession = SparkSession.builder \
  .appName("ex3") \
  .config("spark.driver.host", "localhost") \
  .master("local") \
  .getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
spark.conf.set("spark.sql.shuffle.partitions", "5")

df: DataFrame = spark.read\
  .option("header", True)\
  .csv("users.csv")

df_users = df.createOrReplaceTempView('users')

#####################
# ASSIGNMENTS BEGIN #
#####################

def assignment1() -> DataFrame:
  '''
  Get the columns name, age and income for all users with an income greater than 63000.
  Return back the Spark dataframe.
  '''
  sql = '''
  SELECT name, age, income FROM users WHERE income>63000
  '''
  return spark.sql(sql)

def assignment2() -> DataFrame:
  '''
  Get all education levels and the number of users with that education level.
  Columns should be named as education and education_count.
  Hint: GROUP BY
  Sort the results by the count in descending order.
  Return back the Spark dataframe.
  '''
  sql = '''
  SELECT education, COUNT(*) AS educatiion_count 
  FROM users 
  GROUP BY education
  ORDER BY educatiion_count DESC
  '''
  return spark.sql(sql)

def assignment3() -> DataFrame:
  '''
  Find the average income and spending for users living in NYC.
  Name the column income as avg_income and spending as avg_spending.
  Return back the Spark dataframe.
  '''
  sql = '''
  SELECT AVG(income) AS avg_income, AVG(spending) AS avg_spending
  FROM users
  WHERE location = 'NYC'
  '''
  return spark.sql(sql)

def assignment4(location : str) -> DataFrame:
  '''
  Same as assignment 4, but location should be replaced with the passed parameter location.
  '''
  sql = f'''
  SELECT AVG(income) AS avg_income, AVG(spending) AS avg_spending
  FROM users
  WHERE location = '{location}'
  '''
  return spark.sql(sql)

###################
# ASSIGNMENTS END #
###################

if debugMode:
  print("------")
  print("ASSIGNMENT 1 EXPECTED RESULT:")
  print("+--------+---+------+")
  print("|    name|age|income|")
  print("+--------+---+------+")
  print("|    John| 35| 75000|")
  print("|   David| 28| 85000|")
  print("| Michael| 56|120000|")
  print("|Samantha| 50|100000|")
  print("| Matthew| 32| 90000|")
  print("|  Ashley| 45| 80000|")
  print("|  Joshua| 22| 70000|")
  print("+--------+---+------+")
  print("ASSIGNMENT 1 RESULT:")
  print(assignment1().show())

  print("------")
  print("ASSIGNMENT 2 EXPECTED RESULT:")
  print("+-----------+---------------+")
  print("|  education|education_count|")
  print("+-----------+---------------+")
  print("|  Bachelors|             12|")
  print("|High school|             11|")
  print("|    Masters|              7|")
  print("+-----------+---------------+")
  print("ASSIGNMENT 2 RESULT:")
  print(assignment2().show())

  print("------")
  print("ASSIGNMENT 3 EXPECTED RESULT:")
  print("+----------+------------+")
  print("|avg_income|avg_spending|")
  print("+----------+------------+")
  print("|   20000.0|     10300.0|")
  print("+----------+------------+")
  print("ASSIGNMENT 3 RESULT:")
  print(assignment3().show())

  print("------")
  print("ASSIGNMENT 4 EXPECTED RESULT WITH PARAMETER 'Charlotte':")
  print("+----------+------------+")
  print("|avg_income|avg_spending|")
  print("+----------+------------+")
  print("|    3750.0|     12625.0|")
  print("+----------+------------+")
  print("ASSIGNMENT 4 RESULT:")
  print(assignment4("Charlotte").show())