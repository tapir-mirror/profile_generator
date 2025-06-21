import redis
import json
import requests
import os
import time
import random
from threading import Thread
import argparse

subprompts = ["You are a professional personality analyst. Analyze this LinkedIn profile and provide insights about how this person comes across professionally.",
              "You are a seasoned executive coach. Review the provided LinkedIn profile and offer your analysis of this individual's professional persona.",
              "Act as a headhunter sourcing top talent. Scrutinize this LinkedIn profile and provide a summary of the person's professional character.",
              "Imagine you are a corporate psychologist. From the LinkedIn data below, deconstruct and report on this person's professional disposition.",
              "You are a career strategist advising a client. Examine this LinkedIn profile and give me your take on how this professional is perceived.",
              "As a human resources director, evaluate this potential candidate. Analyze their LinkedIn profile to understand their professional style and presence.",
              "You are an AI-powered professional branding consultant. Process this LinkedIn profile and generate insights into the user's professional image.",
              "Pretend you are a management consultant building a team. Assess the following LinkedIn profile for its professional attributes.",
              "You are a specialist in organizational behavior. Analyze the professional personality conveyed in this LinkedIn profile.",
              "Assume the role of a personal branding expert. Based on this LinkedIn profile, what is your professional assessment of this individual?",
              "You are a venture capitalist evaluating a founder's profile. Analyze the professional demeanor of this person based on their LinkedIn presence.",
              "Act as a senior mentor reviewing a mentee's online presence. Look at this LinkedIn profile and provide feedback on their professional projection.",
              "You are a communications expert analyzing professional messaging. From this LinkedIn profile, detail how this person communicates their professional identity.",
              "Imagine you are a leadership development consultant. Evaluate the leadership potential and professional style evident in this LinkedIn profile.",
              "You are a data analyst specializing in professional networks. Interpret the data in this LinkedIn profile to describe the user's professional personality.",
              "As a talent acquisition specialist, give me the rundown. What does this LinkedIn profile tell you about this person's professional character?",
              "You are a team dynamics facilitator. Analyze this individual's professional persona from their LinkedIn profile to see how they might fit into a team.",
              "Pretend you're a biographer researching a subject's professional life. From their LinkedIn profile, what initial insights can you gather about their professional self?",
              "You are a market intelligence analyst looking at key industry players. Provide a professional personality assessment based on this person's LinkedIn profile.",
              "Assume the persona of a digital identity advisor. How does this person come across professionally, based on an analysis of their LinkedIn profile?",
              "You are a recruitment AI. Process the following LinkedIn profile and output your analysis of the candidate's professional personality."]

def buildprompt(subprompt, profile):
    prompt = f'''{subprompt}

Based on the profile data below, analyze their professional personality and return ONLY a valid JSON response with this exact structure:

{{
  "personality_traits": ["trait1", "trait2", "trait3", "trait4", "trait5"],
  "communication_style": "Formal|Casual|Inspiring|Analytical|Collaborative|Strategic|Visionary|Methodical|Approachable|Direct|Results-Driven|Detail-Oriented|Creative|Supportive|Diplomatic|Energetic|Pragmatic|Authoritative|Technical|Nurturing",
  "vibe_category": "Leader|Innovator|Collaborator|Expert|Strategist|Mentor|Builder|Connector|Problem-Solver|Communicator|Organizer|Visionary|Executor|Analyst|Mediator|Pioneer|Motivator|Guardian|Architect|Advocate",
  "confidence_score": 93,
  "key_strength": "one sentence describing their main professional strength",
  "growth_area": "one sentence describing an area for potential growth",
  "radar_data": [
    {{"trait": "Leadership", "score": 83}},
    {{"trait": "Innovation", "score": 76}},
    {{"trait": "Empathy", "score": 89}},
    {{"trait": "Analytics", "score": 74}},
    {{"trait": "Communication", "score": 82}}
  ]
}}
You should use data from the profile below to inform your analysis.
Profile Data:
{profile}
'''
    return prompt

def call_model_api(prompt, port):
    """
    Make API call to vLLM model running on localhost at specified port
    Uses the /v1/completions endpoint as specified in models.md
    """
    url = f"http://localhost:{port}/v1/completions"
    
    payload = {
        "model": "default",
        "prompt": prompt,
        "temperature": 0.7,
        "max_tokens": 2000,
        "stop": ["Human:", "Assistant:", "\n\n---"]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['text'].strip()
        else:
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error calling model API on port {port}: {e}")
        return None

def save_conversation(port, index, conversation_data, output_dir="../output"):
    """
    Save conversation in the specified format to output folder
    """
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"{port}_{index}.json"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, ensure_ascii=False, indent=2)
        print(f"Saved conversation to {filepath}")
    except Exception as e:
        print(f"Error saving conversation to {filepath}: {e}")

def process_queue(queue_id, redis_client, port, output_dir="../output", queue_prefix="profiles"):
    """
    Process jobs from a specific Redis queue for a specific model port
    """
    queue_name = f"{queue_prefix}:queue:{queue_id}"
    conversation_index = 1
    
    print(f"Starting queue processor for {queue_name} -> localhost:{port}")
    
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
            
            # Call the model API
            response = call_model_api(prompt, port)
            
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
                save_conversation(port, conversation_index, conversation_data, output_dir)
                conversation_index += 1
                
                print(f"Successfully processed job {job_id}")
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

def main():
    """
    Main function to start queue processors for different model ports
    """
    parser = argparse.ArgumentParser(description="Process LinkedIn profiles from Redis queues")
    parser.add_argument("--redis-host", default="localhost", help="Redis host")
    parser.add_argument("--redis-port", default=6379, type=int, help="Redis port")
    parser.add_argument("--redis-db", default=0, type=int, help="Redis database number")
    parser.add_argument("--start-port", default=8000, type=int, help="Starting port for model APIs")
    parser.add_argument("--num-queues", default=4, type=int, help="Number of queues/ports to process")
    parser.add_argument("--queue-offset", default=0, type=int, help="Offset for queue numbers (allows multiple instances)")
    parser.add_argument("--queue-prefix", default="profiles", help="Prefix for queue names")
    parser.add_argument("--output-dir", default="../output", help="Output directory for conversation files")
    
    args = parser.parse_args()
    
    # Connect to Redis
    try:
        redis_client = redis.Redis(host=args.redis_host, port=args.redis_port, db=args.redis_db)
        redis_client.ping()
        print(f"Connected to Redis at {args.redis_host}:{args.redis_port} (db: {args.redis_db})")
    except redis.exceptions.ConnectionError as e:
        print(f"Could not connect to Redis: {e}")
        return
    
    # Create threads for each queue/port combination
    threads = []
    
    for i in range(args.num_queues):
        queue_id = i + args.queue_offset
        port = args.start_port + i
        
        # Ensure port is within the specified range (8000-8007)
        if port > 8007:
            print(f"Warning: Port {port} exceeds maximum allowed port 8007. Skipping.")
            continue
        
        thread = Thread(
            target=process_queue,
            args=(queue_id, redis_client, port, args.output_dir, args.queue_prefix),
            daemon=True
        )
        threads.append(thread)
        thread.start()
        
        print(f"Started processor for {args.queue_prefix}:queue:{queue_id} -> port:{port} -> {args.output_dir}")
    
    if not threads:
        print("No valid threads started. Exiting.")
        return
    
    print(f"Started {len(threads)} queue processors. Press Ctrl+C to stop.")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down queue processors...")

if __name__ == '__main__':
    main()
