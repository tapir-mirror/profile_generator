#!/usr/bin/env python3

import redis
import json
import time
import pandas as pd
import random
from threading import Thread

# Mock the process_queue function to use mock API calls
def mock_process_queue(queue_id, redis_client, port):
    """
    Process jobs from a specific Redis queue with mock API responses
    """
    from prompt import buildprompt, save_conversation, subprompts
    
    queue_name = f"profiles:queue:{queue_id}"
    conversation_index = 1
    
    print(f"Starting MOCK queue processor for {queue_name} -> localhost:{port}")
    
    while True:
        try:
            # Pop job from queue (blocking with 1 second timeout)
            job_data = redis_client.brpop(queue_name, timeout=1)
            
            if job_data is None:
                # No job available, continue polling
                continue
                
            # Parse the job
            queue_name_from_redis, message = job_data
            job_payload = json.loads(message.decode('utf-8'))
            
            job_id = job_payload.get('job_id')
            profile_data = job_payload.get('profile_data')
            
            print(f"Processing job {job_id} from {queue_name} on port {port}")
            
            # Select a random subprompt
            selected_subprompt = random.choice(subprompts)
            prompt = buildprompt(selected_subprompt, json.dumps(profile_data, indent=2))
            
            # Create mock response instead of calling real API
            mock_response = {
                "personality_traits": ["professional", "analytical", "collaborative", "adaptable", "results-oriented"],
                "communication_style": random.choice(["Strategic", "Analytical", "Collaborative", "Direct", "Inspiring"]),
                "vibe_category": random.choice(["Leader", "Expert", "Innovator", "Collaborator", "Strategist"]),
                "confidence_score": random.randint(75, 95),
                "key_strength": f"Strong professional capabilities in {profile_data.get('headline', 'their field')}",
                "growth_area": "Could develop stronger cross-functional collaboration skills",
                "radar_data": [
                    {"trait": "Leadership", "score": random.randint(70, 95)},
                    {"trait": "Innovation", "score": random.randint(70, 95)},
                    {"trait": "Empathy", "score": random.randint(70, 95)},
                    {"trait": "Analytics", "score": random.randint(70, 95)},
                    {"trait": "Communication", "score": random.randint(70, 95)}
                ]
            }
            
            response = json.dumps(mock_response, indent=2)
            
            if response:
                # Create conversation data in the required format
                conversation_data = {
                    "messages": [
                        {
                            "role": "user", 
                            "content": prompt
                        },
                        {
                            "role": "assistant", 
                            "content": response
                        }
                    ]
                }
                
                # Save the conversation
                save_conversation(port, conversation_index, conversation_data)
                conversation_index += 1
                
                print(f"Successfully processed job {job_id}")
                return  # Exit after processing one job for testing
            else:
                print(f"Failed to get response for job {job_id}")
                
        except redis.exceptions.RedisError as e:
            print(f"Redis error in queue processor for port {port}: {e}")
            time.sleep(5)  # Wait before retrying
        except json.JSONDecodeError as e:
            print(f"JSON decode error in queue processor for port {port}: {e}")
        except Exception as e:
            print(f"Unexpected error in queue processor for port {port}: {e}")
            time.sleep(1)  # Wait before continuing

def create_small_test_dataset():
    """Create a small test dataset similar to the LinkedIn format"""
    test_data = [
        {
            "firstName": "John",
            "lastName": "Doe",
            "headline": "Senior Software Engineer at Tech Corp",
            "summary": "Experienced software engineer with 8 years in backend development",
            "position": [{"title": "Senior Software Engineer", "companyName": "Tech Corp"}]
        },
        {
            "firstName": "Jane",
            "lastName": "Smith", 
            "headline": "Product Manager at StartupCorp",
            "summary": "Product manager with 5 years experience in SaaS products",
            "position": [{"title": "Product Manager", "companyName": "StartupCorp"}]
        },
        {
            "firstName": "Mike",
            "lastName": "Johnson",
            "headline": "Data Scientist at AI Labs",
            "summary": "Machine learning expert specializing in NLP and computer vision",
            "position": [{"title": "Data Scientist", "companyName": "AI Labs"}]
        }
    ]
    
    return pd.DataFrame(test_data)

def dispatch_test_profiles(redis_client, profiles, num_queues=2):
    """Dispatch test profiles to Redis queues"""
    queue_base_name = "profiles:queue"
    
    print(f"Dispatching {len(profiles)} profiles to {num_queues} queues...")
    
    for i, (index, profile) in enumerate(profiles.iterrows()):
        profile_dict = profile.to_dict()
        queue_index = i % num_queues
        target_queue = f"{queue_base_name}:{queue_index}"
        
        job_payload = {
            "job_id": f"test-job-{i+1:03d}",
            "profile_data": profile_dict
        }
        
        message = json.dumps(job_payload)
        redis_client.lpush(target_queue, message)
        print(f"  ✓ Dispatched {profile['firstName']} {profile['lastName']} to {target_queue}")

def main():
    """Test the complete Redis workflow"""
    print("🧪 Testing complete Redis workflow with small dataset\n")
    
    try:
        # Connect to Redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✓ Connected to Redis")
        
        # Clear any existing test data
        for i in range(4):
            queue_name = f"profiles:queue:{i}"
            r.delete(queue_name)
        print("✓ Cleared existing queues")
        
        # Create and dispatch test profiles
        test_profiles = create_small_test_dataset()
        dispatch_test_profiles(r, test_profiles, num_queues=2)
        
        print("\n🚀 Starting queue processors...")
        print("Note: This will use mock API responses since model servers aren't running")
        
        # Start queue processors (with timeout for testing)
        threads = []
        for i in range(2):
            port = 8000 + i
            thread = Thread(
                target=mock_process_queue,
                args=(i, r, port),
                daemon=True
            )
            threads.append(thread)
            thread.start()
            print(f"✓ Started processor for queue:{i} -> port:{port}")
        
        # Let it run for a few seconds
        print("\n⏳ Processing for 10 seconds...")
        time.sleep(10)
        
        print("\n📊 Checking results...")
        
        # Check if queues are empty
        total_remaining = 0
        for i in range(2):
            queue_name = f"profiles:queue:{i}"
            remaining = r.llen(queue_name)
            total_remaining += remaining
            print(f"  Queue {i}: {remaining} jobs remaining")
        
        if total_remaining == 0:
            print("✅ All jobs processed successfully!")
        else:
            print(f"⚠️  {total_remaining} jobs still in queues")
        
        # Check output files
        import os
        output_dir = "../output"
        if os.path.exists(output_dir):
            files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
            print(f"✅ Found {len(files)} conversation files in output directory")
            
            # Show some file details
            for filename in sorted(files)[-3:]:  # Show last 3 files
                filepath = os.path.join(output_dir, filename)
                size = os.path.getsize(filepath)
                print(f"  📄 {filename} ({size} bytes)")
        
        print("\n🎉 Redis workflow test completed!")
        print("\n📝 To run with real model APIs:")
        print("   1. Start model servers on ports 8000-8007")
        print("   2. Replace mock_model_api with real API calls")
        print("   3. Run: python3 prompt.py")
        
    except redis.exceptions.ConnectionError:
        print("❌ Could not connect to Redis. Make sure Redis is running.")
        print("   Try: redis-server &")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()
