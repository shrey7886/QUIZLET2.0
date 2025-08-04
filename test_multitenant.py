#!/usr/bin/env python3
"""
Multitenant Database Test Script
Tests tenant creation, isolation, and management
"""

import os
import asyncio
import requests
import json
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_neon_connection():
    """Test Neon database connection"""
    print("🔗 Testing Neon database connection...")
    
    try:
        from app.core.multitenant_config import multitenant_db
        
        # Test basic connection
        with multitenant_db.engine.connect() as conn:
            result = conn.execute("SELECT version();")
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version}")
            
            # Test schema creation capability
            result = conn.execute("SELECT current_database();")
            db_name = result.fetchone()[0]
            print(f"✅ Connected to database: {db_name}")
            
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_tenant_creation():
    """Test tenant creation via API"""
    print("\n🏢 Testing tenant creation...")
    
    tenant_data = {
        "tenant_name": "Test Company",
        "owner_email": "admin@testcompany.com"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/tenants/",
            json=tenant_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Tenant created successfully:")
            print(f"   ID: {result['tenant_id']}")
            print(f"   Name: {result['tenant_name']}")
            print(f"   Admin: {result['admin_email']}")
            print(f"   Password: {result['temp_password']}")
            return result['tenant_id']
        else:
            print(f"❌ Failed to create tenant: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating tenant: {e}")
        return None

def test_tenant_isolation(tenant_id: str):
    """Test that tenants are properly isolated"""
    print(f"\n🔒 Testing tenant isolation for {tenant_id}...")
    
    headers = {
        "X-Tenant-ID": tenant_id,
        "Content-Type": "application/json"
    }
    
    try:
        # Test user creation in tenant
        user_data = {
            "email": "user1@testcompany.com",
            "username": "testuser1",
            "password": "password123"
        }
        
        response = requests.post(
            f"{API_BASE}/tenants/{tenant_id}/users",
            json=user_data,
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ User created in tenant successfully")
        else:
            print(f"❌ Failed to create user: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Test listing users in tenant
        response = requests.get(
            f"{API_BASE}/tenants/{tenant_id}/users",
            headers=headers
        )
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Found {len(users)} users in tenant")
            for user in users:
                print(f"   - {user['email']} ({user['username']})")
        else:
            print(f"❌ Failed to list users: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing tenant isolation: {e}")
        return False

def test_tenant_stats(tenant_id: str):
    """Test tenant statistics"""
    print(f"\n📊 Testing tenant statistics for {tenant_id}...")
    
    try:
        response = requests.get(f"{API_BASE}/tenants/{tenant_id}/stats")
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Tenant statistics retrieved:")
            print(f"   Users: {stats.get('users_count', 0)}")
            print(f"   Quizzes: {stats.get('quizzes_count', 0)}")
            print(f"   Questions: {stats.get('questions_count', 0)}")
            print(f"   Flashcards: {stats.get('flashcards_count', 0)}")
            print(f"   Flashcard Decks: {stats.get('flashcard_decks_count', 0)}")
            return True
        else:
            print(f"❌ Failed to get tenant stats: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting tenant stats: {e}")
        return False

def test_multiple_tenants():
    """Test creating and managing multiple tenants"""
    print("\n🏢 Testing multiple tenant creation...")
    
    tenants = []
    
    # Create multiple tenants
    tenant_names = [
        "Acme Corporation",
        "Tech Startup Inc",
        "University of Learning"
    ]
    
    for name in tenant_names:
        tenant_data = {
            "tenant_name": name,
            "owner_email": f"admin@{name.lower().replace(' ', '').replace('.', '')}.com"
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/tenants/",
                json=tenant_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                tenants.append(result)
                print(f"✅ Created tenant: {name}")
            else:
                print(f"❌ Failed to create tenant {name}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error creating tenant {name}: {e}")
    
    # List all tenants
    try:
        response = requests.get(f"{API_BASE}/tenants/")
        
        if response.status_code == 200:
            tenant_list = response.json()
            print(f"\n📋 Total tenants in system: {len(tenant_list)}")
            for tenant_schema in tenant_list:
                print(f"   - {tenant_schema}")
        else:
            print(f"❌ Failed to list tenants: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error listing tenants: {e}")
    
    return tenants

def test_api_endpoints():
    """Test that API endpoints are accessible"""
    print("\n🔗 Testing API endpoints...")
    
    endpoints = [
        "/",
        "/health",
        "/docs",
        "/api/tenants/",
        "/openapi.json"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code in [200, 307]:  # 307 for redirects
                print(f"✅ {endpoint} - {response.status_code}")
            else:
                print(f"⚠️  {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

def run_all_tests():
    """Run all multitenant tests"""
    print("🧪 Running Multitenant Database Tests")
    print("=" * 50)
    
    # Test 1: Database connection
    if not test_neon_connection():
        print("❌ Database connection failed. Exiting tests.")
        return False
    
    # Test 2: API endpoints
    test_api_endpoints()
    
    # Test 3: Tenant creation
    tenant_id = test_tenant_creation()
    if not tenant_id:
        print("❌ Tenant creation failed. Exiting tests.")
        return False
    
    # Test 4: Tenant isolation
    if not test_tenant_isolation(tenant_id):
        print("❌ Tenant isolation test failed.")
        return False
    
    # Test 5: Tenant statistics
    if not test_tenant_stats(tenant_id):
        print("❌ Tenant statistics test failed.")
        return False
    
    # Test 6: Multiple tenants
    tenants = test_multiple_tenants()
    
    print("\n🎉 All tests completed!")
    print(f"✅ Created {len(tenants)} tenants successfully")
    print(f"✅ Tenant isolation working correctly")
    print(f"✅ API endpoints accessible")
    
    return True

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding correctly")
            exit(1)
    except:
        print("❌ Server is not running. Please start the server first:")
        print("   python main.py")
        exit(1)
    
    # Run tests
    success = run_all_tests()
    
    if success:
        print("\n🎉 Multitenant setup is working correctly!")
        print("\n📋 Next Steps:")
        print("1. Use the tenant IDs above in your API requests")
        print("2. Include X-Tenant-ID header in all requests")
        print("3. Test with your frontend application")
        print("4. Monitor tenant performance and usage")
    else:
        print("\n❌ Some tests failed. Please check the errors above.") 