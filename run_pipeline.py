import csv
import sqlite3
import os

DB_PATH = 'SQL/customer_support_db.sqlite'
RAW_CSV_PATH = 'Dataset/customer_support_tickets.csv'
CLEANED_CSV_PATH = 'Dataset/customer_support_tickets_cleaned.csv'

def setup_database():
    print("--- Step 1: Connecting to SQLite Database ---")
    # Ensure SQL folder exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing tables to ensure repeatability
    cursor.execute("DROP TABLE IF EXISTS tickets;")
    cursor.execute("DROP TABLE IF EXISTS tickets_staging;")
    
    # Create staging table
    cursor.execute("""
    CREATE TABLE tickets_staging (
        Ticket_ID TEXT,
        Customer_ID TEXT,
        Agent_Name TEXT,
        Department TEXT,
        Priority TEXT,
        Category TEXT,
        Created_Date TEXT,
        Closed_Date TEXT,
        Resolution_Time_Hours TEXT,
        SLA_Status TEXT,
        CSAT_Score TEXT,
        Region TEXT,
        Channel TEXT,
        Status TEXT
    );
    """)
    
    # Create production cleaned table
    cursor.execute("""
    CREATE TABLE tickets (
        Ticket_ID TEXT PRIMARY KEY,
        Customer_ID TEXT NOT NULL,
        Agent_Name TEXT NOT NULL,
        Department TEXT NOT NULL,
        Priority TEXT NOT NULL,
        Category TEXT NOT NULL,
        Created_Date TEXT NOT NULL,
        Closed_Date TEXT NULL,
        Resolution_Time_Hours REAL NULL,
        SLA_Status TEXT NOT NULL,
        CSAT_Score INTEGER NULL,
        Region TEXT NOT NULL,
        Channel TEXT NOT NULL,
        Status TEXT NOT NULL,
        
        CONSTRAINT chk_csat CHECK (CSAT_Score IS NULL OR (CSAT_Score >= 1 AND CSAT_Score <= 5)),
        CONSTRAINT chk_priority CHECK (Priority IN ('Low', 'Medium', 'High', 'Urgent')),
        CONSTRAINT chk_status CHECK (Status IN ('Open', 'In Progress', 'Pending', 'Closed'))
    );
    """)
    
    # Create performance indexes
    cursor.execute("CREATE INDEX idx_created_date ON tickets (Created_Date);")
    cursor.execute("CREATE INDEX idx_status ON tickets (Status);")
    cursor.execute("CREATE INDEX idx_agent_name ON tickets (Agent_Name);")
    cursor.execute("CREATE INDEX idx_department ON tickets (Department);")
    
    conn.commit()
    print(f"Staging and production tables created successfully in '{DB_PATH}'.")
    return conn

