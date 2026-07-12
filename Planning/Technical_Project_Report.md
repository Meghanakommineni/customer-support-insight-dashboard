# Master Technical Project Report: Support Analytics Pipeline
**Project: Customer Support Insights Dashboard**  
**Author: Lead Data Analyst & BI Architect**  
**Directory: `Planning/`**

This master report compiles the technical specifications, architectural designs, data definitions, and strategic insights generated across the lifecycle of the **Customer Support Insights Dashboard** project.

---

## 1. Executive Summary
The Customer Support department handles high ticket volumes across four main departments. To replace a fractured tracking methodology, this project designs and builds an end-to-end data intelligence flow. 
* **Data Engineered**: Cleaned **2,500 ticket logs** from a raw set of 2,505.
* **Database Setup**: Implemented a two-tiered (staging-to-production) relational schema using indexes and domain check constraints.
* **Analytical Highlights**: Executed multi-tier SQL queries (CTEs, Window Functions, LAG, DENSE_RANK) to answer key business questions.
* **Visualization Layer**: Created dynamic spreadsheet summary tools (with `XLOOKUP` lookup engines) and outlined the Power BI Star Schema data model and DAX calculations.
* **Core KPI Baseline**: Established the department's baseline metrics: **78.44% SLA compliance** (target 80%), **4.15 average CSAT** (target 4.0), and **41.5 hours average resolution time**.

---

## 2. Data Pipeline Architecture

The project data flows from raw telemetry logs to clean interactive presentations via four main phases:

```text
+-----------------------+      CSV Load      +-------------------------+
| Raw Tickets Log (CSV) |  --------------->  | SQL Staging Table       |
| (No constraints, dups)|                    | (Permissive TEXT schema)|
+-----------------------+                    +-------------------------+
                                                          |
                                                          | SQL ETL (Deduplication, Casts)
                                                          v
+-----------------------+     CSV Export     +-------------------------+
| Cleaned Tickets (CSV) |  <---------------  | SQL Production Table    |
| (Star Schema Ready)   |                    | (Keys, Check constraints|
+-----------------------+                    +-------------------------+
            |
            +--------------> [Excel Sheet: XLOOKUP Engine, Pivot Charts]
            |
            +--------------> [Power BI Model: Star Schema, DAX metrics, UI Grid]
```

---

## 3. Master Data Dictionary

Below is the structured schema description applied to the production dataset:

| Column Name | Database Type | Nullable? | Key Type | Constraint / Domain Bounds | Description |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **Ticket_ID** | `VARCHAR(10)` | No | PK | `TS-XXXX` format | Unique ID for each customer ticket. |
| **Customer_ID** | `VARCHAR(10)` | No | FK | `CU-XXXX` format | References Customer Dimension table. |
| **Agent_Name** | `VARCHAR(50)` | No | Attribute | Standardized string | Assigned support agent. |
| **Department** | `VARCHAR(20)` | No | Attribute | Billing, Technical, Account, General | Responsible business unit. |
| **Priority** | `VARCHAR(10)` | No | Attribute | Low, Medium, High, Urgent | Ticket urgency level. |
| **Category** | `VARCHAR(50)` | No | Attribute | Standardized category strings | Detailed request category. |
| **Created_Date** | `DATETIME` | No | Attribute | `YYYY-MM-DD HH:MM:SS` | Ticket opening timestamp. |
| **Closed_Date** | `DATETIME` | Yes | Attribute | `YYYY-MM-DD HH:MM:SS` | Ticket resolution timestamp. |
| **Resolution_Time_Hours**| `DECIMAL(6,2)`| Yes | Attribute | `>= 0.5` hours | Numeric duration from open to close. |
| **SLA_Status** | `VARCHAR(10)` | No | Attribute | Met, Breached | Calculated SLA compliance state. |
| **CSAT_Score** | `TINYINT` | Yes | Attribute | `1` to `5` | Post-resolution survey rating. |
| **Region** | `VARCHAR(20)` | No | Attribute | North America, Europe, LATAM, APAC | Geography of the customer. |
| **Channel** | `VARCHAR(15)` | No | Attribute | Email, Chat, Phone, Portal | Ticket intake mechanism. |
| **Status** | `VARCHAR(15)` | No | Attribute | Open, In Progress, Pending, Closed | Ticket lifecycle state. |

---

## 4. SQL Data Cleaning & Analytical Logic

### Data Cleaning (ETL)
The staging database data is cleansed and loaded into production using a SQL CTE and Window functions:
1. **Deduplication**: Identifies and drops 5 duplicate rows using `ROW_NUMBER() OVER (PARTITION BY Ticket_ID ORDER BY Created_Date ASC)`.
2. **Text Typo Normalization**: Resolves spelling variations in agents (e.g. `Emly Davis` $\rightarrow$ `Emily Davis`) and categories (e.g. `Paymnt Failure` $\rightarrow$ `Payment Failure`).
3. **Null Handling**: Replaces empty string markers (`""`) with proper SQL `NULL` values for CSAT, Closed Date, and Resolution Time.

