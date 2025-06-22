import redis

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Check all queues
for i in range(4):
    queue_name = f"profiles:queue:{i}"
    length = r.llen(queue_name)
    print(f"Queue {queue_name}: {length} items") 