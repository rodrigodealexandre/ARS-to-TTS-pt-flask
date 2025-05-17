#!/bin/bash

echo "Setting up the Portuguese Voice Assistant environment..."

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Please run this script with sudo"
    exit 1
fi

# 1. Install system dependencies
echo "Installing system dependencies..."
apt-get update
apt-get install -y python3-dev python3-setuptools python3-pip python3-wheel
apt-get install -y build-essential libssl-dev libffi-dev
apt-get install -y espeak-ng python3-espeak

# 2. Download and install cuDNN
echo "Downloading and installing cuDNN..."
wget https://developer.download.nvidia.com/compute/cudnn/9.10.1/local_installers/cudnn-local-repo-ubuntu2204-9.10.1_1.0-1_amd64.deb
dpkg -i cudnn-local-repo-ubuntu2204-9.10.1_1.0-1_amd64.deb
cp /var/cudnn-local-repo-ubuntu2204-9.10.1/cudnn-*-keyring.gpg /usr/share/keyrings/
apt-get update
apt-get -y install cudnn
apt-get -y install cudnn-cuda-12
apt-get install -y libcudnn9-cuda-12
apt-get install -y libcudnn9-dev-cuda-12

# Clean up downloaded files
rm cudnn-local-repo-ubuntu2204-9.10.1_1.0-1_amd64.deb

echo "System dependencies installed successfully!"
echo ""
echo "Now run the following commands to set up the Python environment:"
echo ""
echo "1. Create and activate a new virtual environment:"
echo "   python -m venv LLM"
echo "   source LLM/bin/activate"
echo ""
echo "2. Install Python dependencies in order:"
echo "   pip install numpy==1.22.0"
echo "   pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
echo "   pip install scikit-learn==1.2.2"
echo "   pip install flask==2.0.1 Werkzeug==2.0.3"
echo "   pip install faster-whisper==0.9.0 transformers==4.30.0"
echo "   pip install soundfile==0.12.1 librosa==0.10.1"
echo "   pip install scipy==1.11.3 numba==0.56.4 llvmlite==0.39.1"
echo "   pip install git+https://github.com/coqui-ai/TTS"
echo "   pip install gradio plotly pandas pycoingecko"
echo ""
echo "3. Test the installation:"
echo "   python -c 'import torch; print(torch.cuda.is_available())'"
echo "" 