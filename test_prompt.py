import redis
import json
import time
import os
from prompt import buildprompt, save_conversation, subprompts
import random

def mock_model_api(prompt, port):
    """
    Mock API call that returns a sample response
    """
    print(f"Mock API call to port {port}")
    
    # Simulate API delay
    time.sleep(0.5)
    
    # Return a mock JSON response
    mock_response = {
        "personality_traits": ["analytical", "strategic", "innovative", "collaborative", "results-driven"],
        "communication_style": "Strategic",
        "vibe_category": "Leader",
        "confidence_score": 87,
        "key_strength": "Demonstrates strong leadership and strategic thinking capabilities",
        "growth_area": "Could benefit from developing more technical expertise",
        "radar_data": [
            {"trait": "Leadership", "score": 90},
            {"trait": "Innovation", "score": 85},
            {"trait": "Empathy", "score": 78},
            {"trait": "Analytics", "score": 82},
            {"trait": "Communication", "score": 88}
        ]
    }
    
    return json.dumps(mock_response, indent=2)

def create_test_profile():
    """
    Create a test LinkedIn profile
    """
    return {
        "urn": "test-profile-001",
        "firstName": "John",
        "lastName": "Doe",
        "headline": "Senior Software Engineer at Tech Corp",
        "summary": "Experienced software engineer with 8 years in backend development, specializing in Python and distributed systems.",
        "position": [
            {
                "title": "Senior Software Engineer",
                "companyName": "Tech Corp",
                "description": "Leading backend development for scalable web applications"
            }
        ]
    }

def test_with_redis():
    """
    Test the complete flow with Redis
    """
    print("=== Testing with Redis ===")
    
    try:
        # Connect to Redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✓ Connected to Redis")
        
        # Clear any existing test data
        test_queue = "profiles:queue:0"
        r.delete(test_queue)
        
        # Create test profile and job
        test_profile = create_test_profile()
        job_payload = {
            "job_id": "test-job-001",
            "profile_data": test_profile
        }
        
        # Add job to queue
        r.lpush(test_queue, json.dumps(job_payload))
        print("✓ Added test profile to Redis queue")
        
        # Process the job
        job_data = r.brpop(test_queue, timeout=5)
        if job_data:
            queue_name, message = job_data
            job_payload = json.loads(message.decode('utf-8'))
            
            print(f"✓ Retrieved job: {job_payload['job_id']}")
            
            # Generate prompt
            selected_subprompt = random.choice(subprompts)
            prompt = buildprompt(selected_subprompt, json.dumps(job_payload['profile_data'], indent=2))
            print("✓ Generated prompt")
            
            # Mock API call
            response = mock_model_api(prompt, 8000)
            print("✓ Got mock API response")
            
            # Save conversation
            conversation_data = {
                "messages": [
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": response}
                ]
            }
            
            save_conversation(8000, 1, conversation_data)
            print("✓ Saved conversation")
            
        else:
            print("✗ No job found in queue")
            
    except redis.exceptions.ConnectionError:
        print("✗ Could not connect to Redis")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
        
    return True

def test_without_redis():
    """
    Test core functionality without Redis
    """
    print("\n=== Testing without Redis ===")
    
    try:
        # Create test profile
        test_profile = create_test_profile()
        print("✓ Created test profile")
        
        # Generate prompt
        selected_subprompt = random.choice(subprompts)
        prompt = buildprompt(selected_subprompt, json.dumps(test_profile, indent=2))
        print("✓ Generated prompt")
        print(f"  Prompt length: {len(prompt)} characters")
        
        # Mock API call
        response = mock_model_api(prompt, 8000)
        print("✓ Got mock API response")
        
        # Save conversation
        conversation_data = {
            "messages": [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": response}
            ]
        }
        
        save_conversation(8000, 2, conversation_data)
        print("✓ Saved conversation")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def check_output():
    """
    Check if output files were created
    """
    print("\n=== Checking Output ===")
    
    output_dir = "../output"
    if os.path.exists(output_dir):
        files = os.listdir(output_dir)
        print(f"✓ Output directory exists with {len(files)} files:")
        for file in files:
            filepath = os.path.join(output_dir, file)
            size = os.path.getsize(filepath)
            print(f"  - {file} ({size} bytes)")
            
            # Show content of first file
            if file.endswith('.json'):
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    print(f"    Content preview: {len(data['messages'])} messages")
                except Exception as e:
                    print(f"    Error reading file: {e}")
    else:
        print("✗ Output directory does not exist")

if __name__ == '__main__':
    print("Starting prompt.py test...")
    
    # Test without Redis first
    success1 = test_without_redis()
    
    # Test with Redis if available
    success2 = test_with_redis()
    
    # Check output
    check_output()
    
    print(f"\n=== Test Results ===")
    print(f"Core functionality: {'✓ PASS' if success1 else '✗ FAIL'}")
    print(f"Redis integration: {'✓ PASS' if success2 else '✗ FAIL'}")
    
    if success1:
        print("\n✓ Basic functionality is working!")
        print("✓ You can now run the full prompt.py with real model APIs")
    else:
        print("\n✗ Issues found in basic functionality")
