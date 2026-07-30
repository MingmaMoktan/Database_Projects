CREATE OR ALTER PROCEDURE silver.load_silver_layer
AS
BEGIN
    SET NOCOUNT ON;

    PRINT '==================================================';
    PRINT 'Starting Silver Layer Loading Process';
    PRINT '==================================================';

    -- 1. Load crm_cust_info
    PRINT '--------------------------------------------------';
    PRINT 'Loading Silver.crm_cust_info';
    PRINT '--------------------------------------------------';
    TRUNCATE TABLE silver.crm_cust_info;
    INSERT INTO silver.crm_cust_info (
        cst_id, cst_key, cst_firstname, cst_lastname, cst_marital_status, cst_gndr, cst_create_date
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
             ELSE 'n/a'
        END AS cst_gndr,
        cst_create_date
    FROM(
        SELECT *,
            ROW_NUMBER() OVER(PARTITION BY cst_id ORDER BY cst_create_date DESC) AS flag_last
        FROM bronze.crm_cust_info
        WHERE cst_id IS NOT NULL
    )t WHERE flag_last = 1;
    PRINT '>> Finished loading silver.crm_cust_info';

    -- 2. Load crm_prd_info
    PRINT '--------------------------------------------------';
    PRINT 'Loading Silver.crm_prd_info';
    PRINT '--------------------------------------------------';
    TRUNCATE TABLE silver.crm_prd_info;
    INSERT INTO silver.crm_prd_info(
        prd_id, cat_id, prd_key, prd_nm, prd_cost, prd_line, prd_start_dt, prd_end_dt
    )
    SELECT
        prd_id,
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
        CAST (LEAD (prd_start_dt) OVER (PARTITION BY prd_key ORDER BY prd_start_dt) - 1 AS DATE) AS prd_end_dt 
    FROM bronze.crm_prd_info;
    PRINT '>> Finished loading silver.crm_prd_info';

    -- 3. Load crm_sales_details
    PRINT '--------------------------------------------------';
    PRINT 'Loading Silver.crm_sales_details';
    PRINT '--------------------------------------------------';
    TRUNCATE TABLE silver.crm_sales_details;
    INSERT INTO silver.crm_sales_details(
         sls_ord_num, sls_prd_key, sls_cust_id, sls_order_id, sls_ship_dt, sls_due_dt, sls_sales, sls_quantity, sls_price 
    )
    SELECT
        sls_ord_num,
        sls_prd_key,
        sls_cust_id,
        CASE WHEN sls_order_dt = 0 OR LEN(sls_order_dt) != 8 THEN NULL
             ELSE CAST(CAST(sls_order_dt AS VARCHAR) AS DATE)
        END AS sls_order_dt,
        CASE WHEN sls_ship_dt = 0 OR LEN(sls_ship_dt) != 8 THEN NULL
             ELSE CAST(CAST(sls_ship_dt AS VARCHAR) AS DATE)
        END AS sls_ship_dt,
        CASE WHEN sls_due_dt = 0 OR LEN(sls_due_dt) != 8 THEN NULL
             ELSE CAST(CAST(sls_due_dt AS VARCHAR) AS DATE)
        END AS sls_due_dt,
        CASE WHEN sls_sales != sls_quantity * sls_price OR sls_sales <= 0 OR sls_sales != sls_quantity * ABS(sls_price) THEN sls_quantity * ABS(sls_price)
             ELSE sls_sales
        END AS sls_sales,
        sls_quantity,
        CASE WHEN sls_price IS NULL OR sls_price <= 0 THEN sls_sales / NULLIF(sls_quantity, 0)
             ELSE sls_price
        END AS sls_price
    FROM bronze.crm_sales_details;
    PRINT '>> Finished loading silver.crm_sales_details';

    -- 4. Load erp_cust_az12
    PRINT '--------------------------------------------------';
    PRINT 'Loading Silver.erp_cust_az12';
    PRINT '--------------------------------------------------';
    TRUNCATE TABLE silver.erp_cust_az12;
    INSERT INTO silver.erp_cust_az12(cid, bdate, gen)
    SELECT
        CASE WHEN cid LIKE 'NAS%' THEN SUBSTRING(cid, 4, LEN(cid))
             ELSE cid
        END AS cid,
        CASE WHEN bdate > GETDATE() THEN NULL
             ELSE bdate
        END AS bdate,
        CASE WHEN UPPER(gen) LIKE 'F%' THEN 'Female'
             WHEN UPPER(gen) LIKE 'M%' THEN 'Male'
             ELSE 'n/a'
        END AS gen
    FROM bronze.erp_cust_az12;
    PRINT '>> Finished loading silver.erp_cust_az12';

    -- 5. Load erp_loc_a101
    PRINT '--------------------------------------------------';
    PRINT 'Loading Silver.erp_loc_a101';
    PRINT '--------------------------------------------------';
    TRUNCATE TABLE silver.erp_loc_a101;
    INSERT INTO silver.erp_loc_a101 (cid, cntry)
    SELECT 
        REPLACE(cid, '-', '') cid,
        CASE 
             WHEN UPPER(TRIM(cntry)) LIKE 'DE%' THEN 'Germany'
             WHEN UPPER(TRIM(cntry)) LIKE 'US%' THEN 'United States'
             WHEN TRIM(cntry) = '' OR cntry IS NULL THEN 'n/a'
             ELSE TRIM(cntry)
        END AS cntry
    FROM bronze.erp_loc_a101;
    PRINT '>> Finished loading silver.erp_loc_a101';

    -- 6. Load erp_px_cat_g1v2
    PRINT '--------------------------------------------------';
    PRINT 'Loading Silver.erp_px_cat_g1v2';
    PRINT '--------------------------------------------------';
    TRUNCATE TABLE silver.erp_px_cat_g1v2;
    INSERT INTO silver.erp_px_cat_g1v2 (id, cat, subcat, maintenance)
    SELECT id, cat, subcat, maintenance 
    FROM bronze.erp_px_cat_g1v2;
    PRINT '>> Finished loading silver.erp_px_cat_g1v2';

    PRINT '==================================================';
    PRINT 'Silver Layer Loading Completed Successfully';
    PRINT '==================================================';
END;
GO