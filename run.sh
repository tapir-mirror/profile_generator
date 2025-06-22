#!/bin/bash

# Check if model name is provided
if [ $# -eq 0 ]; then
    echo "Error: Model name is required"
    echo "Usage: $0 <model_name>"
    echo "Example: $0 qwen:32b"
    exit 1
fi

MODEL_NAME="$1"

echo "🚀 Starting three queue profile processing pipeline with model: $MODEL_NAME"

# Create output directory if it doesn't exist
mkdir -p ../output

echo "📦 Starting dispatcher with three queues..."

# Start dispatcher with three queues
python3 dispatcher.py --num-queues 3 &
DISPATCHER_PID=$!
echo "Started dispatcher (PID: $DISPATCHER_PID) - queues 0,1,2"

# Wait a few seconds for dispatcher to initialize
sleep 5

echo "🤖 Starting three prompt processors..."

# Start three prompt processors, each with its own queue
# Each will process from a different queue and output to different subdirectories
python3 prompt.py --num-queues 1 --queue-offset 0 --start-port 11434 --output-dir "../output/worker1" --model "$MODEL_NAME" &
GENERATOR1_PID=$!
echo "Started generator 1 (PID: $GENERATOR1_PID) - queue 0 -> ../output/worker1/"

python3 prompt.py --num-queues 1 --queue-offset 1 --start-port 11434 --output-dir "../output/worker2" --model "$MODEL_NAME" &
GENERATOR2_PID=$!
echo "Started generator 2 (PID: $GENERATOR2_PID) - queue 1 -> ../output/worker2/"

python3 prompt.py --num-queues 1 --queue-offset 2 --start-port 11434 --output-dir "../output/worker3" --model "$MODEL_NAME" &
GENERATOR3_PID=$!
echo "Started generator 3 (PID: $GENERATOR3_PID) - queue 2 -> ../output/worker3/"

echo "✅ All instances started!"
echo ""
echo "📊 Process Status:"
echo "Dispatcher: PID $DISPATCHER_PID (queues 0,1,2)"
echo "Generator 1: PID $GENERATOR1_PID (queue 0 -> ../output/worker1/)"
echo "Generator 2: PID $GENERATOR2_PID (queue 1 -> ../output/worker2/)"
echo "Generator 3: PID $GENERATOR3_PID (queue 2 -> ../output/worker3/)"
echo ""
echo "🛑 To stop all processes:"
echo "kill $DISPATCHER_PID $GENERATOR1_PID $GENERATOR2_PID $GENERATOR3_PID"
echo ""
echo "📁 Output directories:"
echo "ls -la ../output/worker*/"

# Make script executable
chmod +x "$0"

# Keep script running to monitor
wait 