### Core Analysis Query: Top Agents per Department by CSAT
*Utilizes Common Table Expressions (CTEs) and the DENSE_RANK() Window function:*
```sql
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
WHERE csat_rank <= 2
ORDER BY Department, csat_rank;
```

---

## 5. Power BI Relational Model & DAX Metrics

### The Star Schema
To optimize data compression and filter propagation speed, the data is split into a central fact table and surrounding dimensional lookups:
* `fact_tickets` (Fact): Holds foreign keys, dates, resolution metrics, and status fields.
* `dim_agents` (Dimension): Contains unique lists of `Agent_ID`, `Agent_Name`, and `Department`.
* `dim_categories` (Dimension): Contains `Category_ID` and `Category`.
* `dim_dates` (Dimension / Calendar): Built using custom M-code to handle time intelligence.

### Key DAX Measures
* **Total Tickets**: `Total Tickets = COUNTROWS(fact_tickets)`
* **SLA Compliance %**: `SLA Compliance % = DIVIDE(CALCULATE([Total Tickets], fact_tickets[SLA_Status] = "Met"), [Total Tickets], 0)`
* **Average CSAT (Role-Playing Date Connection)**:
  ```dax
  Average CSAT = 
  CALCULATE(
      AVERAGE(fact_tickets[CSAT_Score]),
      USERELATIONSHIP(dim_dates[Date], fact_tickets[Closed_Date])
  )
  ```

---

## 6. Strategic Insights & Operational Action Plan

1. **Address Technical Support SLA Deficits**:
   * *Insight*: Technical Support handles the heaviest volume (**647 tickets**) and has a poor SLA compliance rate of **63.99%** (a 36.01% breach rate), caused by complex category issues (System Bugs, Integration Errors).
   * *Action*: Reallocate 15% of General Support agent hours during peak days to handle tier-1 Technical and Billing issues, freeing up senior technical agents. Adjust the Technical SLA target for high-priority tickets from 48 to **72 hours**.
2. **Optimize Live Chat Channels**:
   * *Insight*: Chat has the lowest compliance rate (**76.97%**) because customers expect real-time resolution on this channel.
   * *Action*: Deploy automated self-service chatbot flows for high-frequency low-complexity categories like *Reset Password* and *Invoice Copy* to deflect up to 20% of chat volume.
3. **Execute Targeted Agent Coaching**:
   * *David Lee (Technical)*: Pair with our fastest agent (Priya Patel, 14.26 hrs resolution time) for a 2-week shadowing program to address technical troubleshooting speed gaps (averages **102.8 hours** per ticket).
   * *John Doe (Billing)*: Enroll John in conflict resolution and billing communication modules to address a low **3.01 CSAT** score.

---

## 7. Project Documentation Directory

For deep-dive documentation on specific phases, refer to the following repository guides:

1. **Business Objectives**: [project_charter.md](file:///c:/Users/91701/OneDrive/Desktop/customer%20support%20insight%20dashboard/Planning/project_charter.md)
2. **Detailed Data Schema**: [data_dictionary.md](file:///c:/Users/91701/OneDrive/Desktop/customer%20support%20insight%20dashboard/Dataset/data_dictionary.md)
3. **Excel Workbook Guide**: [Excel_Guide.md](file:///c:/Users/91701/OneDrive/Desktop/customer%20support%20insight%20dashboard/Excel/Excel_Guide.md)
4. **Power Query & Schema Modeling**: [Data_Modeling_Guide.md](file:///c:/Users/91701/OneDrive/Desktop/customer%20support%20insight%20dashboard/PowerBI/Data_Modeling_Guide.md)
5. **DAX Measures Dictionary**: [DAX_Measures.md](file:///c:/Users/91701/OneDrive/Desktop/customer%20support%20insight%20dashboard/PowerBI/DAX_Measures.md)
6. **Dashboard Style Guide**: [Dashboard_Design_Guide.md](file:///c:/Users/91701/OneDrive/Desktop/customer%20support%20insight%20dashboard/PowerBI/Dashboard_Design_Guide.md)
7. **Git Version Control**: [Git_Tutorial.md](file:///c:/Users/91701/OneDrive/Desktop/customer%20support%20insight%20dashboard/Planning/Git_Tutorial.md)
8. **GitHub Cloud Deployment**: [GitHub_Deployment_Guide.md](file:///c:/Users/91701/OneDrive/Desktop/customer%20support%20insight%20dashboard/Planning/GitHub_Deployment_Guide.md)
9. **SQL Analytical Report**: [query_results_report.md](file:///c:/Users/91701/OneDrive/Desktop/customer%20support%20insight%20dashboard/SQL/query_results_report.md)
10. **Executive Performance Insights**: [business_insights_report.md](file:///c:/Users/91701/OneDrive/Desktop/customer%20support%20insight%20dashboard/SQL/business_insights_report.md)
