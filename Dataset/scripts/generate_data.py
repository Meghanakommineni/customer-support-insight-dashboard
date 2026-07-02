import csv
import random
from datetime import datetime, timedelta

# Configuration
NUM_TICKETS = 2500
OUTPUT_FILE = '../customer_support_tickets.csv'

# Reference data lists
DEPARTMENTS = ['Billing', 'Technical', 'Account', 'General']
PRIORITIES = ['Low', 'Medium', 'High', 'Urgent']
CHANNELS = ['Email', 'Chat', 'Phone', 'Portal']
REGIONS = ['North America', 'Europe', 'Asia-Pacific', 'LATAM']

CATEGORIES = {
    'Billing': ['Refund Request', 'Payment Failure', 'Invoice Copy', 'Subscription Cancel'],
    'Technical': ['System Bug', 'Speed Issue', 'Hardware Malfunction', 'Integration Error'],
    'Account': ['Reset Password', 'Login Issue', 'Update Profile', 'Account Security'],
    'General': ['Feedback', 'Feature Request', 'General Inquiry', 'Partnership']
}

# SLA limits in hours
SLA_LIMITS = {
    'Urgent': 24,    # 1 day
    'High': 48,      # 2 days
    'Medium': 96,    # 4 days
    'Low': 168       # 7 days
}

# Agents with departmental assignments and performance characteristics
AGENTS = {
    'Sarah Jenkins': {'dept': 'Billing', 'avg_speed': 12, 'avg_csat': 4.5},
    'Michael Chen': {'dept': 'Billing', 'avg_speed': 18, 'avg_csat': 4.1},
    'Emily Davis': {'dept': 'Technical', 'avg_speed': 36, 'avg_csat': 4.2},
    'David Lee': {'dept': 'Technical', 'avg_speed': 48, 'avg_csat': 3.6},
    'Sofia Rodriguez': {'dept': 'Account', 'avg_speed': 8, 'avg_csat': 4.7},
    'James Wilson': {'dept': 'Account', 'avg_speed': 14, 'avg_csat': 4.3},
    'Priya Patel': {'dept': 'General', 'avg_speed': 6, 'avg_csat': 4.6},
    'Marcus Brown': {'dept': 'General', 'avg_speed': 10, 'avg_csat': 4.0},
    'Alisha Khan': {'dept': 'Technical', 'avg_speed': 30, 'avg_csat': 4.4},
    'John Doe': {'dept': 'Billing', 'avg_speed': 24, 'avg_csat': 3.2}
}

