-- This is for looking all the customer information
SELECT cst_id, COUNT(*) FROM
(
    -- You can only use below select statement with left join to see all the customer data from different tables
SELECT 
	ci.cst_id,
	ci.cst_key,
	ci.cst_firstname,
	ci.cst_lastname,
	ci.cst_gndr, -- Here is gender
    ci.cst_marital_status
	ci.cst_create_date,
	ca.bdate,
	ca.gen, -- Here is also gender
	la.cntry
FROM silver.crm_cust_info ci
LEFT JOIN silver.erp_cust_az12 ca
ON 	ci.cst_key = ca.cid
LEFT JOIN silver.erp_loc_a101 la
ON 	ci.cst_key = la.cid
)t -- And here we are using the group by and having count(*)>1 to check if there are any duplicates
GROUP BY cst_id
HAVING COUNT(*)>1

-- Now in above query and then the data we have the issue of having the two gender column from two different tables
-- So what we need to do now is to check if the gender matches in both tables and are distinct
-- So for this we can use the following to check
-- So in this case if the gender in columns are male in one column and female in another column then we need to verify which is the master data about the customer
SELECT DISTINCT
    ci.cst_gndr,
    ca.gen,
    -- Now we can put this case and else in our main logic for the data integration in main query
    CASE 
        WHEN ci.cst_gndr != 'n/a' THEN ci.cst_gndr  -- Use CRM if it's valid
        ELSE COALESCE(ca.gen, 'n/a')                -- Otherwise use ERP, or default to 'n/a' if both are blank
    END AS new_gen
FROM silver.crm_cust_info ci
LEFT JOIN silver.erp_cust_az12 ca                    -- (Added the missing 'ca' alias here too)
ON ci.cst_key = ca.cid
ORDER BY 1, 2


-- So here is the final script here we will also add the column name that is more clear and readable
-- This is describing the customer so this is clearly the dimension table as this doesn't have any transactions and events
-- Here we have primary key on the table which may not be on other dimension so we need to generate another one which is also called the surrogate key
-- 
CREATE VIEW gold.dim_customers AS
SELECT 
	ROW_NUMBER() OVER (ORDER BY cst_id) AS customer_key,
	ci.cst_id AS customer_id, -- Here we have primary key on the table which may not be on other dimension so we need to generate another one which is also called the surrogate key
	ci.cst_key AS customer_number,
	ci.cst_firstname AS first_name,
	ci.cst_lastname AS last_name,
	la.cntry AS country,
    CASE 
        WHEN ci.cst_gndr != 'n/a' THEN ci.cst_gndr  -- Use CRM if it's valid
        ELSE COALESCE(ca.gen, 'n/a')                -- Otherwise use ERP, or default to 'n/a' if both are blank
    END AS gender,
	ca.bdate AS birth_date,
    ci.cst_marital_status AS maritial_status,
	ci.cst_create_date AS create_date
FROM silver.crm_cust_info ci
LEFT JOIN silver.erp_cust_az12 ca
ON 	ci.cst_key = ca.cid
LEFT JOIN silver.erp_loc_a101 la
ON 	ci.cst_key = la.cid






-- Now we want to create the product information table
-- In product table we have the historical data and current data
-- So then for the recent and current analysis we should always take the current data while historical data is also good but not for making the present decisions
-- So for this we are going to use the date as the filter
-- In this product data there is a column where there is end_date or prd_end_date which shows it usually is the historical data
-- So we should filter them out and put only those data which have the end_date or prd_date null as null tells us it has not ended and then it is current data
-- And for the final part we have to join the product category table to get all product category data
-- And also check if the data is unique for this we use subquery method
-- And now we arrange the column and then give readble names for the columns
SELECT prd_key, COUNT(*) FROM (
SELECT
	pn.prd_id AS product_id,
	pn.prd_key AS product_number,
	pn.prd_nm AS product_name,
	pn.cat_id AS category_id,
	pc.cat AS category,
	pc.subcat AS subcategory,
	pc.maintenance,
	pn.prd_cost AS cost,
	pn.prd_line AS product_line,
	pn.prd_start_dt AS start_date
FROM silver.crm_prd_info pn
LEFT JOIN silver.erp_px_cat_g1v2 pc
ON pn.cat_id = pc.id
WHERE prd_end_dt IS NULL -- This filters out all historical data
)t 
GROUP BY prd_key
HAVING COUNT(*)>1


-- Here is the final script to create the product view
-- Here we have the description about the product and there is no transactions like order, order date 
-- So we will generate the dimension view for the product
-- Also creating the surrogate key with the product start date is to filter which product is latest on the production
CREATE VIEW gold.dim_customers AS
SELECT
	ROW_NUMBER() OVER (ORDER BY pn.prd_start_dt, pn.prd_key) AS product_key, -- if you forget the logic here look onto this as we use product_start_dt to arrange
	-- but start date may be same for some products so we have to order them again so we used product key
	pn.prd_id AS product_id,
	pn.prd_key AS product_number,
	pn.prd_nm AS product_name,
	pn.cat_id AS category_id,
	pc.cat AS category,
	pc.subcat AS subcategory,
	pc.maintenance,
	pn.prd_cost AS cost,
	pn.prd_line AS product_line,
	pn.prd_start_dt AS start_date
FROM silver.crm_prd_info pn
LEFT JOIN silver.erp_px_cat_g1v2 pc
ON pn.cat_id = pc.id
WHERE prd_end_dt IS NULL -- This filters out all historical data




-- So now we have only one table left for the fact that is the sales tables
-- 