# Excel Implementation Report: Spreadsheet Modeling & Analytics
**Project: Customer Support Insights Dashboard**  

This report documents the design architecture, formulas, and visual analytics implemented in Microsoft Excel to build the interactive customer support analytical workbook.

---

## 1. Spreadsheet Architecture

The workbook `customer_support_analysis.xlsx` is structured into three sheets to maintain clean data segregation (Raw Staging $\rightarrow$ Cleansed Source $\rightarrow$ Presentation Layer):

* **`Raw Data` Sheet**: Contains the raw, unchanged 2,505 ticket logs imported directly from the database staging tables. It acts as an audit trail.
* **`Cleaned Data` Sheet**: Contains the cleaned, deduplicated, and formatted 2,500 ticket records. 
  * Features custom formatting like **conditional styling** to highlight SLA statuses: `"Met"` in light green (`#C6EFCE` fill with `#006100` dark green text) and `"Breached"` in light red (`#FFC7CE` fill with `#9C0006` dark red text).
* **`KPI Dashboard` Sheet**: The presentation layer designed with a professional corporate color palette (deep slate navy `#1F4E79`, steel blue `#2F5597`, and soft blue `#DDEBF7`) summarizing support metrics and housing the interactive lookup engine.

---

## 2. Implemented Formulas & Calculation Logic

All KPIs and search tools on the executive dashboard calculate dynamically based on cell formulas:

### A. Core Executive Metrics
* **Total Tickets**: `=COUNTA('Cleaned Data'!A:A)-1`
  * *Logic*: Counts all records in the ID column of the cleaned data, subtracting `1` to exclude the header row.
* **Closed Tickets**: `=COUNTIF('Cleaned Data'!N:N,"Closed")`
  * *Logic*: Counts support tickets that have completed resolutions.
* **Open Tickets (Backlog)**: `=B5-C5`
  * *Logic*: Dynamically subtracts closed tickets from total tickets.
* **SLA Compliance %**: `=COUNTIF('Cleaned Data'!J:J,"Met")/B5`
  * *Logic*: Divides tickets meeting service guidelines by total ticket volume (formatted as `0.00%`).
* **Avg Resolution Time (Hrs)**: `=AVERAGE('Cleaned Data'!I:I)`
  * *Logic*: Returns the average resolution duration. Empty cells (from open tickets) are automatically ignored.
* **Avg CSAT Score**: `=AVERAGE('Cleaned Data'!K:K)`
  * *Logic*: Computes mean customer feedback survey ratings.

### B. Interactive Ticket Search Tool
The dashboard implements a search tool in row 13 driven by the search input cell `C10`:
* **Formula Example (Agent Name Lookup - C13)**:
  `=IF($C$10="","",_xlfn.XLOOKUP($C$10,'Cleaned Data'!$A:$A,'Cleaned Data'!$C:$C,"Not Found"))`
* *Logic*:
  * The outer `IF` statement checks if the search input box is empty. If it is, the cells remain clean and blank rather than throwing `#N/A` errors.
  * The inner `_xlfn.XLOOKUP` retrieves fields (Customer, Agent, Department, Priority, SLA, CSAT, Status) from the `Cleaned Data` sheet based on the input Ticket ID.
  * If a Ticket ID is entered but does not exist, `XLOOKUP` displays `"Not Found"`.

---

## 3. Data Visualization & Summaries

The workbook leverages interactive charts to highlight critical support insights:

* **Department Workload Distribution (Bar Chart)**: Visualizes ticket counts across departments, exposing the Technical division as the highest volume area.
* **SLA Compliance by Channel (Donut Chart)**: Details the proportion of met versus breached SLAs across phone, email, chat, and social media channels.
* **CSAT Score vs. Resolution Time (Scatter Plot)**: Maps the correlation between resolution speed and customer satisfaction, visually proving that satisfaction drops significantly as resolution duration extends.