def generate_dataset():
    random.seed(42)  # For reproducibility
    
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 6, 30)
    delta_days = (end_date - start_date).days
    
    tickets = []
    
    for i in range(1, NUM_TICKETS + 1):
        ticket_id = f"TS-{1000 + i}"
        customer_id = f"CU-{random.randint(1001, 1999)}"
        
        # 1. Channel, Region, and priority
        channel = random.choice(CHANNELS)
        region = random.choice(REGIONS)
        priority = random.choices(PRIORITIES, weights=[40, 35, 18, 7], k=1)[0]
        
        # 2. Select Department and Category
        department = random.choice(DEPARTMENTS)
        category = random.choice(CATEGORIES[department])
        
        # Introduce Typos for data cleaning exercise in Excel phase (approx 2% of rows)
        if random.random() < 0.02:
            if category == 'Payment Failure':
                category = 'Paymnt Failure'
            elif category == 'Reset Password':
                category = 'Resst Password'
            elif category == 'Subscription Cancel':
                category = 'Subscrpt Cancel'
                
        # 3. Agent selection based on department
        dept_agents = [name for name, info in AGENTS.items() if info['dept'] == department]
        agent = random.choice(dept_agents)
        agent_info = AGENTS[agent]
        
        # Introduce agent name variations for cleaning
        if random.random() < 0.01:
            if agent == 'Emily Davis':
                agent = 'Emly Davis'
            elif agent == 'David Lee':
                agent = 'David L.'
                
        # 4. Dates & Status
        created_days_offset = random.randint(0, delta_days)
        created_time = start_date + timedelta(
            days=created_days_offset,
            hours=random.randint(8, 18),
            minutes=random.randint(0, 59)
        )
        
        # Determine status: 88% Closed, 6% Open, 4% In Progress, 2% Pending
        status = random.choices(['Closed', 'Open', 'In Progress', 'Pending'], weights=[88, 6, 4, 2], k=1)[0]
        
        closed_date_str = ""
        resolution_hours = ""
        sla_status = ""
        csat_score = ""
        
        if status == 'Closed':
            # Calculate resolution time in hours
            # Base speed of agent + priority impact (Urgent resolved faster)
            priority_multipliers = {'Urgent': 0.4, 'High': 0.7, 'Medium': 1.0, 'Low': 1.5}
            base_hours = agent_info['avg_speed'] * priority_multipliers[priority]
            
            # Add random variance (log-normal distribution to simulate real-world support outlier times)
            variance = random.lognormvariate(0.5, 0.8)
            res_hours = round(base_hours * variance, 2)
            if res_hours < 0.5:
                res_hours = 0.5
            
            resolution_hours = res_hours
            closed_time = created_time + timedelta(hours=res_hours)
            closed_date_str = closed_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Determine SLA compliance
            sla_limit = SLA_LIMITS[priority]
            if res_hours <= sla_limit:
                sla_status = 'Met'
            else:
                sla_status = 'Breached'
                
            # Determine CSAT score (correlated to resolution hours & agent's base CSAT)
            # High speed = better CSAT. SLA Breach = much worse CSAT.
            if sla_status == 'Breached':
                csat_base = agent_info['avg_csat'] - 1.5
            else:
                if res_hours < (sla_limit * 0.25):
                    csat_base = agent_info['avg_csat'] + 0.5
                else:
                    csat_base = agent_info['avg_csat']
            
            # Cap CSAT between 1 and 5
            csat_val = round(random.normalvariate(csat_base, 0.7))
            csat_val = max(1, min(5, csat_val))
            
            # Note: Approximately 20% of users don't respond to the feedback survey
            if random.random() > 0.20:
                csat_score = csat_val
        else:
            # Unclosed tickets don't have resolution hours or closed dates
            # Check if ticket has already breached SLA relative to a "current date" of July 1, 2026
            current_time = datetime(2026, 7, 1)
            hours_open = (current_time - created_time).total_seconds() / 3600
            sla_limit = SLA_LIMITS[priority]
            if hours_open > sla_limit:
                sla_status = 'Breached'
            else:
                sla_status = 'Met'
        
        ticket_row = {
            'Ticket_ID': ticket_id,
            'Customer_ID': customer_id,
            'Agent_Name': agent,
            'Department': department,
            'Priority': priority,
            'Category': category,
            'Created_Date': created_time.strftime('%Y-%m-%d %H:%M:%S'),
            'Closed_Date': closed_date_str,
            'Resolution_Time_Hours': resolution_hours,
            'SLA_Status': sla_status,
            'CSAT_Score': csat_score,
            'Region': region,
            'Channel': channel,
            'Status': status
        }
        tickets.append(ticket_row)

    # 5. Add duplicate tickets to simulate log errors (approx 5 duplicates)
    for _ in range(5):
        dup_ticket = random.choice(tickets).copy()
        tickets.append(dup_ticket)
        
    # Shuffle list so duplicates are dispersed
    random.shuffle(tickets)
    
    # Write to CSV
    headers = [
        'Ticket_ID', 'Customer_ID', 'Agent_Name', 'Department', 'Priority', 
        'Category', 'Created_Date', 'Closed_Date', 'Resolution_Time_Hours', 
        'SLA_Status', 'CSAT_Score', 'Region', 'Channel', 'Status'
    ]
    
    import os
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(tickets)
        
    print(f"Successfully generated {len(tickets)} support ticket records in '{OUTPUT_FILE}'.")

if __name__ == '__main__':
    generate_dataset()
