#!/bin/bash

# SSH tunnel details
REMOTE_USER=""
REMOTE_HOST=""
REMOTE_HOST2=""
REMOTE_PORT=""
LOCAL_MEDGEMMA_PORT=""
LOCAL_GEMMA_PORT=""
REMOTE_MEDGEMMA_FORWARD_PORT=""
REMOTE_GEMMA_FORWARD_PORT=""

# Run SSH tunnel in the background
ssh -f -N -L ${LOCAL_MEDGEMMA_PORT}:localhost:${REMOTE_MEDGEMMA_FORWARD_PORT} -p ${REMOTE_PORT} ${REMOTE_USER}@${REMOTE_HOST}
ssh -f -N -L ${LOCAL_GEMMA_PORT}:localhost:${REMOTE_GEMMA_FORWARD_PORT} -p ${REMOTE_PORT} ${REMOTE_USER}@${REMOTE_HOST2}

echo "SSH tunnel established Medgemma: localhost:${LOCAL_MEDGEMMA_PORT} -> ${REMOTE_HOST}:${REMOTE_MEDGEMMA_FORWARD_PORT}"
echo "SSH tunnel established Gemma: localhost:${LOCAL_GEMMA_PORT} -> ${REMOTE_HOST}:${REMOTE_GEMMA_FORWARD_PORT}"
echo "Too kill process run  lsof -i :PORT; kill <PID>"
