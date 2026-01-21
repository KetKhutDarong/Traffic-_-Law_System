# migrate_db.py
import sqlite3
import os

def migrate_database():
    """Add missing columns to existing database"""
    
    # Your database is likely named 'traffic_law.db' or similar
    # Check what database file exists
    possible_db_files = ['traffic_law.db', 'instance/traffic_law.db', 'traffic_law_expert.db']
    
    db_file = None
    for file in possible_db_files:
        if os.path.exists(file):
            db_file = file
            break
    
    if not db_file:
        # Check for any .db file in current directory
        for file in os.listdir('.'):
            if file.endswith('.db'):
                db_file = file
                break
    
    if not db_file:
        print("No database file found!")
        print("Looking for: traffic_law.db, instance/traffic_law.db, or any .db file")
        return
    
    print(f"Found database: {db_file}")
    print("Connecting to database...")
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        # Check if violation_records table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='violation_records'")
        if not cursor.fetchone():
            print("violation_records table doesn't exist!")
            print("You need to run the application first to create the tables.")
            return
        
        # Check current table structure
        cursor.execute("PRAGMA table_info(violation_records)")
        columns = cursor.fetchall()
        
        print("\nCurrent table structure:")
        print("Column Name | Type")
        print("-" * 30)
        for col in columns:
            print(f"{col[1]:<12} | {col[2]}")
        
        # Check for driver_name column
        column_names = [col[1] for col in columns]
        
        if 'driver_name' not in column_names:
            print("\n✗ Missing 'driver_name' column!")
            print("Adding driver_name column...")
            cursor.execute('ALTER TABLE violation_records ADD COLUMN driver_name TEXT')
            print("✓ Column 'driver_name' added successfully!")
        else:
            print("\n✓ 'driver_name' column already exists")
        
        # Check other important columns
        missing_columns = []
        important_columns = [
            ('license_number', 'TEXT'),
            ('plate_number', 'TEXT'), 
            ('vehicle_type', 'TEXT'),
            ('has_helmet', 'TEXT'),
            ('speed', 'INTEGER'),
            ('has_license', 'TEXT'),
            ('violations', 'TEXT'),
            ('total_fine', 'INTEGER')
        ]
        
        for col_name, col_type in important_columns:
            if col_name not in column_names:
                missing_columns.append((col_name, col_type))
        
        if missing_columns:
            print(f"\nFound {len(missing_columns)} missing columns:")
            for col_name, col_type in missing_columns:
                print(f"  - {col_name} ({col_type})")
            
            print("\nAdding missing columns...")
            for col_name, col_type in missing_columns:
                try:
                    cursor.execute(f'ALTER TABLE violation_records ADD COLUMN {col_name} {col_type}')
                    print(f"✓ Added {col_name} column")
                except Exception as e:
                    print(f"✗ Error adding {col_name}: {e}")
        else:
            print("\n✓ All important columns are present")
        
        conn.commit()
        print("\n" + "="*50)
        print("✓ MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*50)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("="*50)
    print("DATABASE MIGRATION TOOL")
    print("="*50)
    print("\nThis tool will fix the 'driver_name' column issue.")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    
    try:
        input()
        migrate_database()
    except KeyboardInterrupt:
        print("\n\nMigration cancelled by user.")
    except Exception as e:
        print(f"\nError: {e}")
    
    print("\nPress Enter to exit...")
    input()