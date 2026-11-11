#!/usr/bin/env bash
# Download the MediaPipe model files the pyTracking scripts expect (kept out of git: ~12 MB).
set -euo pipefail
cd "$(dirname "$0")"
base=https://storage.googleapis.com/mediapipe-models
[ -f hand_landmarker.task ] || curl -fL -o hand_landmarker.task "$base/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
[ -f face_landmarker.task ] || curl -fL -o face_landmarker.task "$base/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
echo "models ready"
