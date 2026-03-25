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
-- Table silver.crm_cust_info: Here is the INSERT statement with all the transfromations CLEAN AND LOAD DATA IN silver.crm_cust_info
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
END AS cst_marital_status,
CASE WHEN UPPER(cst_gndr) = 'F' THEN 'Female'
     WHEN UPPER (cst_gndr) = 'M' THEN 'Male'
     ElSE 'n/a'
END AS cst_gndr,
cst_create_date
FROM(
    SELECT
    *,
    ROW_NUMBER() OVER(PARTITION BY cst_id ORDER BY cst_create_date DESC) AS flag_last
    FROM bronze.crm_cust_info
    WHERE cst_id IS NOT NULL
)t WHERE flag_last=1;








-- =========================================================================================================================
-- CLEAN AND LOAD DATA IN silver.crm_prd_info
-- check
SELECT
prd_id,
prd_key,
-- HERE below we are extracting the 5 first characters to create cat_id that matches cat_id from another table
-- We will also use the REPLACE function because CO-RF and CO_RF are different
-- And REPLACE function will replace '-' with '_' to match the id.
REPLACE(SUBSTRING(prd_key, 1, 5), '-', '_') AS cat_id, 
SUBSTRING(prd_key, 7, LEN(prd_key)) AS prd_key,
prd_nm,
ISNULL(prd_cost, 0) AS prd_cost,
CASE UPPER(TRIM(prd_line))
    WHEN 'M' THEN 'Mountain'
    WHEN 'R' THEN 'Road'
    WHEN 'S' THEN 'Other Sales'
    WHEN 'T' THEN 'Touring'
    ELSE 'n/a'
END AS prd_line,
prd_start_dt,
prd_end_dt
FROM bronze.crm_prd_info;

-- Add the following filter to check if any cat_id is missing comparing with table erp_px_cat_g1v2
WHERE REPLACE(SUBSTRING(prd_key, 1, 5), '-', '_') NOT IN
(SELECT DISTINCT id from bronze.erp_px_cat_g1v2)


-- Check for unwanted spaces
SELECT
prd_nm
FROM
bronze.crm_prd_info
WHERE TRIM(prd_nm)!=prd_nm;

-- Check if the prd_cost is negative which is not practical and or prd_cost is null
SELECT
prd_cost
FROM
bronze.crm_prd_info
WHERE prd_cost<0 OR prd_cost IS NULL;

-- Now if we check the start and end data then they make no sense as end date is before the start date.
-- So we need to switch the end date and start date in such a way that the dates do not overlap.
-- So for this we will use the LEAD () window function 
INSERT INTO silver.crm_prd_info(
    prd_id,
    cat_id,
    prd_key,
    prd_nm,
    prd_cost,
    prd_line,
    prd_start_dt,
    prd_end_dt
)
SELECT
prd_id,
-- HERE below we are extracting the 5 first characters to create cat_id that matches cat_id from another table
-- We will also use the REPLACE function because CO-RF and CO_RF are different
-- And REPLACE function will replace '-' with '_' to match the id.
REPLACE(SUBSTRING(prd_key, 1, 5), '-', '_') AS cat_id, 
SUBSTRING(prd_key, 7, LEN(prd_key)) AS prd_key,
prd_nm,
ISNULL(prd_cost, 0) AS prd_cost,
CASE UPPER(TRIM(prd_line))
    WHEN 'M' THEN 'Mountain'
    WHEN 'R' THEN 'Road'
    WHEN 'S' THEN 'Other Sales'
    WHEN 'T' THEN 'Touring'
    ELSE 'n/a'
END AS prd_line,
CAST (prd_start_dt AS DATE) AS prd_start_dt,
CAST (LEAD (prd_start_dt) OVER (PARTITION BY prd_key ORDER BY prd_start_dt)-1 AS DATE) AS prd_end_dt -- Here we did -1 so that dates do not overlap
FROM bronze.crm_prd_info;

