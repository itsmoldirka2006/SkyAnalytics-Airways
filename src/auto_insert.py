import psycopg2
import time
import random
from datetime import datetime

db_config = {
    'host': 'localhost',
    'database': 'skyanalytics_airways',
    'user': 'postgres',
    'password': '0000',
    'port': '5432'
}

def get_next_boarding_pass_id():
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
        cursor.execute("""
            SELECT b.booking_id 
            FROM booking b 
            LEFT JOIN boarding_pass bp ON b.booking_id = bp.booking_id 
            WHERE bp.booking_id IS NULL 
            LIMIT 100
        """)
        booking_ids = [row[0] for row in cursor.fetchall()]
        
        if not booking_ids:
            cursor.execute("SELECT booking_id FROM booking LIMIT 100")
            booking_ids = [row[0] for row in cursor.fetchall()]
        
        if not booking_ids:
            print("No valid bookings found")
            return None, None
        
        next_id = get_next_boarding_pass_id()
        column_names = ['boarding_pass_id', 'booking_id', 'seat', 'boarding_time', 'created_at']
        
        booking_id = random.choice(booking_ids)
        seat = f"{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}{random.randint(1, 30)}"
        boarding_time = datetime.now().date()
        created_at = datetime.now().date()
        
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
            print(f"Inserted boarding pass ID {data_values[0]}: Booking {data_values[1]}, Seat {data_values[2]}")
        else:
            print("Skipping insertion - no valid data generated")
            
    except psycopg2.IntegrityError as e:
        print(f"Integrity error: {e}")
        conn.rollback()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

try:
    print("Starting auto-insert script for boarding_pass table...")
    print("Press Ctrl+C to stop")
    
    insert_count = 0
    while True:
        insert_boarding_pass()
        insert_count += 1
        time.sleep(15)  
        
except KeyboardInterrupt:
    print(f"\nScript stopped by user. Total inserts: {insert_count}")