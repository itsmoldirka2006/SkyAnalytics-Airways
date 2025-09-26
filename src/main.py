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
            "name": "Total Airlines by Country",
            "sql": "SELECT airline_country, COUNT(*) as airline_count FROM airline GROUP BY airline_country ORDER BY airline_count DESC LIMIT 5;"
        },
        {
            "name": "Baggage Check Results", 
            "sql": "SELECT check_result, COUNT(*) as result_count FROM baggage_check GROUP BY check_result;"
        },
        {
            "name": "Average Baggage Weight",
            "sql": "SELECT ROUND(AVG(weight_in_kg), 2) as avg_weight FROM baggage;"
        },
        {
            "name": "Airlines with Recent Updates",
            "sql": "SELECT airline_name, update_at FROM airline WHERE update_at >= '2024-01-01' ORDER BY update_at DESC LIMIT 5;"
        }
    ]
    
    for query in queries:
        try:
            df = pd.read_sql_query(query["sql"], conn)
            print(f"\n {query['name']}:")
            print(df)
            print("-" * 50)
        except Exception as e:
            print(f"Error in {query['name']}: {e}")

def main():
    conn = connect_db()
    if not conn:
        return
    run_queries(conn)
    conn.close()
    print("\nDatabase analysis completed!")
    
if __name__ == "__main__":
    main()