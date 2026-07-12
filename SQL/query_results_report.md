# SQL Data Analysis & Business Queries Report
**Project: Customer Support Insights Dashboard**  
**Author: Antigravity (AI Pair Programmer)**  
**Database Engine: SQLite (Local Pipeline)**

This report documents the results of executing the analytical queries from `analysis_queries.sql` on the cleaned customer support dataset of **2,500 tickets** (derived from the raw 2,505 records with 5 duplicates removed).

---

## 1. Summary of Database Metrics

### 1.1 Total Tickets
* **Query**: `SELECT COUNT(*) AS total_tickets FROM tickets;`
* **Result**:
| total_tickets |
| ------------- |
| 2500          |

### 1.2 Open Tickets (High & Urgent Priority Preview)
* **Query**: Urgent or High priority tickets that are currently Open (sorted by creation date)
* **Result**:
| Ticket_ID | Customer_ID | Agent_Name   | Priority | Created_Date        | Status      |
| --------- | ----------- | ------------ | -------- | ------------------- | ----------- |
| TS-3085   | CU-1647     | Alisha Khan  | High     | 2026-06-24 08:14:00 | In Progress |
| TS-3441   | CU-1798     | John Doe     | High     | 2026-06-18 13:12:00 | Pending     |
| TS-2916   | CU-1055     | David Lee    | High     | 2026-06-15 14:50:00 | Open        |
| TS-1878   | CU-1402     | Michael Chen | High     | 2026-06-14 10:35:00 | In Progress |
| TS-2458   | CU-1040     | Emily Davis  | High     | 2026-06-09 08:32:00 | Open        |

### 1.3 Ticket Volume by Priority
* **Query**: Count of tickets by priority
* **Result**:
| Priority | ticket_count |
| -------- | ------------ |
| Low      | 979          |
| Medium   | 914          |
| High     | 442          |
| Urgent   | 165          |

### 1.4 Ticket Volume by Department
* **Query**: Count of tickets by department (departments with > 500 tickets)
* **Result**:
| Department | ticket_count |
| ---------- | ------------ |
| Technical  | 647          |
| Billing    | 623          |
| General    | 622          |
| Account    | 608          |

---

## 2. Answers to Key Business Questions

### Question 1: Workload Analysis
> **Which ticket categories (e.g., Billing, Technical, Account) have the highest ticket volumes?**

The database contains 4 main departments, each handling 4 distinct categories. The workload is relatively evenly distributed across all 16 categories, ranging from 147 to 166 tickets each.

**Top Categories by Ticket Volume:**
1. **System Bug** (Technical): 166 tickets
2. **Partnership** (General): 162 tickets
3. **Speed Issue** (Technical): 161 tickets
4. **Integration Error** (Technical): 160 tickets
5. **Hardware Malfunction** (Technical): 160 tickets
6. **Feature Request** (General): 160 tickets

**Full Category Distribution:**
| Category             | Ticket Count | Department |
| -------------------- | ------------ | ---------- |
| System Bug           | 166          | Technical  |
| Partnership          | 162          | General    |
| Speed Issue          | 161          | Technical  |
| Integration Error    | 160          | Technical  |
| Hardware Malfunction | 160          | Technical  |
| Feature Request      | 160          | General    |
| Reset Password       | 158          | Account    |
| Invoice Copy         | 158          | Billing    |
| Payment Failure      | 157          | Billing    |
| Subscription Cancel  | 155          | Billing    |
| Refund Request       | 153          | Billing    |
| General Inquiry      | 153          | General    |
| Login Issue          | 151          | Account    |
| Account Security     | 150          | Account    |
| Update Profile       | 149          | Account    |
| Feedback             | 147          | General    |

* **Insight**: The **Technical** department bears the heaviest individual workloads (System Bug, Speed Issue, Integration Error, and Hardware Malfunction are all in the top 5). This explains why it has the highest total ticket volume (647) among all departments.

---

### Question 2: SLA Compliance
> **Which support channels (e.g., Email, Chat, Phone) have the highest SLA breach rates, and why?**

To understand SLA performance, we analyzed SLA compliance rates across both Departments and Channels.

**SLA Compliance by Department:**
| Department | Total Tickets | SLA Met Count | SLA Compliance % | SLA Breach % |
| ---------- | ------------- | ------------- | ---------------- | ------------ |
| Account    | 608           | 526           | **86.51%**       | 13.49%       |
| General    | 622           | 538           | **86.50%**       | 13.50%       |
| Billing    | 623           | 494           | **79.29%**       | 20.71%       |
| Technical  | 647           | 414           | **63.99%**       | 36.01%       |

**SLA Compliance by Channel:**
| Channel | Total Tickets | SLA Met Count | SLA Compliance % | SLA Breach % |
| ------- | ------------- | ------------- | ---------------- | ------------ |
| Email   | 649           | 527           | **81.20%**       | 18.80%       |
| Phone   | 559           | 446           | **79.79%**       | 20.21%       |
| Portal  | 645           | 501           | **77.67%**       | 22.33%       |
| Chat    | 647           | 498           | **76.97%**       | 23.03%       |

