import psycopg2
import pandas as pd

def connect_db():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="skyanalytics_airways",
            user="postgres",
            password="0000"  
        )
        print("Connected to database successfully!")
        return conn
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def run_queries(conn):
    queries = [
        {
            "name": "1. Basic SELECT with LIMIT (Simple data inspection)",
            "sql": "SELECT * FROM airline LIMIT 10;"
        },
        {
            "name": "2. Filtering with WHERE and sorting with ORDER BY",
            "sql": """
                SELECT airline_name, airline_country, created_at 
                FROM airline 
                WHERE created_at > '2024-01-01'
                ORDER BY created_at DESC;
            """
        },
        {
            "name": "3. Aggregation with GROUP BY and COUNT",
            "sql": """
                SELECT airline_country, COUNT(*) as airline_count
                FROM airline 
                GROUP BY airline_country 
                ORDER BY airline_count DESC;
            """
        },
        {
            "name": "4. Aggregation with AVG, MIN, MAX",
            "sql": """
                SELECT 
                    ROUND(AVG(weight_in_kg), 2) as average_weight,
                    ROUND(MIN(weight_in_kg), 2) as min_weight,
                    ROUND(MAX(weight_in_kg), 2) as max_weight
                FROM baggage;
            """
        },
        {
            "name": "5. JOIN between two tables",
            "sql": """
                SELECT a.airline_name, b.weight_in_kg
                FROM airline a
                JOIN baggage b ON a.airline_id = b.baggage_id
                LIMIT 10;
            """
        },
        {
            "name": "6. Baggage check results analysis",
            "sql": """
                SELECT check_result, COUNT(*) as result_count
                FROM baggage_check 
                GROUP BY check_result 
                ORDER BY result_count DESC;
            """
        },
        {
            "name": "7. Heavy baggage analysis (>30kg)",
            "sql": """
                SELECT COUNT(*) as heavy_baggage_count
                FROM baggage 
                WHERE weight_in_kg > 30;
            """
        },
        {
            "name": "8. Monthly baggage creation pattern",
            "sql": """
                SELECT 
                    EXTRACT(MONTH FROM created_date) as month_number,
                    COUNT(*) as baggage_count
                FROM baggage 
                GROUP BY month_number 
                ORDER BY month_number;
            """
        },
        {
            "name": "9. Airlines with missing codes",
            "sql": """
                SELECT airline_name, airline_country 
                FROM airline 
                WHERE airline_code IS NULL;
            """
        },
        {
            "name": "10. Complex JOIN with multiple tables",
            "sql": """
                SELECT 
                    a.airline_name,
                    b.weight_in_kg,
                    bc.check_result,
                    bp.seat
                FROM airline a
                JOIN baggage b ON a.airline_id = b.baggage_id
                JOIN baggage_check bc ON b.booking_id = bc.booking_id
                JOIN boarding_pass bp ON b.booking_id = bp.booking_id
                LIMIT 10;
            """
        }
    ]
    
    print("Running 10 Analytical Queries for SkyAnalytics Airways\n")
    print("=" * 70)
    
    for i, query in enumerate(queries, 1):
        try:
            df = pd.read_sql_query(query["sql"], conn)
            print(f"\n{query['name']}")
            print(f"Query: {query['sql'].strip().replace(chr(10), ' ')[:80]}...")
            print(f"Results: {len(df)} rows returned")
            print("─" * 50)
            
            if len(df) > 0:
                print(df.to_string(index=False))
            else:
                print("No results returned")
                
            print("─" * 50)
            
        except Exception as e:
            print(f"Error in Query {i}: {query['name']}")
            print(f"Error details: {e}")
            print("─" * 50)

def display_summary(conn):
    try:
        print("\n" + "=" * 70)
        print("DATABASE SUMMARY STATISTICS")
        print("=" * 70)
        
        tables = ['airline', 'airport', 'baggage', 'baggage_check', 'boarding_pass']
        for table in tables:
            count = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table}", conn)
            print(f"{table.capitalize():<15}: {count['count'][0]:>4} records")
        
        avg_weight = pd.read_sql_query("SELECT ROUND(AVG(weight_in_kg), 2) as avg FROM baggage", conn)
        heavy_baggage = pd.read_sql_query("SELECT COUNT(*) as heavy FROM baggage WHERE weight_in_kg > 30", conn)
        checked_ratio = pd.read_sql_query("""
            SELECT 
                ROUND(100.0 * SUM(CASE WHEN check_result = 'Checked' THEN 1 ELSE 0 END) / COUNT(*), 1) as checked_percent 
            FROM baggage_check
        """, conn)
        
        print(f"Average baggage weight: {avg_weight['avg'][0]} kg")
        print(f"Heavy baggage (>30kg): {heavy_baggage['heavy'][0]} items")
        print(f"Baggage checked: {checked_ratio['checked_percent'][0]}%")
        
    except Exception as e:
        print(f"Error generating summary: {e}")

def main():
    print("SkyAnalytics Airways - Data Analytics Dashboard")
    print("=" * 70)

    conn = connect_db()
    if not conn:
        print("Cannot proceed without database connection")
        return
    
    try:
        run_queries(conn)
        display_summary(conn)
        
        print("\nAll 10 analytical topics completed successfully!")
        print("Analysis includes: SELECT, WHERE, ORDER BY, GROUP BY, JOIN, Aggregations")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
    
    finally:
        conn.close()
        print("\nDatabase connection closed.")

if __name__ == "__main__":
    main()