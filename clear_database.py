#!/usr/bin/env python3
"""
Script to safely clear the rfq_system.db database.
This script drops and recreates all tables, giving you a fresh empty database.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from app.models.database import Base, engine
    
    print("Clearing database...")
    print("-" * 50)
    
    # Drop all tables
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✓ Tables dropped")
    
    # Recreate all tables
    print("Recreating tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")
    
    print("-" * 50)
    print("✓ Database cleared successfully!")
    print("\nYou can now restart the backend server.")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    sys.exit(1)
