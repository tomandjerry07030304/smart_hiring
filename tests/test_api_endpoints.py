"""
API Endpoint Testing Script
Tests all critical endpoints of the Smart Hiring System
Run this script to verify the system is working correctly
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://my-project-smart-hiring.onrender.com/api"
LOCAL_URL = "http://localhost:5000/api"

# Choose which URL to test
API_URL = BASE_URL  # Change to LOCAL_URL for local testing

# Test results storage
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(name, passed, details=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    test_results["tests"].append({
        "name": name,
        "status": status,
        "details": details
    })
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
    print(f"{status} - {name}")
    if details and not passed:
        print(f"    Details: {details}")

def test_health_check():
    """Test 1: Health Check Endpoint"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        passed = response.status_code == 200 and response.json().get("status") == "healthy"
        log_test("Health Check", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        log_test("Health Check", False, str(e))
        return False

def test_register_candidate():
    """Test 2: User Registration (Candidate)"""
    try:
        data = {
            "email": f"test_candidate_{datetime.now().timestamp()}@test.com",
            "password": "Test@123",
            "full_name": "Test Candidate",
            "role": "candidate"
        }
        response = requests.post(f"{API_URL}/auth/register", json=data, timeout=10)
        passed = response.status_code == 201
        log_test("Register Candidate", passed, f"Status: {response.status_code}")
        if passed:
            return response.json().get("user_id")
        return None
    except Exception as e:
        log_test("Register Candidate", False, str(e))
        return None

def test_register_recruiter():
    """Test 3: User Registration (Recruiter)"""
    try:
        data = {
            "email": f"test_recruiter_{datetime.now().timestamp()}@test.com",
            "password": "Test@123",
            "full_name": "Test Recruiter",
            "role": "company"
        }
        response = requests.post(f"{API_URL}/auth/register", json=data, timeout=10)
        passed = response.status_code == 201
        log_test("Register Recruiter", passed, f"Status: {response.status_code}")
        if passed:
            return response.json().get("user_id")
        return None
    except Exception as e:
        log_test("Register Recruiter", False, str(e))
        return None

def test_login(email, password):
    """Test 4: User Login"""
    try:
        data = {
            "email": email,
            "password": password
        }
        response = requests.post(f"{API_URL}/auth/login", json=data, timeout=10)
        passed = response.status_code == 200 and "access_token" in response.json()
        log_test(f"Login ({email})", passed, f"Status: {response.status_code}")
        if passed:
            return response.json().get("access_token")
        return None
    except Exception as e:
        log_test(f"Login ({email})", False, str(e))
        return None

def test_admin_login():
    """Test 5: Admin Login"""
    return test_login("admin@smarthiring.com", "changeme")

def test_create_job(token):
    """Test 6: Create Job (Recruiter only)"""
    try:
        data = {
            "title": "Senior Python Developer",
            "description": "We are looking for an experienced Python developer with 5+ years of experience.\n\nResponsibilities:\n- Design and implement backend services\n- Write clean, maintainable code\n- Collaborate with team members",
            "company_name": "Test Company Inc.",
            "location": "Remote",
            "job_type": "Full-time",
            "required_skills": ["Python", "Django", "PostgreSQL", "Docker"],
            "experience_required": 5,
            "salary_range": {"min": 80000, "max": 120000}
        }
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{API_URL}/jobs/create", json=data, headers=headers, timeout=10)
        passed = response.status_code == 201
        log_test("Create Job", passed, f"Status: {response.status_code}")
        if passed:
            return response.json().get("job_id")
        return None
    except Exception as e:
        log_test("Create Job", False, str(e))
        return None

def test_list_jobs():
    """Test 7: List All Jobs (Public)"""
    try:
        response = requests.get(f"{API_URL}/jobs/list?status=open", timeout=10)
        passed = response.status_code == 200 and "jobs" in response.json()
        job_count = len(response.json().get("jobs", []))
        log_test("List Jobs", passed, f"Found {job_count} jobs")
        return passed
    except Exception as e:
        log_test("List Jobs", False, str(e))
        return False

def test_get_job_details(job_id):
    """Test 8: Get Job Details"""
    try:
        response = requests.get(f"{API_URL}/jobs/{job_id}", timeout=10)
        passed = response.status_code == 200
        log_test("Get Job Details", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        log_test("Get Job Details", False, str(e))
        return False

def test_apply_to_job(token, job_id):
    """Test 9: Apply to Job (Candidate only)"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{API_URL}/candidates/apply/{job_id}", json={}, headers=headers, timeout=10)
        passed = response.status_code in [200, 201]
        log_test("Apply to Job", passed, f"Status: {response.status_code}")
        if passed:
            return response.json().get("application_id")
        return None
    except Exception as e:
        log_test("Apply to Job", False, str(e))
        return None

def test_get_candidate_applications(token):
    """Test 10: Get Candidate's Applications"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/candidates/applications", headers=headers, timeout=10)
        passed = response.status_code == 200 and "applications" in response.json()
        app_count = len(response.json().get("applications", []))
        log_test("Get Candidate Applications", passed, f"Found {app_count} applications")
        return passed
    except Exception as e:
        log_test("Get Candidate Applications", False, str(e))
        return False

def test_get_company_jobs(token):
    """Test 11: Get Company's Jobs"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/jobs/company", headers=headers, timeout=10)
        passed = response.status_code == 200 and "jobs" in response.json()
        job_count = len(response.json().get("jobs", []))
        log_test("Get Company Jobs", passed, f"Found {job_count} jobs")
        return passed
    except Exception as e:
        log_test("Get Company Jobs", False, str(e))
        return False

def test_get_company_stats(token):
    """Test 12: Get Company Dashboard Stats"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/jobs/company/stats", headers=headers, timeout=10)
        passed = response.status_code == 200
        if passed:
            stats = response.json()
            log_test("Get Company Stats", passed, 
                    f"Active Jobs: {stats.get('active_jobs', 0)}, Applications: {stats.get('total_applications', 0)}")
        else:
            log_test("Get Company Stats", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        log_test("Get Company Stats", False, str(e))
        return False

def test_get_company_applications(token):
    """Test 13: Get Company's Applications"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_URL}/jobs/company/applications", headers=headers, timeout=10)
        passed = response.status_code == 200 and "applications" in response.json()
        app_count = len(response.json().get("applications", []))
        log_test("Get Company Applications", passed, f"Found {app_count} applications")
        return passed
    except Exception as e:
        log_test("Get Company Applications", False, str(e))
        return False

def test_unauthorized_access():
    """Test 14: Unauthorized Access (No Token)"""
    try:
        response = requests.get(f"{API_URL}/jobs/company", timeout=10)
        passed = response.status_code == 401  # Should be unauthorized
        log_test("Unauthorized Access Protection", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        log_test("Unauthorized Access Protection", False, str(e))
        return False

def test_rbac_candidate_cannot_create_job(candidate_token):
    """Test 15: RBAC - Candidate Cannot Create Job"""
    try:
        data = {
            "title": "Test Job",
            "description": "This should fail"
        }
        headers = {"Authorization": f"Bearer {candidate_token}"}
        response = requests.post(f"{API_URL}/jobs/create", json=data, headers=headers, timeout=10)
        passed = response.status_code == 403  # Should be forbidden
        log_test("RBAC: Candidate Cannot Create Job", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        log_test("RBAC: Candidate Cannot Create Job", False, str(e))
        return False

def run_all_tests():
    """Run all API tests"""
    print("\n" + "="*60)
    print("🧪 SMART HIRING SYSTEM - API ENDPOINT TESTS")
    print("="*60)
    print(f"Testing URL: {API_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

    # Test 1: Health Check
    print("1️⃣ SYSTEM HEALTH")
    print("-" * 40)
    if not test_health_check():
        print("\n⚠️  System is not healthy. Aborting tests.\n")
        return
    print()

    # Test 2-3: User Registration
    print("2️⃣ USER REGISTRATION")
    print("-" * 40)
    candidate_email = f"test_candidate_{datetime.now().timestamp()}@test.com"
    recruiter_email = f"test_recruiter_{datetime.now().timestamp()}@test.com"
    
    candidate_id = test_register_candidate()
    recruiter_id = test_register_recruiter()
    print()

    # Test 4-5: Authentication
    print("3️⃣ AUTHENTICATION")
    print("-" * 40)
    admin_token = test_admin_login()
    candidate_token = test_login(candidate_email, "Test@123") if candidate_id else None
    recruiter_token = test_login(recruiter_email, "Test@123") if recruiter_id else None
    print()

    # Test 6-8: Job Management
    print("4️⃣ JOB MANAGEMENT")
    print("-" * 40)
    job_id = None
    if recruiter_token:
        job_id = test_create_job(recruiter_token)
    test_list_jobs()
    if job_id:
        test_get_job_details(job_id)
    print()

    # Test 9-10: Candidate Operations
    print("5️⃣ CANDIDATE OPERATIONS")
    print("-" * 40)
    if candidate_token and job_id:
        test_apply_to_job(candidate_token, job_id)
        test_get_candidate_applications(candidate_token)
    print()

    # Test 11-13: Recruiter Operations
    print("6️⃣ RECRUITER OPERATIONS")
    print("-" * 40)
    if recruiter_token:
        test_get_company_jobs(recruiter_token)
        test_get_company_stats(recruiter_token)
        test_get_company_applications(recruiter_token)
    print()

    # Test 14-15: Security & RBAC
    print("7️⃣ SECURITY & ACCESS CONTROL")
    print("-" * 40)
    test_unauthorized_access()
    if candidate_token:
        test_rbac_candidate_cannot_create_job(candidate_token)
    print()

    # Results Summary
    print("="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    print(f"✅ Passed: {test_results['passed']}")
    print(f"❌ Failed: {test_results['failed']}")
    total = test_results['passed'] + test_results['failed']
    success_rate = (test_results['passed'] / total * 100) if total > 0 else 0
    print(f"📈 Success Rate: {success_rate:.1f}%")
    print("="*60)

    if test_results['failed'] > 0:
        print("\n❌ FAILED TESTS:")
        for test in test_results['tests']:
            if "FAIL" in test['status']:
                print(f"  - {test['name']}: {test['details']}")
    
    print("\n✅ TEST COMPLETE\n")

    # Save results to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"test_results_{timestamp}.json"
    with open(report_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "api_url": API_URL,
            "summary": {
                "total": total,
                "passed": test_results['passed'],
                "failed": test_results['failed'],
                "success_rate": f"{success_rate:.1f}%"
            },
            "tests": test_results['tests']
        }, f, indent=2)
    
    print(f"📄 Detailed results saved to: {report_file}\n")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user\n")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}\n")
