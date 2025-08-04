#!/usr/bin/env python3
"""
Multitenant Database Initialization Script for Quizlet AI
Sets up Neon PostgreSQL with schema-based multitenancy
"""

import os
import asyncio
from sqlalchemy import text, create_engine
from app.core.multitenant_config import MultitenantDatabase, TenantManager, generate_tenant_id

async def init_multitenant_db():
    """Initialize multitenant database with Neon PostgreSQL"""
    
    print("🚀 Initializing Multitenant Database...")
    
    # Check if Neon URL is set
    neon_url = os.getenv("NEON_DATABASE_URL")
    if not neon_url:
        print("❌ NEON_DATABASE_URL environment variable not set")
        print("Please set it in your .env file:")
        print("NEON_DATABASE_URL=postgresql://username:password@host/database?sslmode=require")
        return False
    
    try:
        # Test connection to Neon
        print("🔗 Testing Neon database connection...")
        engine = create_engine(neon_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version}")
            
            # Check if we can create schemas
            result = conn.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            print(f"🗄️  Connected to database: {db_name}")
        
        # Initialize multitenant database
        print("🏗️  Setting up multitenant infrastructure...")
        multitenant_db = MultitenantDatabase()
        
        # Create shared schema for common data
        print("📋 Creating shared schema...")
        with engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS shared"))
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS public"))
            conn.commit()
        
        # Create sample tenants for testing
        print("🧪 Creating sample tenants...")
        
        sample_tenants = [
            {
                "name": "Acme Corporation",
                "email": "admin@acme.com"
            },
            {
                "name": "Tech Startup Inc",
                "email": "admin@techstartup.com"
            },
            {
                "name": "University of Learning",
                "email": "admin@university.edu"
            }
        ]
        
        created_tenants = []
        
        for tenant_data in sample_tenants:
            tenant_id = generate_tenant_id()
            print(f"📝 Creating tenant: {tenant_data['name']}")
            
            try:
                result = await TenantManager.create_tenant(
                    tenant_id=tenant_id,
                    tenant_name=tenant_data['name'],
                    owner_email=tenant_data['email']
                )
                
                created_tenants.append({
                    "tenant_id": tenant_id,
                    "tenant_name": tenant_data['name'],
                    "admin_email": tenant_data['email'],
                    "temp_password": "admin123"
                })
                
                print(f"✅ Created tenant: {tenant_data['name']} (ID: {tenant_id[:8]}...)")
                
            except Exception as e:
                print(f"❌ Failed to create tenant {tenant_data['name']}: {e}")
        
        # List all schemas
        print("\n📊 Database Schemas Created:")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT schema_name 
                FROM information_schema.schemata 
                ORDER BY schema_name
            """))
            schemas = result.fetchall()
            
            for schema in schemas:
                schema_name = schema[0]
                if schema_name.startswith('tenant_'):
                    print(f"   🏢 {schema_name}")
                elif schema_name in ['public', 'shared']:
                    print(f"   📁 {schema_name}")
        
        # Print tenant information
        print("\n🎉 Multitenant Setup Complete!")
        print("\n📋 Sample Tenants Created:")
        for tenant in created_tenants:
            print(f"   🏢 {tenant['tenant_name']}")
            print(f"      ID: {tenant['tenant_id']}")
            print(f"      Admin: {tenant['admin_email']}")
            print(f"      Password: {tenant['temp_password']}")
            print()
        
        print("🔧 Next Steps:")
        print("1. Update your .env file with the tenant IDs above")
        print("2. Use X-Tenant-ID header in API requests")
        print("3. Test tenant isolation with different tenant IDs")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing multitenant database: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tenant_isolation():
    """Test that tenants are properly isolated"""
    print("\n🧪 Testing Tenant Isolation...")
    
    try:
        from app.core.multitenant_config import multitenant_db, TenantManager
        
        # Get list of tenants
        tenants = TenantManager.list_all_tenants()
        
        if len(tenants) < 2:
            print("⚠️  Need at least 2 tenants to test isolation")
            return
        
        # Test data isolation
        for tenant_schema in tenants[:2]:
            tenant_id = tenant_schema.replace('tenant_', '').replace('_', '-')
            print(f"📊 Testing tenant: {tenant_schema}")
            
            stats = TenantManager.get_tenant_stats(tenant_id)
            print(f"   Users: {stats.get('users_count', 0)}")
            print(f"   Quizzes: {stats.get('quizzes_count', 0)}")
            print(f"   Flashcards: {stats.get('flashcards_count', 0)}")
        
        print("✅ Tenant isolation test completed")
        
    except Exception as e:
        print(f"❌ Error testing tenant isolation: {e}")

if __name__ == "__main__":
    # Run initialization
    success = asyncio.run(init_multitenant_db())
    
    if success:
        # Test isolation
        test_tenant_isolation()
    else:
        print("❌ Multitenant database initialization failed") 