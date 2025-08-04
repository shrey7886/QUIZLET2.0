#!/usr/bin/env python3
"""
Test Neon Database Connection
"""

import os
from sqlalchemy import create_engine, text

def test_neon_connection():
    """Test connection to Neon database"""
    
    # Get database URL from environment
    neon_url = os.getenv("NEON_DATABASE_URL")
    
    if not neon_url:
        print("❌ NEON_DATABASE_URL environment variable not set")
        print("Please set it in your .env file or environment")
        return False
    
    try:
        # Create engine
        engine = create_engine(neon_url, echo=False)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            
            print("✅ Neon database connected successfully!")
            print(f"📊 PostgreSQL version: {version}")
            
            # Test if we can create tables
            result = conn.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            print(f"🗄️  Connected to database: {db_name}")
            
            return True
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check your NEON_DATABASE_URL format")
        print("2. Ensure SSL is configured: ?sslmode=require")
        print("3. Verify your IP is whitelisted in Neon")
        print("4. Check username/password credentials")
        return False

if __name__ == "__main__":
    test_neon_connection() 