-- Now that we have very good transformation 
-- we also added cat_id and then changed the prd_start_dt and prd_end_dt into DATE
-- So we need to CREATE new silver.crm_prd_info table which you can see in the silver ddl script








-- ==============================================================================================================================
-- crm_sales_info table
-- Checking the data quality
-- In this crm_sales_info table column that contain the dates are not in DATE format but in integer.
-- So we need to check the negatives in date if exists as dates cannot be negative
-- Also we need to convert these dates which are in integer to the real DATE FORMAT
-- check if the dates are negative or null
-- not only this but check every date column
-- if there are 0 in dates the change them into NULLS
-- Also check if the dates mentioned are unrealistic
-- Do this for all other columns like sls_ship_dt and sls_due_dt
SELECT 
NULLIF(sls_order_dt, 0) AS sls_order_dt
FROM
bronze.crm_sales_details
WHERE sls_order_dt<=0 
OR LEN(sls_order_dt)!=8
OR sls_order_dt>20500101
OR sls_order_dt<19900101;


-- Now that we have checked for all the dates we also need to check if order date is before the shiping date or not
SELECT 
*
FROM
bronze.crm_sales_details
WHERE sls_order_dt>sls_ship_dt
OR sls_order_dt>sls_due_dt;


-- Next we also need to check
-- Total sales = Quantity * Price
-- So for this total sales cannot be zero and nulls are also not allowed

SELECT DISTINCT
sls_sales,
sls_quantity,
sls_price
FROM 
bronze.crm_sales_details
WHERE sls_sales != sls_quantity*sls_price
OR sls_sales IS NULL OR sls_quantity IS NULL OR sls_price IS NULL
OR sls_sales<=0 OR sls_quantity<=0 OR sls_price<=0
ORDER BY sls_sales, sls_quantity, sls_price;

-- check the transformations
SELECT
sls_sales AS old_sls_sales,
sls_quantity,
sls_price AS old_sls_price,
CASE WHEN sls_sales != sls_quantity*sls_price OR sls_sales<=0 OR sls_sales!=sls_quantity*ABS(sls_price) THEN sls_quantity*ABS(sls_price)
     ELSE sls_sales
END AS sls_sales,
sls_quantity,
CASE WHEN sls_price IS NULL OR sls_price<=0 THEN sls_sales/NULLIF(sls_quantity, 0)
     ELSE sls_price
END AS sls_price
FROM 
bronze.crm_sales_details;

-- Check if the tables connects properly or not or there are any missing data mismatch between table crm_sales_detail and crm_prd_info
-- But before you go and insert the data check if the column attributes and table matches or not
-- Since we did the CASTING of the date from INT to DATE we also need to make the new table that exctly has this
INSERT INTO silver.crm_sales_detail

SELECT
sls_ord_num,
sls_prd_key,
sls_cust_id,
CASE WHEN sls_order_dt=0 OR LEN(sls_order_dt)!=8 THEN NULL
     ELSE CAST(CAST(sls_order_dt AS VARCHAR) AS DATE)
END AS sls_order_dt,
CASE WHEN sls_ship_dt=0 OR LEN(sls_ship_dt)!=8 THEN NULL
     ELSE CAST(CAST(sls_ship_dt AS VARCHAR) AS DATE)
END AS sls_ship_dt,
CASE WHEN sls_due_dt=0 OR LEN(sls_due_dt)!=8 THEN NULL
     ELSE CAST(CAST(sls_due_dt AS VARCHAR) AS DATE)
END AS sls_due_dt,
CASE WHEN sls_sales != sls_quantity*sls_price OR sls_sales<=0 OR sls_sales!=sls_quantity*ABS(sls_price) THEN sls_quantity*ABS(sls_price)
     ELSE sls_sales
END AS sls_sales,
sls_quantity,
CASE WHEN sls_price IS NULL OR sls_price<=0 THEN sls_sales/NULLIF(sls_quantity, 0)
     ELSE sls_price
END AS sls_price
FROM 
bronze.crm_sales_details;
-- Check also for another column sls_cust_id in silver.crm_cust_info same way