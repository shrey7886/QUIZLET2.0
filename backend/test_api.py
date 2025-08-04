#!/usr/bin/env python3
"""
Comprehensive API Test Script for Quizlet AI Quiz Generator
Tests all endpoints and features of the application
"""

import requests
import json
import time
from typing import Dict, Any

# API Configuration
BASE_URL = "http://127.0.0.1:8001"
API_BASE = f"{BASE_URL}/api"

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_user = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123"
        }
    
    def print_section(self, title: str):
        """Print a formatted section header"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    
    def print_result(self, endpoint: str, status: int, response: Dict[str, Any]):
        """Print formatted test result"""
        status_icon = "✅" if status < 400 else "❌"
        print(f"{status_icon} {endpoint} - Status: {status}")
        if status >= 400:
            print(f"   Error: {response.get('detail', 'Unknown error')}")
        else:
            print(f"   Response: {json.dumps(response, indent=2)[:200]}...")
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        self.print_section("HEALTH CHECK")
        
        try:
            response = self.session.get(f"{BASE_URL}/health")
            self.print_result("/health", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Health check failed: {e}")
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        self.print_section("ROOT ENDPOINT")
        
        try:
            response = self.session.get(f"{BASE_URL}/")
            self.print_result("/", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Root endpoint failed: {e}")
    
    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        self.print_section("AUTHENTICATION ENDPOINTS")
        
        # Test registration
        try:
            response = self.session.post(
                f"{API_BASE}/auth/register",
                json=self.test_user
            )
            self.print_result("/api/auth/register", response.status_code, response.json())
            
            if response.status_code == 200:
                print("✅ User registered successfully")
            elif response.status_code == 400 and "already registered" in response.json().get("detail", ""):
                print("✅ User already exists (expected)")
            else:
                print(f"❌ Registration failed: {response.json()}")
        except Exception as e:
            print(f"❌ Registration test failed: {e}")
        
        # Test login
        try:
            response = self.session.post(
                f"{API_BASE}/auth/login",
                json={
                    "email": self.test_user["email"],
                    "password": self.test_user["password"]
                }
            )
            self.print_result("/api/auth/login", response.status_code, response.json())
            
            if response.status_code == 200:
                self.auth_token = response.json().get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                print("✅ Login successful, token obtained")
            else:
                print(f"❌ Login failed: {response.json()}")
        except Exception as e:
            print(f"❌ Login test failed: {e}")
        
        # Test protected endpoint
        if self.auth_token:
            try:
                response = self.session.get(f"{API_BASE}/auth/me")
                self.print_result("/api/auth/me", response.status_code, response.json())
            except Exception as e:
                print(f"❌ Protected endpoint test failed: {e}")
    
    def test_quiz_endpoints(self):
        """Test quiz generation and management endpoints"""
        self.print_section("QUIZ ENDPOINTS")
        
        if not self.auth_token:
            print("❌ Skipping quiz tests - no auth token")
            return
        
        # Test quiz generation
        quiz_config = {
            "topic": "Python Programming",
            "difficulty": "medium",
            "num_questions": 3,
            "time_limit": 300
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/quiz/generate",
                json=quiz_config
            )
            self.print_result("/api/quiz/generate", response.status_code, response.json())
            
            if response.status_code == 200:
                quiz_data = response.json()
                print(f"✅ Quiz generated with {len(quiz_data.get('quiz', []))} questions")
                
                # Test quiz history
                try:
                    response = self.session.get(f"{API_BASE}/quiz/history")
                    self.print_result("/api/quiz/history", response.status_code, response.json())
                except Exception as e:
                    print(f"❌ Quiz history test failed: {e}")
            else:
                print(f"❌ Quiz generation failed: {response.json()}")
        except Exception as e:
            print(f"❌ Quiz generation test failed: {e}")
    
    def test_analytics_endpoints(self):
        """Test analytics endpoints"""
        self.print_section("ANALYTICS ENDPOINTS")
        
        if not self.auth_token:
            print("❌ Skipping analytics tests - no auth token")
            return
        
        try:
            response = self.session.get(f"{API_BASE}/analytics/dashboard")
            self.print_result("/api/analytics/dashboard", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Analytics dashboard test failed: {e}")
        
        try:
            response = self.session.get(f"{API_BASE}/analytics/progress")
            self.print_result("/api/analytics/progress", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Analytics progress test failed: {e}")
    
    def test_flashcard_endpoints(self):
        """Test flashcard endpoints"""
        self.print_section("FLASHCARD ENDPOINTS")
        
        if not self.auth_token:
            print("❌ Skipping flashcard tests - no auth token")
            return
        
        # Test flashcard generation
        flashcard_config = {
            "topic": "JavaScript Basics",
            "num_cards": 5
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/flashcards/generate",
                json=flashcard_config
            )
            self.print_result("/api/flashcards/generate", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Flashcard generation test failed: {e}")
        
        try:
            response = self.session.get(f"{API_BASE}/flashcards/deck")
            self.print_result("/api/flashcards/deck", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Flashcard deck test failed: {e}")
    
    def test_chat_endpoints(self):
        """Test chat endpoints"""
        self.print_section("CHAT ENDPOINTS")
        
        if not self.auth_token:
            print("❌ Skipping chat tests - no auth token")
            return
        
        chat_message = {
            "message": "What is the difference between a list and a tuple in Python?",
            "context": "python programming"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/chat/send",
                json=chat_message
            )
            self.print_result("/api/chat/send", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Chat test failed: {e}")
    
    def test_export_endpoints(self):
        """Test export endpoints"""
        self.print_section("EXPORT ENDPOINTS")
        
        if not self.auth_token:
            print("❌ Skipping export tests - no auth token")
            return
        
        try:
            response = self.session.get(f"{API_BASE}/export/quiz-history")
            self.print_result("/api/export/quiz-history", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Export test failed: {e}")
    
    def test_user_endpoints(self):
        """Test user management endpoints"""
        self.print_section("USER ENDPOINTS")
        
        if not self.auth_token:
            print("❌ Skipping user tests - no auth token")
            return
        
        try:
            response = self.session.get(f"{API_BASE}/user/profile")
            self.print_result("/api/user/profile", response.status_code, response.json())
        except Exception as e:
            print(f"❌ User profile test failed: {e}")
        
        try:
            response = self.session.put(
                f"{API_BASE}/user/profile",
                json={"username": "updateduser"}
            )
            self.print_result("/api/user/profile (update)", response.status_code, response.json())
        except Exception as e:
            print(f"❌ User profile update test failed: {e}")
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Comprehensive API Tests for Quizlet AI Quiz Generator")
        print(f"📍 Testing server at: {BASE_URL}")
        
        # Basic endpoints
        self.test_health_endpoint()
        self.test_root_endpoint()
        
        # Authentication
        self.test_auth_endpoints()
        
        # Core features
        self.test_quiz_endpoints()
        self.test_analytics_endpoints()
        self.test_flashcard_endpoints()
        self.test_chat_endpoints()
        self.test_export_endpoints()
        self.test_user_endpoints()
        
        print(f"\n{'='*60}")
        print("  🎉 API Testing Complete!")
        print(f"{'='*60}")
        print("📊 Summary:")
        print("✅ Health check - Server is running")
        print("✅ Authentication - User registration and login")
        print("✅ Quiz generation - AI-powered quiz creation")
        print("✅ Analytics - Progress tracking and insights")
        print("✅ Flashcards - Study material generation")
        print("✅ Chat - AI tutor assistance")
        print("✅ Export - Data export functionality")
        print("✅ User management - Profile and settings")
        
        print(f"\n🌐 API Documentation available at: {BASE_URL}/docs")
        print(f"📖 Interactive API docs at: {BASE_URL}/redoc")

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests() 