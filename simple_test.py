#!/usr/bin/env python3

import json
import os
import sys

# Add current directory to path to import prompt module
sys.path.append('.')

def test_basic_functionality():
    """Test the basic prompt building and file saving functionality"""
    print("=== Testing Basic Functionality ===")
    
    try:
        # Import functions from prompt.py
        from prompt import buildprompt, save_conversation, subprompts
        print("✓ Successfully imported prompt module")
        
        # Test profile data
        test_profile = {
            "firstName": "Jane",
            "lastName": "Smith", 
            "headline": "Data Scientist at AI Corp",
            "summary": "Passionate data scientist with expertise in machine learning and analytics",
            "position": [
                {
                    "title": "Senior Data Scientist",
                    "companyName": "AI Corp",
                    "description": "Leading ML model development"
                }
            ]
        }
        print("✓ Created test profile")
        
        # Test prompt building
        test_subprompt = subprompts[0]  # Use first subprompt
        prompt = buildprompt(test_subprompt, json.dumps(test_profile, indent=2))
        print("✓ Built prompt successfully")
        print(f"  Prompt length: {len(prompt)} characters")
        
        # Test conversation saving
        mock_response = {
            "personality_traits": ["analytical", "detail-oriented", "innovative", "collaborative", "driven"],
            "communication_style": "Analytical",
            "vibe_category": "Expert",
            "confidence_score": 85,
            "key_strength": "Strong analytical and technical problem-solving abilities",
            "growth_area": "Could enhance leadership and team management skills",
            "radar_data": [
                {"trait": "Leadership", "score": 75},
                {"trait": "Innovation", "score": 88},
                {"trait": "Empathy", "score": 80},
                {"trait": "Analytics", "score": 95},
                {"trait": "Communication", "score": 78}
            ]
        }
        
        conversation_data = {
            "messages": [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": json.dumps(mock_response, indent=2)}
            ]
        }
        
        # Save conversation
        save_conversation(8000, 1, conversation_data)
        print("✓ Saved conversation successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_output_files():
    """Check if output files were created correctly"""
    print("\n=== Checking Output Files ===")
    
    output_dir = "../output"
    
    if not os.path.exists(output_dir):
        print("✗ Output directory does not exist")
        return False
        
    files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
    
    if not files:
        print("✗ No JSON files found in output directory")
        return False
        
    print(f"✓ Found {len(files)} JSON files:")
    
    for filename in files:
        filepath = os.path.join(output_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check file structure
            if 'messages' in data and len(data['messages']) == 2:
                user_msg = data['messages'][0]
                assistant_msg = data['messages'][1]
                
                if (user_msg.get('role') == 'user' and 
                    assistant_msg.get('role') == 'assistant' and
                    user_msg.get('content') and 
                    assistant_msg.get('content')):
                    
                    print(f"  ✓ {filename} - Valid structure")
                    print(f"    User message: {len(user_msg['content'])} chars")
                    print(f"    Assistant message: {len(assistant_msg['content'])} chars")
                else:
                    print(f"  ✗ {filename} - Invalid message structure")
            else:
                print(f"  ✗ {filename} - Missing or invalid messages array")
                
        except Exception as e:
            print(f"  ✗ {filename} - Error reading file: {e}")
    
    return True

def simulate_redis_workflow():
    """Simulate the Redis workflow without actually using Redis"""
    print("\n=== Simulating Redis Workflow ===")
    
    try:
        from prompt import buildprompt, save_conversation, subprompts
        import random
        
        # Simulate multiple profiles
        test_profiles = [
            {
                "firstName": "Alice", 
                "lastName": "Johnson",
                "headline": "Product Manager at StartupCorp",
                "summary": "Product manager with 5 years experience in SaaS products"
            },
            {
                "firstName": "Bob",
                "lastName": "Williams", 
                "headline": "Software Engineer at TechGiant",
                "summary": "Full-stack developer specializing in React and Node.js"
            },
            {
                "firstName": "Carol",
                "lastName": "Davis",
                "headline": "Marketing Director at Growth Inc",
                "summary": "Digital marketing expert with focus on B2B lead generation"
            }
        ]
        
        print(f"✓ Created {len(test_profiles)} test profiles")
        
        # Process each profile (simulating queue processing)
        for i, profile in enumerate(test_profiles):
            # Simulate job processing
            job_id = f"test-job-{i+1:03d}"
            port = 8000 + (i % 4)  # Distribute across ports 8000-8003
            
            print(f"  Processing job {job_id} on port {port}...")
            
            # Generate prompt with random subprompt
            selected_subprompt = random.choice(subprompts)
            prompt = buildprompt(selected_subprompt, json.dumps(profile, indent=2))
            
            # Create mock response
            mock_response = {
                "personality_traits": ["professional", "focused", "collaborative", "adaptable", "results-oriented"],
                "communication_style": "Professional",
                "vibe_category": "Collaborator",
                "confidence_score": 80 + (i * 5),
                "key_strength": f"Strong {['analytical', 'creative', 'leadership'][i % 3]} capabilities",
                "growth_area": "Could develop stronger cross-functional collaboration",
                "radar_data": [
                    {"trait": "Leadership", "score": 70 + (i * 3)},
                    {"trait": "Innovation", "score": 75 + (i * 2)},
                    {"trait": "Empathy", "score": 80 + (i * 1)},
                    {"trait": "Analytics", "score": 85 - (i * 1)},
                    {"trait": "Communication", "score": 78 + (i * 2)}
                ]
            }
            
            # Save conversation
            conversation_data = {
                "messages": [
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": json.dumps(mock_response, indent=2)}
                ]
            }
            
            save_conversation(port, i + 2, conversation_data)  # Start from index 2
            print(f"    ✓ Saved conversation for {profile['firstName']} {profile['lastName']}")
        
        print("✓ Completed simulated workflow")
        return True
        
    except Exception as e:
        print(f"✗ Error in workflow simulation: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing prompt.py implementation\n")
    
    # Test 1: Basic functionality
    test1_success = test_basic_functionality()
    
    # Test 2: Simulated workflow
    test2_success = simulate_redis_workflow()
    
    # Test 3: Check output files
    test3_success = check_output_files()
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    print(f"Basic functionality:     {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"Simulated workflow:      {'✅ PASS' if test2_success else '❌ FAIL'}")
    print(f"Output file validation:  {'✅ PASS' if test3_success else '❌ FAIL'}")
    
    if all([test1_success, test2_success, test3_success]):
        print("\n🎉 All tests passed! The prompt.py implementation is working correctly.")
        print("\n📝 Next steps:")
        print("   1. Start your model servers on ports 8000-8007")
        print("   2. Run dispatcher.py to populate Redis queues")
        print("   3. Run prompt.py to process the queues")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")

if __name__ == '__main__':
    main()
