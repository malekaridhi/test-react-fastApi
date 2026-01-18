import requests
import json
import os
from dotenv import load_dotenv          
load_dotenv()  # take environment variables from .env file
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/api")
HEADERS = {"Content-Type": "application/json"}

def print_response(method, endpoint, response):
    print(f"\n{'='*60}")
    print(f"{method} {endpoint}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
    print('='*60)

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL.replace('/api', '')}/health")
    print_response("GET", "/health", response)

def test_generate_ideas():
    """Test idea generation"""
    data = {
        "icp_profile": "Small business owners",
        "pain_points": ["no time", "expensive marketing", "no systems"],
        "content_topics": ["automation", "social media", "email marketing"],
        "offer_type": "consulting",
        "brand_voice": "friendly",
        "conversion_goal": "booked calls"
    }
    
    response = requests.post(
        f"{BASE_URL}/lead-magnets/generate-ideas",
        json=data,
        headers=HEADERS
    )
    print_response("POST", "/lead-magnets/generate-ideas", response)
    return response.json() if response.status_code == 200 else None

def test_create_lead_magnet():
    """Test creating a lead magnet"""
    data = {
        "title": "Marketing Automation Checklist",
        "type": "checklist",
        "value_promise": "Automate 10 hours of work per week",
        "conversion_score": 9
    }
    
    response = requests.post(
        f"{BASE_URL}/lead-magnets/",
        json=data,
        headers=HEADERS
    )
    print_response("POST", "/lead-magnets/", response)
    return response.json() if response.status_code == 201 else None

def test_get_lead_magnets():
    """Test getting all lead magnets"""
    response = requests.get(f"{BASE_URL}/lead-magnets/")
    print_response("GET", "/lead-magnets/", response)
    return response.json() if response.status_code == 200 else None

def test_get_single_lead_magnet(lead_magnet_id: int):
    """Test getting a single lead magnet"""
    response = requests.get(f"{BASE_URL}/lead-magnets/{lead_magnet_id}")
    print_response("GET", f"/lead-magnets/{lead_magnet_id}", response)
    return response.json() if response.status_code == 200 else None

def test_update_lead_magnet(lead_magnet_id: int):
    """Test updating a lead magnet"""
    data = {
        "title": "Updated Marketing Checklist",
        "type": "checklist",
        "value_promise": "Now even better!",
        "conversion_score": 10
    }
    
    response = requests.put(
        f"{BASE_URL}/lead-magnets/{lead_magnet_id}",
        json=data,
        headers=HEADERS
    )
    print_response("PUT", f"/lead-magnets/{lead_magnet_id}", response)
    return response.json() if response.status_code == 200 else None

def test_generate_content(lead_magnet_id: int):
    """Test generating content for a lead magnet"""
    params = {"pain_points": ["no time", "no clients"]}
    
    response = requests.post(
        f"{BASE_URL}/lead-magnets/{lead_magnet_id}/generate-content",
        params=params
    )
    print_response("POST", f"/lead-magnets/{lead_magnet_id}/generate-content", response)
    return response.json() if response.status_code == 200 else None

# def test_delete_lead_magnet(lead_magnet_id: int):
#     """Test deleting a lead magnet"""
#     response = requests.delete(f"{BASE_URL}/lead-magnets/{lead_magnet_id}")
#     print_response("DELETE", f"/lead-magnets/{lead_magnet_id}", response)
#     return response.status_code == 204

def run_all_tests():
    """Run all tests in sequence"""
    print(" Starting API Tests...")
    
    # 1. Test health
    test_health()
    
    # 2. Test idea generation
    ideas = test_generate_ideas()
    
    # 3. Test create lead magnet
    created_magnet = test_create_lead_magnet()
    
    if created_magnet:
        lead_magnet_id = created_magnet.get('id')
        
        # 4. Test get all magnets
        test_get_lead_magnets()
        
        # 5. Test get single magnet
        test_get_single_lead_magnet(lead_magnet_id)
        
        # 6. Test update magnet
        test_update_lead_magnet(lead_magnet_id)
        
        # 7. Test generate content (if LLM is working)
        # test_generate_content(lead_magnet_id)
     
        
        # 9. Verify deletion
        test_get_single_lead_magnet(lead_magnet_id)  # Should return 404
        
    
    print("\n All tests completed!")

if __name__ == "__main__":
    run_all_tests()