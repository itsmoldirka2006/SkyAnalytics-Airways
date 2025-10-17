import psycopg2
import time
import random
from datetime import datetime, timedelta

db_config = {
    'host': 'localhost',
    'database': 'skyanalytics_airways',
    'user': 'postgres',
    'password': '0000',
    'port': '5432'
}

def get_next_boarding_pass_id():
    """Get the next available boarding_pass_id"""
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COALESCE(MAX(boarding_pass_id), 0) + 1 FROM boarding_pass")
        next_id = cursor.fetchone()[0]
        return next_id
    except Exception as e:
        print(f"Error getting next ID: {e}")
        return 1
    finally:
        cursor.close()
        conn.close()

def generate_boarding_pass():
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT booking_id FROM booking LIMIT 200")
        booking_ids = [row[0] for row in cursor.fetchall()]
        
        if not booking_ids:
            print("No valid bookings found")
            return None, None
        
        next_id = get_next_boarding_pass_id()
        column_names = ['boarding_pass_id', 'booking_id', 'seat', 'boarding_time', 'created_at']
        
        booking_id = random.choice(booking_ids)
        seat = f"{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}{random.randint(1, 30)}"
        
        current_time = datetime.now()
        boarding_time = current_time
        created_at = current_time.date()
        
        data_values = [next_id, booking_id, seat, boarding_time, created_at]
        
        return column_names, data_values
        
    except Exception as e:
        print(f"Error generating boarding pass: {e}")
        return None, None
    finally:
        cursor.close()
        conn.close()

def insert_boarding_pass():
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        column_names, data_values = generate_boarding_pass()
        if column_names and data_values:
            placeholders = ', '.join(['%s'] * len(data_values))
            columns_str = ', '.join(column_names)
            
            query = f'''
                INSERT INTO boarding_pass 
                ({columns_str})
                VALUES ({placeholders})
            '''
            
            cursor.execute(query, data_values)
            conn.commit()
            print(f"Inserted boarding pass ID {data_values[0]}: Booking {data_values[1]}, Seat {data_values[2]} at {datetime.now().strftime('%H:%M:%S')}")
        else:
            print("Skipping insertion - no valid data generated")
            
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

try:
    print("STARTING ENHANCED AUTO-INSERT SCRIPT")
    print("Inserting every 10 seconds for maximum visibility")
    print("Script started at:", datetime.now().strftime('%H:%M:%S'))
    print("Press Ctrl+C to stop\n")
    
    insert_count = 0
    while True:
        insert_boarding_pass()
        insert_count += 1
  
        for i in range(10, 0, -1):
            print(f"Next insert in: {i} seconds", end='\r')
            time.sleep(1)
        print(" " * 30, end='\r')  
        
except KeyboardInterrupt:
    print(f"\n\nScript stopped by user. Total inserts: {insert_count}")
    print("Script ended at:", datetime.now().strftime('%H:%M:%S'))