* **Insight**: 
  * **Chat** has the highest SLA breach rate (**23.03%**), closely followed by **Portal** (**22.33%**). **Email** is the most compliant channel (**81.20%**).
  * **Technical** support has a massive SLA breach rate of **36.01%**. Because technical issues (System Bugs, Integration Errors) require deeper troubleshooting and longer investigation, they naturally take longer, leading to high breach rates. This indicates a need to review and adjust SLA limits for Technical tickets or increase staffing in the Technical department.

---

### Question 3: Agent Performance
> **Who are the top-performing agents based on CSAT and resolution time? Who might need additional training or support?**

We ranked all agents by their Average CSAT and Average Resolution Time on closed tickets.

**Full Agent Leaderboard:**
| Agent Name      | Department | Avg CSAT (1-5) | Avg Resolution Time (Hrs) | Closed Tickets |
| --------------- | ---------- | -------------- | ------------------------- | -------------- |
| Sofia Rodriguez | Account    | **4.77**       | 22.65                     | 281            |
| Priya Patel     | General    | **4.68**       | 14.26                     | 287            |
| Sarah Jenkins   | Billing    | **4.64**       | 25.83                     | 182            |
| James Wilson    | Account    | **4.46**       | 31.12                     | 259            |
| Marcus Brown    | General    | **4.25**       | 25.25                     | 254            |
| Alisha Khan     | Technical  | **4.05**       | 66.36                     | 192            |
| Michael Chen    | Billing    | **4.05**       | 48.63                     | 170            |
| Emily Davis     | Technical  | **3.91**       | 86.52                     | 175            |
| David Lee       | Technical  | **3.13**       | 102.81                    | 202            |
| John Doe        | Billing    | **3.01**       | 59.55                     | 187            |

* **Top Performers**:
  * **Sofia Rodriguez** (Account) has the highest customer satisfaction score of **4.77 CSAT** with a swift resolution time of 22.65 hours.
  * **Priya Patel** (General) is the fastest agent, resolving tickets in **14.26 hours** on average with an exceptional **4.68 CSAT**.
* **Underperformers (Requiring Training/Support)**:
  * **David Lee** (Technical) struggles with complex technical tickets, averaging **102.81 hours** to close a ticket and yielding a low customer satisfaction rating of **3.13 CSAT**.
  * **John Doe** (Billing) has the lowest satisfaction score (**3.01 CSAT**) despite having a faster resolution time (59.55 hours) than the Technical agents, indicating customer service quality issues (e.g., tone or billing dispute handling).

---

### Question 4: Trend Analysis
> **Is there a monthly or weekly trend in ticket volumes? Are there seasonal spikes?**

We evaluated monthly ticket volumes and month-over-month (MoM) growth rates over a 6-month period.

| Month   | Ticket Count | Growth Count | MoM Growth % |
| ------- | ------------ | ------------ | ------------ |
| 2026-01 | 440          | *Baseline*   | *Baseline*   |
| 2026-02 | 354          | -86          | -19.55%      |
| 2026-03 | 410          | +56          | +15.82%      |
| 2026-04 | 421          | +11          | +2.68%       |
| 2026-05 | 463          | +42          | +9.98%       |
| 2026-06 | 412          | -51          | -11.02%      |

* **Insight**:
  * Ticket volume is relatively stable, fluctuating between **350 and 465 tickets** per month.
  * We observed a volume peak in **January** (440) and **May** (463), and a significant dip in **February** (354, -19.55%). No major seasonal anomalies or continuous spikes are visible in this timeframe, suggesting stable customer support operations.

---

### Question 5: Satisfaction Drivers
> **Is there a direct correlation between longer resolution times and lower CSAT scores?**

Yes. We analyzed closed tickets by grouping them into resolution time buckets and evaluating their average CSAT scores.

**Average CSAT by Resolution Time Buckets:**
| Resolution Time | Average CSAT | Closed Ticket Count |
| --------------- | ------------ | ------------------- |
| **0-12 hours**  | **4.64**     | 427                 |
| **12-24 hours** | **4.49**     | 405                 |
| **24-48 hours** | **4.15**     | 392                 |
| **48-96 hours** | **3.77**     | 306                 |
| **96+ hours**   | **3.01**     | 196                 |

**Average CSAT by SLA Status:**
* **SLA Met**: **4.34 CSAT** (1,557 tickets)
* **SLA Breached**: **2.40 CSAT** (169 tickets)

* **Key Correlation Insights**:
  1. **Direct negative correlation**: As ticket resolution times increase, customer satisfaction declines steadily. Resolution under 12 hours yields an outstanding **4.64 CSAT**, while resolution taking more than 4 days drops CSAT to **3.01**.
  2. **SLA compliance is the primary driver of satisfaction**: Tickets that breach SLA limits show an average score of **2.40 CSAT** compared to **4.34 CSAT** when SLA is met. Preventing SLA breaches is crucial to keeping customer satisfaction high.

---
*Report successfully compiled by the Local ETL Pipeline.*
