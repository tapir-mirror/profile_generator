# Model Deployment Configuration

This document lists all the deployed models, their versions, and their respective ports.

## Models

| Port | Model | Version/Checkpoint | Quantization | Memory Usage |
|------|-------|-------------------|--------------|--------------|
| 8000 | Llama 2 | meta-llama/Llama-2-13b-chat-hf | INT8 | 10.4% |
| 8001 | Mistral | mistralai/Mistral-7B-Instruct-v0.2 | FP16 | 10.4% |
| 8002 | CodeLlama | codellama/CodeLlama-7b-Instruct-hf | INT8 | 5.7% |
| 8003 | Phi-2 | microsoft/phi-2 | FP16 | 4.7% |
| 8004 | Qwen | Qwen/Qwen-7B-Chat | INT4 | 3.6% |
| 8005 | Mixtral | mistralai/Mixtral-8x7B-Instruct-v0.1 | INT4 | 17.7% |
| 8006 | Qwen3 | abhishekchohan/Qwen3-14B-AWQ | AWQ | 9.5% |
| 8007 | Phi-4 | microsoft/phi-4-mini-instruct | INT4 | 2.8% |

## Access

All models are running as vLLM API servers and can be accessed via HTTP at:
```http
http://localhost:<PORT>/v1/completions
```

## Quantization Details
- INT8: 8-bit integer quantization
- INT4: 4-bit integer quantization
- FP16: 16-bit floating point (no quantization)
- AWQ: Activation-aware Weight Quantization

## Memory Allocation
Total GPU memory utilization across all models: 64.8% 