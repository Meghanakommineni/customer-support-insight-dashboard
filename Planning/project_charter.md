# Project Charter: Customer Support Insights Dashboard

## 1. Problem Statement
The Customer Support department currently lacks a unified system to monitor key operational and performance metrics. Support leadership cannot easily track ticket volume distributions, agent performance, resolution times, or customer satisfaction (CSAT) trends. This lack of data-driven insights leads to:
* Inefficiencies in ticket allocation and workload management.
* SLA (Service Level Agreement) breaches going undetected.
* Difficulty in identifying low-performing areas or agents requiring training.
* Inability to trace customer dissatisfaction back to specific support categories or response delays.

To solve this, we need a robust analytics pipeline that consolidates support ticket data and visualizes it in a clear, interactive dashboard.

---

## 2. Project Scope
This project will use sample ticket data to simulate a production-grade business intelligence flow.
* **In Scope**:
  * Developing a relational database schema in SQL (MySQL) to store structured support ticket logs.
  * Writing complex SQL queries to profile data and calculate key performance statistics.
  * Performing exploratory data cleaning and profiling using Microsoft Excel.
  * Building an interactive, star-schema data model in Power BI.
  * Designing an executive-ready dashboard showcasing operational KPIs, trends, and agent performance.
  * Publishing project documentation and version history on GitHub.
* **Out of Scope**:
  * Real-time streaming data ingestion (pipeline will use batch-processed historical datasets).
  * Direct integration with live CRM platforms (e.g., Salesforce, Zendesk API).
  * Advanced machine learning predictions (e.g., automated ticket routing, NLP sentiment analysis).

---

## 3. Project Objectives
1. **Consolidate Data**: Set up a structured, clean relational database to serve as a reliable source of truth.
2. **Standardize Metrics**: Establish agreed-upon definitions for key support metrics like Average Resolution Time (ART) and SLA Compliance.
3. **Actionable Insights**: Empower support managers to identify specific action items (e.g., targeting channels with low SLA compliance or categories with high resolution times).
4. **Professional Presentation**: Create a clean, visually compelling, and intuitive BI dashboard following modern design principles.

---

## 4. Key Performance Indicators (KPIs)
We will monitor the following primary KPIs:
* **Total Tickets**: Total count of customer support tickets received.
* **Open Tickets**: Tickets currently in an unresolved state (e.g., New, Open, Pending).
* **Closed Tickets**: Tickets successfully resolved/closed.
* **SLA Compliance Rate (%)**: 
  $$\text{SLA Compliance \%} = \left( \frac{\text{Tickets resolved within SLA limit}}{\text{Total resolved tickets}} \right) \times 100$$
* **Average Resolution Time (ART)**: The average time taken to close a ticket (usually measured in hours or days).
* **Average Customer Satisfaction Score (CSAT)**: The average rating given by customers post-resolution (on a scale of 1 to 5).
* **Ticket Backlog**: Outstanding unresolved tickets at the end of the reporting period.

---

## 5. Key Business Questions
1. **Workload Analysis**: Which ticket categories (e.g., Billing, Technical, Account) have the highest ticket volumes?
2. **SLA Compliance**: Which support channels (e.g., Email, Chat, Phone) have the highest SLA breach rates, and why?
3. **Agent Performance**: Who are the top-performing agents based on CSAT and resolution time? Who might need additional training or support?
4. **Trend Analysis**: Is there a monthly or weekly trend in ticket volumes? Are there seasonal spikes?
5. **Satisfaction Drivers**: Is there a direct correlation between longer resolution times and lower CSAT scores?

---

## 6. Expected Outcomes
* **Support Managers** can optimize team scheduling and resources based on ticket trends.
* **Training Lead** can design tailored training modules for agents lagging in CSAT or resolution times.
* **Executive Leadership** has immediate visibility into the overall health and cost-efficiency of the support organization.
