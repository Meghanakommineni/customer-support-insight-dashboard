-- ==========================================
-- SQL DATABASE SETUP
-- Project: Customer Support Insights Dashboard
-- Description: Creates the database schema, staging table, and target production tables.
-- ==========================================

-- 1. Create and select the database
CREATE DATABASE IF NOT EXISTS customer_support_db;
USE customer_support_db;

-- 2. Drop tables if they already exist to ensure repeatable execution
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS tickets_staging;

-- 3. Create STAGING Table
-- Purpose: This table holds the raw CSV data exactly as it is. 
-- No Primary Keys or strict constraints are applied yet. This allows us to load 
-- data containing duplicate keys, null values, or typos without failing the import.
CREATE TABLE tickets_staging (
    Ticket_ID VARCHAR(255),
    Customer_ID VARCHAR(255),
    Agent_Name VARCHAR(255),
    Department VARCHAR(255),
    Priority VARCHAR(255),
    Category VARCHAR(255),
    Created_Date VARCHAR(255),
    Closed_Date VARCHAR(255),
    Resolution_Time_Hours VARCHAR(255),
    SLA_Status VARCHAR(255),
    CSAT_Score VARCHAR(255),
    Region VARCHAR(255),
    Channel VARCHAR(255),
    Status VARCHAR(255)
);

-- 4. Create PRODUCTION (Cleaned) Table
-- Purpose: The target structured table. Proper constraints, correct data types,
-- and primary keys are applied here. This is the table that BI tools and analysts query.
CREATE TABLE tickets (
    Ticket_ID VARCHAR(10) PRIMARY KEY,
    Customer_ID VARCHAR(10) NOT NULL,
    Agent_Name VARCHAR(50) NOT NULL,
    Department VARCHAR(20) NOT NULL,
    Priority VARCHAR(10) NOT NULL,
    Category VARCHAR(50) NOT NULL,
    Created_Date DATETIME NOT NULL,
    Closed_Date DATETIME NULL,
    Resolution_Time_Hours DECIMAL(6,2) NULL,
    SLA_Status VARCHAR(10) NOT NULL,
    CSAT_Score TINYINT NULL,
    Region VARCHAR(20) NOT NULL,
    Channel VARCHAR(15) NOT NULL,
    Status VARCHAR(15) NOT NULL,
    
    -- Ensure CSAT is only between 1 and 5 (Domain integrity check)
    CONSTRAINT chk_csat CHECK (CSAT_Score IS NULL OR (CSAT_Score >= 1 AND CSAT_Score <= 5)),
    
    -- Ensure Priority is a standard value
    CONSTRAINT chk_priority CHECK (Priority IN ('Low', 'Medium', 'High', 'Urgent')),
    
    -- Ensure Status is a valid lifecycle state
    CONSTRAINT chk_status CHECK (Status IN ('Open', 'In Progress', 'Pending', 'Closed'))
);

-- 5. Create Performance Indexes
-- Purpose: Indexes speed up common database queries. Since analytical dashboards 
-- will frequently filter, group, and sort by dates, status, agent, and department,
-- indexes are added to these columns.
CREATE INDEX idx_created_date ON tickets (Created_Date);
CREATE INDEX idx_status ON tickets (Status);
CREATE INDEX idx_agent_name ON tickets (Agent_Name);
CREATE INDEX idx_department ON tickets (Department);
