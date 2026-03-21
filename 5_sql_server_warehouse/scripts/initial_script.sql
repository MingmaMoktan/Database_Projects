/*
============================================================================
Create Database and Schemas
============================================================================

Script Purpose:
    This script creates new database named 'DataWarehouse' after checking if it already exists.
    If the database exists, it is dropped and recreated. Additionally the script sets up three schemas within the database: bronze, silver and gold

WARNING:
    Running this script wil drop the entire 'DataWarehouse' database if it exists.
    All data in the database will be permanently deleted. Proceed with caution and ensure you have proper backups before running the script.
*/


-- This is the system database where we should connect to create our database
USE master;
GO

-- Create database if it is not created


/*
-- If we need to recreate the database again and the database exists.
IF EXISTS (SELECT 1 FROM sys.databases WHERE name='DataWarehouse')
BEGIN
    ALTER DATABASE DataWarehouse SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE DataWarehouse;
END
GO
*/

CREATE DATABASE DataWarehouse;
GO


USE DataWarehouse;
GO

CREATE SCHEMA bronze;
GO

CREATE SCHEMA silver;
GO

CREATE SCHEMA gold;
GO
