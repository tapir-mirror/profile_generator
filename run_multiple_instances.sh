
# Example script showing how to run multiple instances of dispatcher and prompt generator
#!/bin/bash

echo "🚀 Starting multiple instances of profile processing pipeline"

# Kill any existing processes (optional)
# pkill -f "python3 dispatcher.py"
# pkill -f "python3 prompt.py"

echo "📦 Starting dispatchers..."

# Dispatcher 1: Process first dataset to queues 0-3
python3 dispatcher.py --queue-offset 0 --num-queues 4 &
DISPATCHER1_PID=$!
echo "Started dispatcher 1 (PID: $DISPATCHER1_PID) - queues 0-3"

# Dispatcher 2: Process second dataset to queues 4-7  
python3 dispatcher.py --queue-offset 4 --num-queues 4 &
DISPATCHER2_PID=$!
echo "Started dispatcher 2 (PID: $DISPATCHER2_PID) - queues 4-7"

# Wait a few seconds for d
sleep 5

echo "🤖 Starting prompt +..."

# Generator 1: Process ports 8000-8003 (queues 0-3) -> ../output1/
python3 prompt.py --start-port 8000 --num-queues 4 --queue-offset 0 --output-dir "../output1" &
GENERATOR1_PID=$!
echo "Started generator 1 (PID: $GENERATOR1_PID) - ports 8000-8003 -> ../output1/"

# Generator 2: Process ports 8004-8007 (queues 4-7) -> ../output2/
python3 prompt.py --start-port 8004 --num-queues 4 --queue-offset 4 --output-dir "../output2" &
GENERATOR2_PID=$!
echo "Started generator 2 (PID: $GENERATOR2_PID) - ports 8004-8007 -> ../output2/"

echo "✅ All instances started!"
echo ""
echo "📊 Process Status:"
echo "Dispatcher 1: PID $DISPATCHER1_PID (queues 0-3)"
echo "Dispatcher 2: PID $DISPATCHER2_PID (queues 4-7)" 
echo "Generator 1:  PID $GENERATOR1_PID (ports 8000-8003 -> ../output1/)"
echo "Generator 2:  PID $GENERATOR2_PID (ports 8004-8007 -> ../output2/)"
echo ""
echo "🛑 To stop all processes:"
echo "kill $DISPATCHER1_PID $DISPATCHER2_PID $GENERATOR1_PID $GENERATOR2_PID"
echo ""
echo "📁 Output directories:"
echo "ls -la ../output1/ ../output2/"

# Keep script running to monitor
wait
