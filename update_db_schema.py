#!/usr/bin/env python
import os
import sqlite3
import sys
import shutil
from datetime import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.models.base import Base
from src.models.enhanced_models import Goal, Habit
from src.models.value import Value
from src.models.category import Category

def backup_database(db_path):
    """Create a backup of the existing database"""
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(db_path, backup_path)
        print(f"Created backup of database at {backup_path}")
        return True
    return False

def recreate_database(db_path):
    """Drop and recreate the database with the new schema"""
    # Create a new engine
    engine = create_engine(f'sqlite:///{db_path}')
    
    # Drop all tables
    Base.metadata.drop_all(engine)
    
    # Create all tables with new schema
    Base.metadata.create_all(engine)
    
    print(f"Recreated database schema at {db_path}")
    return engine

def main():
    # Define database path
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, 'life_system.db')
    
    print("This script will update the database schema for the LifeSystem application.")
    print("It will create a backup of your existing database and then recreate the schema.")
    print("Your existing data may not be preserved if the schema changes are extensive.")
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"No database found at {db_path}. Creating a new database.")
        engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(engine)
        print("Database created successfully.")
        return
    
    # Backup existing database
    if backup_database(db_path):
        # Recreate database with new schema
        engine = recreate_database(db_path)
        
        # Output database structure for verification
        inspector = inspect(engine)
        print("\nUpdated database schema:")
        for table_name in inspector.get_table_names():
            print(f"\nTable: {table_name}")
            for column in inspector.get_columns(table_name):
                print(f"  {column['name']} ({column['type']})")
        
        print("\nDatabase schema update completed successfully.")
        print("Note: You may need to re-add your data or restore it from a backup manually.")
        print("A backup of your previous database has been created in the data directory.")
    else:
        print("Failed to backup database. Update aborted.")

if __name__ == "__main__":
    main() 