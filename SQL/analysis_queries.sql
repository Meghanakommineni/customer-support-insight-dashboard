-- ==========================================
-- SQL DATA ANALYSIS & BUSINESS QUERIES
-- Project: Customer Support Insights Dashboard
-- Description: Progressive learning queries to answer key business questions.
-- ==========================================

USE customer_support_db;

-- =========================================================================
-- LEVEL 1: BASIC RETRIEVAL & FILTERING (SELECT, WHERE, ORDER BY)
-- =========================================================================

-- Query 1.1: Total Tickets in the database
-- Concept: COUNT(*) counts all rows.
SELECT COUNT(*) AS total_tickets 
FROM tickets;


-- Query 1.2: Find all Urgent or High priority tickets that are currently Open
-- Concept: WHERE filters rows based on logical conditions. ORDER BY sorts results.
SELECT Ticket_ID, Customer_ID, Agent_Name, Priority, Created_Date, Status
FROM tickets
WHERE Priority IN ('High', 'Urgent') 
  AND Status != 'Closed'
ORDER BY Created_Date DESC;


-- =========================================================================
-- LEVEL 2: AGGREGATIONS & GROUPINGS (GROUP BY, HAVING, AGGREGATE FUNCTIONS)
-- =========================================================================

-- Query 2.1: Count of tickets by Priority
-- Concept: GROUP BY aggregates data into groups. COUNT(column) returns count per group.
SELECT Priority, COUNT(*) AS ticket_count
FROM tickets
GROUP BY Priority
ORDER BY ticket_count DESC;


-- Query 2.2: Find departments with more than 500 tickets
-- Concept: HAVING filters groups after aggregation has occurred.
SELECT Department, COUNT(*) AS ticket_count
FROM tickets
GROUP BY Department
HAVING COUNT(*) > 500
ORDER BY ticket_count DESC;


-- =========================================================================
-- LEVEL 3: CONDITIONAL LOGIC & DATE FUNCTIONS (CASE, DATE FUNCTIONS)
-- =========================================================================

-- Query 3.1: Monthly Ticket volume trend
-- Concept: DATE_FORMAT or MONTHNAME extracts parts of dates.
SELECT 
    DATE_FORMAT(Created_Date, '%Y-%m') AS ticket_month,
    COUNT(*) AS ticket_count
FROM tickets
GROUP BY DATE_FORMAT(Created_Date, '%Y-%m')
ORDER BY ticket_month ASC;


-- Query 3.2: SLA Compliance Rate by Department
-- Concept: CASE WHEN evaluates conditional logic. SUM and COUNT calculate percentages.
-- SLA Compliance % = (resolved within SLA / total resolved) * 100
SELECT 
    Department,
    COUNT(*) AS total_tickets,
    SUM(CASE WHEN SLA_Status = 'Met' THEN 1 ELSE 0 END) AS sla_met_count,
    ROUND(
        (SUM(CASE WHEN SLA_Status = 'Met' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 
        2
    ) AS sla_compliance_pct
FROM tickets
GROUP BY Department
ORDER BY sla_compliance_pct DESC;


-- Query 3.3: Average Resolution Time and CSAT by Priority (Closed tickets only)
-- Concept: AVG ignores NULL values. Open tickets are automatically excluded here.
SELECT 
    Priority,
    ROUND(AVG(Resolution_Time_Hours), 2) AS avg_resolution_time_hrs,
    ROUND(AVG(CSAT_Score), 2) AS avg_csat_score
FROM tickets
WHERE Status = 'Closed'
GROUP BY Priority
ORDER BY avg_resolution_time_hrs ASC;


-- =========================================================================
-- LEVEL 4: ADVANCED SQL (CTEs, SUBQUERIES, WINDOW FUNCTIONS, RANKING)
-- =========================================================================

-- Query 4.1: Identify top-performing agents within each department by CSAT
-- Concept: CTE (Common Table Expression) creates a temporary result set.
-- DENSE_RANK() assigns ranks within partitioned groups, handling ties without gaps.
WITH AgentCSATRankings AS (
    SELECT 
        Department,
        Agent_Name,
        ROUND(AVG(CSAT_Score), 2) AS avg_csat,
        COUNT(*) AS total_closed_tickets,
        DENSE_RANK() OVER (
            PARTITION BY Department 
            ORDER BY AVG(CSAT_Score) DESC, COUNT(*) DESC
        ) AS csat_rank
    FROM tickets
    WHERE Status = 'Closed' AND CSAT_Score IS NOT NULL
    GROUP BY Department, Agent_Name
)
SELECT Department, Agent_Name, avg_csat, total_closed_tickets, csat_rank
FROM AgentCSATRankings
WHERE csat_rank <= 2 -- Get the top 2 agents per department
ORDER BY Department, csat_rank;


-- Query 4.2: Month-over-Month Ticket Volume Growth Rate
-- Concept: LAG() accesses data from the previous row in the partition.
WITH MonthlyVolume AS (
    SELECT 
        DATE_FORMAT(Created_Date, '%Y-%m') AS billing_month,
        COUNT(*) AS ticket_count
    FROM tickets
    GROUP BY DATE_FORMAT(Created_Date, '%Y-%m')
),
GrowthCalculations AS (
    SELECT 
        billing_month,
        ticket_count,
        LAG(ticket_count, 1) OVER (ORDER BY billing_month) AS previous_month_count
    FROM MonthlyVolume
)
SELECT 
    billing_month,
    ticket_count,
    previous_month_count,
    ticket_count - previous_month_count AS net_change,
    ROUND(
        ((ticket_count - previous_month_count) / previous_month_count) * 100, 
        2
    ) AS mom_growth_pct
FROM GrowthCalculations;


-- Query 4.3: Find tickets that took longer than their category's average resolution time
-- Concept: Correlated Subquery compares each row against aggregated values of the same category.
SELECT 
    t.Ticket_ID, 
    t.Category, 
    t.Priority, 
    t.Resolution_Time_Hours,
    avg_table.category_avg_hours,
    ROUND(t.Resolution_Time_Hours - avg_table.category_avg_hours, 2) AS hours_above_average
FROM tickets t
INNER JOIN (
    -- Subquery to get average per category
    SELECT Category, AVG(Resolution_Time_Hours) AS category_avg_hours
    FROM tickets
    WHERE Status = 'Closed'
    GROUP BY Category
) AS avg_table ON t.Category = avg_table.Category
WHERE t.Status = 'Closed' 
  AND t.Resolution_Time_Hours > avg_table.category_avg_hours
ORDER BY hours_above_average DESC
LIMIT 10;
