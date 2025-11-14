"""
Quick test script to verify API is working
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Make sure the server is running (python backend/app.py)")
        return False

def test_register():
    """Test user registration"""
    print("\n🔍 Testing user registration...")
    data = {
        "email": "testuser@example.com",
        "password": "test123456",
        "full_name": "Test User",
        "role": "candidate"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        if response.status_code == 201:
            print("✅ User registration successful")
            result = response.json()
            print(f"   User ID: {result['user_id']}")
            print(f"   Token: {result['access_token'][:30]}...")
            return result['access_token']
        elif response.status_code == 409:
            print("⚠️  User already exists, trying login...")
            return test_login(data['email'], data['password'])
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_login(email, password):
    """Test user login"""
    print("\n🔍 Testing user login...")
    data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        if response.status_code == 200:
            print("✅ Login successful")
            result = response.json()
            print(f"   Token: {result['access_token'][:30]}...")
            return result['access_token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_protected_endpoint(token):
    """Test protected endpoint with token"""
    print("\n🔍 Testing protected endpoint...")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
        if response.status_code == 200:
            print("✅ Protected endpoint access successful")
            user = response.json()
            print(f"   Email: {user['email']}")
            print(f"   Name: {user['full_name']}")
            print(f"   Role: {user['role']}")
            return True
        else:
            print(f"❌ Protected endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_job_listing():
    """Test job listing endpoint"""
    print("\n🔍 Testing job listing...")
    try:
        response = requests.get(f"{BASE_URL}/jobs/list")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Job listing successful")
            print(f"   Total jobs: {result['total']}")
            print(f"   Retrieved: {result['count']}")
            if result['jobs']:
                print(f"   First job: {result['jobs'][0]['title']}")
            return True
        else:
            print(f"❌ Job listing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Smart Hiring System - API Test Suite")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Server is not running. Please start it first:")
        print("   python backend/app.py")
        return
    
    # Test 2: Register user
    token = test_register()
    
    if token:
        # Test 3: Protected endpoint
        test_protected_endpoint(token)
    
    # Test 4: Public endpoint
    test_job_listing()
    
    print("\n" + "=" * 60)
    print("✅ API tests completed!")
    print("=" * 60)
    print("\n📚 For more API details, see API_DOCUMENTATION.md")

if __name__ == "__main__":
    main()
