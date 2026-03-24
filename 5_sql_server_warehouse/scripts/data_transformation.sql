/*
Here I have compiled the data transformation scripts cheatsheet.
All of these codes are reusable in any advance data cleaning and transformations.
The transformations are in steps.
*/

-- Checking the duplicates and null values by aggregating the primary key (cst_id) and applying the window ranking function
SELECT 
cst_id,
COUNT(*)
FROM
bronze.crm_cust_info
GROUP BY cst_id
HAVING COUNT(*)>1 OR cst_id IS NULL;

-- Here is the data transformation
-- Before that we need to check the data quality among the duplicates so for this pick one cst_id as apply following
SELECT
*
FROM bronze.crm_cust_info
WHERE cst_id=29466;

-- After this if the there are the duplicate data with the cst_id = 29466 then we need to select only one that is latest and has all the information
-- So for this we will use the WINDOW ranking function.
SELECT
*,
ROW_NUMBER() OVER(PARTITION BY cst_id ORDER BY cst_create_date DESC) AS flag_last
FROM bronze.crm_cust_info
WHERE cst_id=29466; -- Use where clause for only id 29466 but for all don't use the where clause

-- Now to check all the duplicated that were flagged 2 and 3 and more we can use the following command
SELECT
*
FROM(
    SELECT
    *,
    ROW_NUMBER() OVER(PARTITION BY cst_id ORDER BY cst_create_date DESC) AS flag_last
    FROM bronze.crm_cust_info
)t WHERE flag_last!=1; 
-- and if we want to check if there are no duplicates we can change the fiter
SELECT
*
FROM(
    SELECT
    *,
    ROW_NUMBER() OVER(PARTITION BY cst_id ORDER BY cst_create_date DESC) AS flag_last
    FROM bronze.crm_cust_info
    WHERE cst_id IS NOT NULL
)t WHERE flag_last=1 AND cst_id=29466; -- check only for this id but if you want to check for all then remove this command








-- Check for unwanted spaces
SELECT 
cst_firstname
FROM 
bronze.crm_cust_info
WHERE cst_firstname != TRIM(cst_firstname); 
-- Here this trim function will now check if there are spaces infront and back of the firstname and if there are then they will be displayed
-- You can also check same for the last_name as well and also check for all the string values

-- Now to remove the space we can apply the same TRIM function for the first_name and last_name
SELECT
cst_id,
TRIM(cst_firstname) as cst_firstname,
TRIM(cst_lastname) as cst_lastname,
cst_marital_status,
cst_gndr,
cst_create_date
FROM(
    SELECT
    *,
    ROW_NUMBER() OVER(PARTITION BY cst_id ORDER BY cst_create_date DESC) AS flag_last
    FROM bronze.crm_cust_info
    WHERE cst_id IS NOT NULL
)t WHERE flag_last=1;









-- Checking the data standardization and data consistency
SELECT DISTINCT 
cst_gndr
FROM bronze.crm_cust_info;

-- So if the above query statement gives the distinct data like M for male and F for female then the data is standard
-- Now each time we get the gender then let's map the F to Female and M to Male and for marital status 'M' to Married and 'S' to Single
-- Final transformed code
SELECT
cst_id,
TRIM(cst_firstname) as cst_firstname,
TRIM(cst_lastname) as cst_lastname,
CASE WHEN UPPER(cst_marital_status) = 'M' THEN 'Married'
     WHEN UPPER(cst_marital_status) = 'S' THEN 'Single'
     ELSE 'n/a'
END cst_marital_status,
CASE WHEN UPPER(cst_gndr) = 'F' THEN 'Female'
     WHEN UPPER (cst_gndr) = 'M' THEN 'Male'
     ElSE 'n/a'
END cst_gndr,
cst_create_date
FROM(
    SELECT
    *,
    ROW_NUMBER() OVER(PARTITION BY cst_id ORDER BY cst_create_date DESC) AS flag_last
    FROM bronze.crm_cust_info
    WHERE cst_id IS NOT NULL
)t WHERE flag_last=1;




-- All above column were to check and transform the data now we will insert the data into the table in silver layer.
-- Above Final transformed code carries all the transformations in which we will now use the INSERT statement to insert the data in silver column.
-- Here is the INSERT statement with all the transfromations CLEAN AND LOAD DATA IN silver.crm_cust_info
INSERT INTO silver.crm_cust_info (
    cst_id,
    cst_key,
    cst_firstname,
    cst_lastname,
    cst_marital_status,
    cst_gndr,
    cst_create_date
)
SELECT
cst_id,
cst_key,
TRIM(cst_firstname) as cst_firstname,
TRIM(cst_lastname) as cst_lastname,
CASE WHEN UPPER(cst_marital_status) = 'M' THEN 'Married'
     WHEN UPPER(cst_marital_status) = 'S' THEN 'Single'
     ELSE 'n/a'
END cst_marital_status,
CASE WHEN UPPER(cst_gndr) = 'F' THEN 'Female'
     WHEN UPPER (cst_gndr) = 'M' THEN 'Male'
     ElSE 'n/a'
END cst_gndr,
cst_create_date
FROM(
    SELECT
    *,
    ROW_NUMBER() OVER(PARTITION BY cst_id ORDER BY cst_create_date DESC) AS flag_last
    FROM bronze.crm_cust_info
    WHERE cst_id IS NOT NULL
)t WHERE flag_last=1;







-- CLEAN AND LOAD DATA IN silver.crm_prd_info
SELECT
prd_id,
prd_key,
-- HERE below we are extracting the 5 first characters to create cat_id that matches cat_id from another table
-- We will also use the REPLACE function because CO-RF and CO_RF are different
-- And REPLACE function will replace '-' with '_' to match the id.
REPLACE(SUBSTRING(prd_key, 1, 5), '-', '_') AS cat_id, 
prd_nm,
prd_cost,
prd_line,
prd_start_dt,
prd_end_dt
FROM bronze.crm_prd_info
WHERE REPLACE(SUBSTRING(prd_key, 1, 5), '-', '_') NOT IN -- this checks if any cat_id is missing comparing with table erp_px_cat_g1v2
(SELECT DISTINCT id from bronze.erp_px_cat_g1v2)