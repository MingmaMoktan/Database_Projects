## Data Catalog: Gold Layer Schema

This data catalog documents the core dimensional data warehouse models (`gold` schema) built from the cleaned integration layer (`silver` schema).

---

### 1. Dimension Table: `gold.dim_customers`

* **Description:** Represents customer master data. Consolidates customer profile details, geographical locations, and demographic attributes from multiple source systems, resolving duplicate records and conflicting fields (such as gender prioritization).
* **Type:** Dimension Table (Descriptive data, no transaction events).

| Column Name | Data Type (Logical) | Key Type | Description / Logic |
| --- | --- | --- | --- |
| **`customer_key`** | Integer | **Surrogate Key** | Unique sequential identifier generated via `ROW_NUMBER() OVER (ORDER BY cst_id)` for internal warehouse relations. |
| **`customer_id`** | Integer / ID | Natural Key | Original system primary key from the CRM system (`ci.cst_id`). |
| **`customer_number`** | String | Business Key | Unique business key representing the customer account (`ci.cst_key`). |
| **`first_name`** | String | Attribute | Customer's first name. |
| **`last_name`** | String | Attribute | Customer's last name. |
| **`country`** | String | Attribute | Customer's home country, derived from location data (`la.cntry`). |
| **`gender`** | String | Attribute | Resolved gender attribute. Prioritizes valid CRM data (`ci.cst_gndr != 'n/a'`), falling back to ERP data or defaulting to `'n/a'`. |
| **`birth_date`** | Date | Attribute | Customer's date of birth (`ca.bdate`). |
| **`maritial_status`** | String | Attribute | Customer's marital status (`ci.cst_marital_status`). |
| **`create_date`** | Timestamp | Audit | Record creation timestamp in the source system (`ci.cst_create_date`). |

---

### 2. Dimension Table: `gold.dim_product`

* **Description:** Contains active product specifications and category classifications. Filters out historical/expired product iterations to reflect current operational catalogs.
* **Type:** Dimension Table (Descriptive data, product hierarchy).

| Column Name | Data Type (Logical) | Key Type | Description / Logic |
| --- | --- | --- | --- |
| **`product_key`** | Integer | **Surrogate Key** | Unique sequential identifier ordered by product start date and product key to handle active/historical lifecycle tracking. |
| **`product_id`** | Integer / ID | Natural Key | Original product identifier (`pn.prd_id`). |
| **`product_number`** | String | Business Key | Business code/number for the product (`pn.prd_key`). |
| **`product_name`** | String | Attribute | Descriptive name of the product (`pn.prd_nm`). |
| **`category_id`** | String | Foreign Key | Category classification code (`pn.cat_id`). |
| **`category`** | String | Attribute | Main product category name (`pc.cat`). |
| **`subcategory`** | String | Attribute | Detailed product subcategory name (`pc.subcat`). |
| **`maintenance`** | String | Attribute | Maintenance status or requirements (`pc.maintenance`). |
| **`cost`** | Numeric | Metric / Measure | Standard baseline cost of the product (`pn.prd_cost`). |
| **`product_line`** | String | Attribute | Product line grouping (`pn.prd_line`). |
| **`start_date`** | Date | Audit / Filter | Effective start date of the product version (`pn.prd_start_dt`). Filtered where `prd_end_dt IS NULL`. |

---

### 3. Fact Table: `gold.fact_sales` *(Recommended View/Table Structure)*

* **Description:** Represents transactional sales events. Contains metrics (sales, quantity, price) and foreign keys mapping back to customer and product dimensions.
* **Type:** Fact Table (Transactional event-based data).

| Column Name | Data Type (Logical) | Key Type | Description / Logic |
| --- | --- | --- | --- |
| **`sls_ord_num`** | String | Business Key | Sales order transaction number. |
| **`sls_prd_key`** | String | Foreign Key | References product key / number to join with `dim_product`. |
| **`sls_cust_id`** | Integer / ID | Foreign Key | References customer identifier to join with `dim_customers`. |
| **`sls_order_dt`** | Date | Temporal | Date when the sales order was placed. |
| **`sls_ship_dt`** | Date | Temporal | Date when the order was shipped. |
| **`sls_due_dt`** | Date | Temporal | Due date for payment/delivery fulfillment. |
| **`sls_sales`** | Numeric | Fact / Metric | Total sales revenue generated from the line item. |
| **`sls_quantity`** | Integer | Fact / Metric | Quantity of products ordered. |
| **`sls_price`** | Numeric | Fact / Metric | Unit price of the product during the transaction. |