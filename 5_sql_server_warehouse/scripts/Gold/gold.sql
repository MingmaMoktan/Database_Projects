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


-- So here is the final script
SELECT 
	ci.cst_id,
	ci.cst_key,
	ci.cst_firstname,
	ci.cst_lastname,
    ci.cst_marital_status,
    CASE 
        WHEN ci.cst_gndr != 'n/a' THEN ci.cst_gndr  -- Use CRM if it's valid
        ELSE COALESCE(ca.gen, 'n/a')                -- Otherwise use ERP, or default to 'n/a' if both are blank
    END AS new_gen,
	ci.cst_create_date,
	ca.bdate,
	la.cntry
FROM silver.crm_cust_info ci
LEFT JOIN silver.erp_cust_az12 ca
ON 	ci.cst_key = ca.cid
LEFT JOIN silver.erp_loc_a101 la
ON 	ci.cst_key = la.cid