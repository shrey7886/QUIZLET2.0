#!/usr/bin/env python3
"""
Integration Test for Quizlet AI Quiz Generator
Tests all connections between frontend and backend before deployment
"""

import requests
import json
import time
from typing import Dict, Any

class IntegrationTester:
    def __init__(self):
        self.base_url = "http://localhost:8001"  # Local testing
        self.api_url = f"{self.base_url}/api"
        self.test_user = {
            "email": "integration-test@example.com",
            "username": "integrationtest",
            "password": "testpassword123"
        }
        self.auth_token = None
        
    def print_section(self, title: str):
        """Print a formatted section header"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    
    def print_result(self, test_name: str, success: bool, details: str = ""):
        """Print formatted test result"""
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}")
        if details:
            print(f"   {details}")
    
    def test_backend_health(self):
        """Test backend health endpoint"""
        self.print_section("BACKEND HEALTH CHECK")
        
        try:
            response = requests.get(f"{self.base_url}/health")
            success = response.status_code == 200
            self.print_result("Health Endpoint", success, f"Status: {response.status_code}")
            
            if success:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
            
            return success
        except Exception as e:
            self.print_result("Health Endpoint", False, f"Error: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test all API endpoints"""
        self.print_section("API ENDPOINTS TEST")
        
        endpoints = [
            ("GET", "/api/auth/me", "Protected endpoint"),
            ("POST", "/api/auth/register", "Registration endpoint"),
            ("POST", "/api/auth/login", "Login endpoint"),
            ("GET", "/api/quiz/history", "Quiz history endpoint"),
            ("GET", "/api/analytics/dashboard", "Analytics dashboard endpoint"),
            ("GET", "/api/flashcards/deck", "Flashcards endpoint"),
            ("GET", "/api/chat/rooms", "Chat rooms endpoint"),
        ]
        
        results = []
        for method, endpoint, description in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                if method == "GET":
                    response = requests.get(url)
                elif method == "POST":
                    response = requests.post(url, json={})
                
                # 401 is expected for protected endpoints without auth
                # 422 is expected for POST endpoints with empty data
                success = response.status_code in [200, 401, 422]
                self.print_result(f"{method} {endpoint}", success, f"{description} - Status: {response.status_code}")
                results.append(success)
                
            except Exception as e:
                self.print_result(f"{method} {endpoint}", False, f"{description} - Error: {e}")
                results.append(False)
        
        return all(results)
    
    def test_authentication_flow(self):
        """Test complete authentication flow"""
        self.print_section("AUTHENTICATION FLOW TEST")
        
        # Test registration
        try:
            response = requests.post(f"{self.api_url}/auth/register", json=self.test_user)
            success = response.status_code in [200, 400]  # 400 if user already exists
            self.print_result("User Registration", success, f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   User registered successfully")
            elif response.status_code == 400 and "already registered" in response.json().get("detail", ""):
                print(f"   User already exists (expected)")
            
        except Exception as e:
            self.print_result("User Registration", False, f"Error: {e}")
            return False
        
        # Test login
        try:
            response = requests.post(f"{self.api_url}/auth/login", json={
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            })
            success = response.status_code == 200
            self.print_result("User Login", success, f"Status: {response.status_code}")
            
            if success:
                self.auth_token = response.json().get("access_token")
                print(f"   Token obtained successfully")
            else:
                print(f"   Login failed: {response.json()}")
                return False
                
        except Exception as e:
            self.print_result("User Login", False, f"Error: {e}")
            return False
        
        # Test protected endpoint
        if self.auth_token:
            try:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = requests.get(f"{self.api_url}/auth/me", headers=headers)
                success = response.status_code == 200
                self.print_result("Protected Endpoint", success, f"Status: {response.status_code}")
                
                if success:
                    user_data = response.json()
                    print(f"   User: {user_data.get('username', 'Unknown')}")
                
                return success
                
            except Exception as e:
                self.print_result("Protected Endpoint", False, f"Error: {e}")
                return False
        
        return False
    
    def test_quiz_generation(self):
        """Test quiz generation with authentication"""
        self.print_section("QUIZ GENERATION TEST")
        
        if not self.auth_token:
            self.print_result("Quiz Generation", False, "No auth token available")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            quiz_config = {
                "topic": "Python Programming",
                "difficulty": "medium",
                "num_questions": 2,
                "time_limit": 300
            }
            
            response = requests.post(f"{self.api_url}/quiz/generate", json=quiz_config, headers=headers)
            success = response.status_code == 200
            self.print_result("Quiz Generation", success, f"Status: {response.status_code}")
            
            if success:
                quiz_data = response.json()
                questions = quiz_data.get('quiz', [])
                print(f"   Generated {len(questions)} questions")
                if questions:
                    print(f"   First question: {questions[0].get('question', 'N/A')[:50]}...")
            else:
                print(f"   Error: {response.json()}")
            
            return success
            
        except Exception as e:
            self.print_result("Quiz Generation", False, f"Error: {e}")
            return False
    
    def test_frontend_build(self):
        """Test if frontend can be built successfully"""
        self.print_section("FRONTEND BUILD TEST")
        
        import subprocess
        import os
        
        try:
            # Check if we're in the right directory
            if not os.path.exists("frontend/package.json"):
                self.print_result("Frontend Build", False, "frontend/package.json not found")
                return False
            
            # Try to build the frontend
            result = subprocess.run(
                ["npm", "run", "build"], 
                cwd="frontend", 
                capture_output=True, 
                text=True
            )
            
            success = result.returncode == 0
            self.print_result("Frontend Build", success, f"Return code: {result.returncode}")
            
            if not success:
                print(f"   Build error: {result.stderr}")
            else:
                print(f"   Build successful!")
            
            return success
            
        except Exception as e:
            self.print_result("Frontend Build", False, f"Error: {e}")
            return False
    
    def test_vercel_configuration(self):
        """Test Vercel configuration files"""
        self.print_section("VERCEL CONFIGURATION TEST")
        
        import os
        
        # Check root vercel.json
        if os.path.exists("vercel.json"):
            self.print_result("Root vercel.json", True, "Found")
        else:
            self.print_result("Root vercel.json", False, "Missing")
            return False
        
        # Check backend requirements.txt
        if os.path.exists("backend/requirements.txt"):
            self.print_result("Backend requirements.txt", True, "Found")
        else:
            self.print_result("Backend requirements.txt", False, "Missing")
            return False
        
        # Check frontend package.json
        if os.path.exists("frontend/package.json"):
            self.print_result("Frontend package.json", True, "Found")
        else:
            self.print_result("Frontend package.json", False, "Missing")
            return False
        
        return True
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🔍 Starting Integration Tests for Quizlet AI Quiz Generator")
        print(f"📍 Testing at: {self.base_url}")
        
        tests = [
            ("Backend Health", self.test_backend_health),
            ("API Endpoints", self.test_api_endpoints),
            ("Authentication Flow", self.test_authentication_flow),
            ("Quiz Generation", self.test_quiz_generation),
            ("Frontend Build", self.test_frontend_build),
            ("Vercel Configuration", self.test_vercel_configuration),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append(result)
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append(False)
        
        # Summary
        print(f"\n{'='*60}")
        print("  🎯 INTEGRATION TEST SUMMARY")
        print(f"{'='*60}")
        
        passed = sum(results)
        total = len(results)
        
        print(f"✅ Tests Passed: {passed}/{total}")
        print(f"❌ Tests Failed: {total - passed}/{total}")
        
        if passed == total:
            print("🎉 All tests passed! Ready for deployment!")
            print("\n📋 Deployment Checklist:")
            print("✅ Backend API endpoints working")
            print("✅ Authentication system functional")
            print("✅ Quiz generation working")
            print("✅ Frontend builds successfully")
            print("✅ Vercel configuration ready")
            print("\n🚀 Ready to deploy with: vercel --prod")
        else:
            print("⚠️  Some tests failed. Please fix issues before deployment.")
        
        return passed == total

if __name__ == "__main__":
    tester = IntegrationTester()
    tester.run_all_tests() 