def load_raw_csv_to_staging(conn):
    print("\n--- Step 2: Loading Raw CSV Data into Staging ---")
    cursor = conn.cursor()
    
    if not os.path.exists(RAW_CSV_PATH):
        raise FileNotFoundError(f"Raw CSV file not found at '{RAW_CSV_PATH}'")
        
    with open(RAW_CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader) # Skip header
        
        rows = [row for row in reader]
        
    cursor.executemany("""
    INSERT INTO tickets_staging (
        Ticket_ID, Customer_ID, Agent_Name, Department, Priority, Category,
        Created_Date, Closed_Date, Resolution_Time_Hours, SLA_Status, CSAT_Score,
        Region, Channel, Status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, rows)
    
    conn.commit()
    print(f"Loaded {len(rows)} rows into 'tickets_staging'.")

def run_etl_cleaning(conn):
    print("\n--- Step 3: Running ETL & Data Cleaning ---")
    cursor = conn.cursor()
    
    # Clean, deduplicate, and copy into production table
    etl_query = """
    INSERT INTO tickets (
        Ticket_ID, Customer_ID, Agent_Name, Department, Priority, Category,
        Created_Date, Closed_Date, Resolution_Time_Hours, SLA_Status, CSAT_Score,
        Region, Channel, Status
    )
    WITH DeduplicatedStaging AS (
        SELECT *,
               ROW_NUMBER() OVER (
                   PARTITION BY Ticket_ID 
                   ORDER BY Created_Date ASC
               ) as row_num
        FROM tickets_staging
    )
    SELECT 
        Ticket_ID,
        Customer_ID,
        CASE 
            WHEN Agent_Name = 'Emly Davis' THEN 'Emily Davis'
            WHEN Agent_Name = 'David L.' THEN 'David Lee'
            ELSE Agent_Name
        END AS Agent_Name,
        Department,
        Priority,
        CASE 
            WHEN Category = 'Paymnt Failure' THEN 'Payment Failure'
            WHEN Category = 'Resst Password' THEN 'Reset Password'
            WHEN Category = 'Subscrpt Cancel' THEN 'Subscription Cancel'
            ELSE Category
        END AS Category,
        Created_Date,
        CASE 
            WHEN Closed_Date = '' OR Closed_Date IS NULL THEN NULL
            ELSE Closed_Date
        END AS Closed_Date,
        CASE 
            WHEN Resolution_Time_Hours = '' OR Resolution_Time_Hours IS NULL THEN NULL
            ELSE CAST(Resolution_Time_Hours AS REAL)
        END AS Resolution_Time_Hours,
        SLA_Status,
        CASE 
            WHEN CSAT_Score = '' OR CSAT_Score IS NULL THEN NULL
            ELSE CAST(CSAT_Score AS INTEGER)
        END AS CSAT_Score,
        Region,
        Channel,
        Status
    FROM DeduplicatedStaging
    WHERE row_num = 1;
    """
    
    cursor.execute(etl_query)
    conn.commit()
    
    # Get total records
    cursor.execute("SELECT COUNT(*) FROM tickets;")
    prod_count = cursor.fetchone()[0]
    print(f"ETL completed. Inserted {prod_count} deduplicated and cleaned rows into 'tickets'.")
    
    # Run Verifications
    print("\n--- Running Cleaning Verifications ---")
    
    # 1. Duplicates check
    cursor.execute("SELECT Ticket_ID, COUNT(*) FROM tickets GROUP BY Ticket_ID HAVING COUNT(*) > 1;")
    dups = cursor.fetchall()
    print(f"Verification - Duplicate counts (should be 0): {len(dups)}")
    
    # 2. Typos check
    cursor.execute("SELECT Category, COUNT(*) FROM tickets WHERE Category IN ('Paymnt Failure', 'Resst Password', 'Subscrpt Cancel') GROUP BY Category;")
    typos = cursor.fetchall()
    print(f"Verification - Remaining typos (should be 0): {len(typos)}")
    
    # 3. Agent name variations check
    cursor.execute("SELECT Agent_Name, COUNT(*) FROM tickets WHERE Agent_Name IN ('Emly Davis', 'David L.') GROUP BY Agent_Name;")
    agent_typos = cursor.fetchall()
    print(f"Verification - Agent name typos (should be 0): {len(agent_typos)}")

def export_cleaned_csv(conn):
    print("\n--- Step 4: Exporting Cleaned Data to CSV ---")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets;")
    rows = cursor.fetchall()
    
    # Fetch headers from cursor description
    headers = [description[0] for description in cursor.description]
    
    with open(CLEANED_CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
        
    print(f"Cleaned dataset successfully exported to '{CLEANED_CSV_PATH}'.")

def format_as_markdown_table(headers, rows):
    col_widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(str(val if val is not None else '')))
            
    header_line = "| " + " | ".join(f"{h:<{col_widths[i]}}" for i, h in enumerate(headers)) + " |"
    sep_line = "| " + " | ".join("-" * col_widths[i] for i in range(len(headers))) + " |"
    
    markdown_rows = []
    for row in rows:
        row_str = "| " + " | ".join(f"{str(val if val is not None else ''):<{col_widths[i]}}" for i, val in enumerate(row)) + " |"
        markdown_rows.append(row_str)
        
    return "\n".join([header_line, sep_line] + markdown_rows)

def run_analysis_queries(conn):
    print("\n--- Step 5: Executing Analysis Queries & Answering Key Business Questions ---")
    cursor = conn.cursor()
    
    queries = {
        "1.1 Total Tickets": "SELECT COUNT(*) AS total_tickets FROM tickets;",
        
        "1.2 Urgent/High priority tickets currently Open (Top 5 for preview)": """
            SELECT Ticket_ID, Customer_ID, Agent_Name, Priority, Created_Date, Status
            FROM tickets
            WHERE Priority IN ('High', 'Urgent') 
              AND Status != 'Closed'
            ORDER BY Created_Date DESC
            LIMIT 5;
        """,
        
        "2.1 Count of tickets by Priority": """
            SELECT Priority, COUNT(*) AS ticket_count
            FROM tickets
            GROUP BY Priority
            ORDER BY ticket_count DESC;
        """,
        
        "2.2 Departments with more than 500 tickets": """
            SELECT Department, COUNT(*) AS ticket_count
            FROM tickets
            GROUP BY Department
            HAVING COUNT(*) > 500
            ORDER BY ticket_count DESC;
        """,
        
        "3.1 Monthly Ticket volume trend": """
            SELECT 
                strftime('%Y-%m', Created_Date) AS ticket_month,
                COUNT(*) AS ticket_count
            FROM tickets
            GROUP BY strftime('%Y-%m', Created_Date)
            ORDER BY ticket_month ASC;
        """,
        
        "3.2 SLA Compliance Rate by Department": """
            SELECT 
                Department,
                COUNT(*) AS total_tickets,
                SUM(CASE WHEN SLA_Status = 'Met' THEN 1 ELSE 0 END) AS sla_met_count,
                ROUND(
                    (SUM(CASE WHEN SLA_Status = 'Met' THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100, 
                    2
                ) AS sla_compliance_pct
            FROM tickets
            GROUP BY Department
            ORDER BY sla_compliance_pct DESC;
        """,
        
        "3.3 Average Resolution Time and CSAT by Priority (Closed only)": """
            SELECT 
                Priority,
                ROUND(AVG(Resolution_Time_Hours), 2) AS avg_resolution_time_hrs,
                ROUND(AVG(CSAT_Score), 2) AS avg_csat_score
            FROM tickets
            WHERE Status = 'Closed'
            GROUP BY Priority
            ORDER BY avg_resolution_time_hrs ASC;
        """,
        
        "4.1 Top 2 Agents per Department by CSAT (Closed with CSAT)": """
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
        """,
        
        "4.2 Month-over-Month Ticket Volume Growth Rate": """
            WITH MonthlyVolume AS (
                SELECT 
                    strftime('%Y-%m', Created_Date) AS billing_month,
                    COUNT(*) AS ticket_count
                FROM tickets
                GROUP BY strftime('%Y-%m', Created_Date)
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
                (ticket_count - previous_month_count) AS net_change,
                ROUND(
                    ((ticket_count - previous_month_count) * 1.0 / previous_month_count) * 100, 
                    2
                ) AS mom_growth_pct
            FROM GrowthCalculations;
        """,
        
        "4.3 SLA Compliance Rate by Channel": """
            SELECT 
                Channel,
                COUNT(*) AS total_tickets,
                SUM(CASE WHEN SLA_Status = 'Met' THEN 1 ELSE 0 END) AS sla_met_count,
                ROUND(
                    (SUM(CASE WHEN SLA_Status = 'Met' THEN 1.0 ELSE 0.0 END) / COUNT(*)) * 100, 
                    2
                ) AS sla_compliance_pct
            FROM tickets
            GROUP BY Channel
            ORDER BY sla_compliance_pct DESC;
        """
    }
    
    results = {}
    for name, sql in queries.items():
        print(f"\nRunning Query: {name}")
        cursor.execute(sql)
        headers = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        md_table = format_as_markdown_table(headers, rows)
        print(md_table)
        results[name] = md_table
        
    return results

def main():
    conn = setup_database()
    try:
        load_raw_csv_to_staging(conn)
        run_etl_cleaning(conn)
        export_cleaned_csv(conn)
        run_analysis_queries(conn)
    finally:
        conn.close()
        print("\nDatabase connection closed. Pipeline successfully finished!")

if __name__ == '__main__':
    main()
