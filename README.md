# SkyAnalytics Airways - Data Analytics Project

## Project Overview
SkyAnalytics Airways specializes in airline operations optimization through data analysis.

## Setup Instructions
1. Install PostgreSQL and pgAdmin4
2. Create database: `skyanalytics_airways`
3. Run the SQL scripts in database/ folder
4. Install Python dependencies: `pip install -r requirements.txt`
5. Run analysis: `python src/main.py`

## Tools Used
- PostgreSQL, pgAdmin4
- Python, pandas, psycopg2

## Data Source
The original dataset is located in `database/airport_dump.sql`. This file contains:
- 5 tables: airline, airport, baggage_check, baggage, boarding_pass
- Sample data for airline operations analysis
- Total of 1,070+ records across all tables

## Sample Analytics

!(docs/analytics_screenshot.png)

*Figure 1: Python script output showing airline analytics including country distribution, baggage check results, and average weights.*

!(docs/pgadmin_analytics.png)

*Figure 2: pgAdmin4 query results showing comprehensive airline analytics including country distribution, baggage check statistics, and average weight analysis.*