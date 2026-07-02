-- ==========================================
-- SQL ETL & DATA CLEANING SCRIPT
-- Project: Customer Support Insights Dashboard
-- Description: Cleans the staging data (deduplicates, fixes typos, casts dates/numbers)
--              and loads it into the final production tickets table.
-- ==========================================

USE customer_support_db;

-- Clear any existing records in the production table to prevent primary key conflicts on rerun
TRUNCATE TABLE tickets;

-- Note on Importing raw CSV to tickets_staging in MySQL:
-- You can load the raw CSV using a GUI client (like MySQL Workbench Import Wizard) or by running:
--
-- LOAD DATA INFILE 'c:/Users/91701/OneDrive/Desktop/customer support insight dashboard/Dataset/customer_support_tickets.csv'
-- INTO TABLE tickets_staging
-- FIELDS TERMINATED BY ','
-- OPTIONALLY ENCLOSED BY '"'
-- LINES TERMINATED BY '\r\n'
-- IGNORE 1 LINES;

-- 1. Run the ETL query to clean, cast, and transfer data
INSERT INTO tickets (
    Ticket_ID,
    Customer_ID,
    Agent_Name,
    Department,
    Priority,
    Category,
    Created_Date,
    Closed_Date,
    Resolution_Time_Hours,
    SLA_Status,
    CSAT_Score,
    Region,
    Channel,
    Status
)
WITH DeduplicatedStaging AS (
    -- Remove duplicate rows based on Ticket_ID using Window Functions
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY Ticket_ID 
               ORDER BY STR_TO_DATE(Created_Date, '%Y-%m-%d %H:%M:%S') ASC
           ) as row_num
    FROM tickets_staging
)
SELECT 
    Ticket_ID,
    Customer_ID,
    
    -- Clean Agent Name typos
    CASE 
        WHEN Agent_Name = 'Emly Davis' THEN 'Emily Davis'
        WHEN Agent_Name = 'David L.' THEN 'David Lee'
        ELSE Agent_Name
    END AS Agent_Name,
    
    Department,
    Priority,
    
    -- Clean Category typos
    CASE 
        WHEN Category = 'Paymnt Failure' THEN 'Payment Failure'
        WHEN Category = 'Resst Password' THEN 'Reset Password'
        WHEN Category = 'Subscrpt Cancel' THEN 'Subscription Cancel'
        ELSE Category
    END AS Category,
    
    -- Cast dates from string to DATETIME format
    STR_TO_DATE(Created_Date, '%Y-%m-%d %H:%M:%S') AS Created_Date,
    
    -- Convert empty strings to NULL before casting to DATETIME
    CASE 
        WHEN Closed_Date = '' OR Closed_Date IS NULL THEN NULL
        ELSE STR_TO_DATE(Closed_Date, '%Y-%m-%d %H:%M:%S')
    END AS Closed_Date,
    
    -- Convert empty strings to NULL and cast to DECIMAL
    CASE 
        WHEN Resolution_Time_Hours = '' OR Resolution_Time_Hours IS NULL THEN NULL
        ELSE CAST(Resolution_Time_Hours AS DECIMAL(6,2))
    END AS Resolution_Time_Hours,
    
    SLA_Status,
    
    -- Convert empty strings to NULL and cast to TINYINT
    CASE 
        WHEN CSAT_Score = '' OR CSAT_Score IS NULL THEN NULL
        ELSE CAST(CSAT_Score AS TINYINT)
    END AS CSAT_Score,
    
    Region,
    Channel,
    Status

FROM DeduplicatedStaging
WHERE row_num = 1; -- Keep only the first instance of each Ticket_ID (drops the 5 duplicates)

-- 2. Verify cleaning success
-- Query to confirm that duplicate records were successfully removed (should return 0 rows)
SELECT Ticket_ID, COUNT(*) 
FROM tickets 
GROUP BY Ticket_ID 
HAVING COUNT(*) > 1;

-- Query to verify that typos were standardized (should return 0 rows)
SELECT Category, COUNT(*) 
FROM tickets 
WHERE Category IN ('Paymnt Failure', 'Resst Password', 'Subscrpt Cancel')
GROUP BY Category;
