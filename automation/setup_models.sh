#!/usr/bin/env sh
# Download the Kokoro TTS model files (Apache-2.0) from the project's GitHub release into assets/models/.
set -e
D="$(dirname "$0")/../assets/models"; mkdir -p "$D"; R=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
[ -s "$D/kokoro-v1.0.onnx" ] || curl -fsSL -o "$D/kokoro-v1.0.onnx" "$R/kokoro-v1.0.onnx"
[ -s "$D/voices-v1.0.bin" ]  || curl -fsSL -o "$D/voices-v1.0.bin"  "$R/voices-v1.0.bin"
ls -la "$D"
