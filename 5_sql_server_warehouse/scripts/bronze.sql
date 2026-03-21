-- DataWarehouse.bronze.crm_cust_info definition

-- Drop table

-- DROP TABLE DataWarehouse.bronze.crm_cust_info;

CREATE TABLE DataWarehouse.bronze.crm_cust_info (
	cst_id int NULL,
	cst_key nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	cst_firstname nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	cst_lastname nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	cst_marital_status nvarchar(50) COLLATE SQL_Latin1_General_CP1_CI_AS NULL,
	cst_create_date date NULL
);

