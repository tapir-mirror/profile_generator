import redis
import json
import uuid
import pandas as pd

def dispatch_to_redis_queues(redis_client, profiles, num_queues):
    """
    Dispatches a list of profiles to a specified number of Redis queues.

    Args:
        redis_client (redis.Redis): An active Redis client connection.
        profiles (pd.DataFrame): A DataFrame containing LinkedIn profiles.
        num_queues (int): The number of parallel queues to distribute profiles among.
    """
    if num_queues <= 0:
        print("Error: Number of queues must be a positive integer.")
        return

    # A base name for our queues for better organization in Redis
    queue_base_name = "profiles:queue"
    total_dispatched = 0

    print(f"Starting dispatch of {len(profiles)} profiles to {num_queues} queues...\n")

    # Convert DataFrame rows to dictionaries and dispatch them
    for i, (index, profile) in enumerate(profiles.iterrows()):
        # Convert the profile Series to a dictionary
        profile_dict = profile.to_dict()
        
        # Determine which queue to send the profile to using round-robin
        queue_index = i % num_queues
        target_queue = f"{queue_base_name}:{queue_index}"

        # --- Prepare the data payload ---
        job_payload = {
            "job_id": str(uuid.uuid4()),
            "profile_data": profile_dict
        }

        # Convert the Python dictionary to a JSON string for storage in Redis
        message = json.dumps(job_payload)

        try:
            # LPUSH adds the new message to the left (head) of the list (queue)
            redis_client.lpush(target_queue, message)
            print(f"  Dispatched profile {i+1} (Job ID: {job_payload['job_id']}) to queue '{target_queue}'")
            total_dispatched += 1
        except redis.exceptions.RedisError as e:
            print(f"Error dispatching profile {i+1} to Redis: {e}")

    print(f"\nDispatch complete. Total profiles sent: {total_dispatched}/{len(profiles)}.")


if __name__ == '__main__':
    # --- Configuration ---
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    NUMBER_OF_QUEUES = 4  # The number of parallel queues you want to use
    DATASET_PATH = "./LinkedIn_Dataset.pcl"  # Path to the LinkedIn dataset

    try:
        # Load the LinkedIn dataset
        print("Loading LinkedIn dataset...")
        dataset = pd.read_pickle(DATASET_PATH)
        print(f"Loaded {len(dataset)} profiles from dataset.")

        # Establish a connection to the Redis server
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        
        # Check if the server is available
        r.ping()
        print(f"Successfully connected to Redis at {REDIS_HOST}:{REDIS_PORT}")

        # Run the dispatcher function with the LinkedIn dataset
        dispatch_to_redis_queues(r, dataset, NUMBER_OF_QUEUES)

    except FileNotFoundError:
        print(f"Error: Could not find the dataset file at {DATASET_PATH}")
    except redis.exceptions.ConnectionError as e:
        print(f"Could not connect to Redis: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

