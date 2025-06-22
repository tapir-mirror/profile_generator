#!/bin/bash
#$ -cwd
#$ -j y
#$ -pe smp 8        # 8 cores (8 cores per GPU)
#$ -l h_rt=1:0:0    # 1 hour runtime (required to run on the short queue)
#$ -l h_vmem=11G    # 11 * 8 = 88G total RAM
#$ -l gpu=1         # request 1 

alias cds="cd /data/scratch/apx186"
alias jt="jobstats -b `date '+%d/%m/%y'`"
alias glogin="qlogin -pe smp 8 -l h_rt=1:0:0 -l h_vmem=11G -l gpu=1"
alias lp="module load python/3.12.1-gcc-12.2.0 && module load cuda"
export OLLAMA_MODELS=/data/scratch/apx186/.ollama/models
module load nano
module load use.own uv
module load use.own ollama
module load use.own redis-server
module load use.own redis-cli
source .venv/bin/activate
redis-server &
ollama serve &
./run.sh phi4:14b
