echo "Updating system..."
sudo apt update && sudo apt upgrade -y

echo "Installing required packages..."
sudo apt install git wget curl python3 python3-pip python3-venv python3-dev python3-matplotlib python3-pandas libopengl0 libgl1 libegl1 mesa-utils flightgear -y

echo "Removing ModemManager..."
sudo apt remove modemmanager -y

echo "Installing Python MAVLink tools..."
python3 -m pip install --break-system-packages --force-reinstall empy==3.3.4 pymavlink MAVProxy future

echo "Downloading QGroundControl..."
mkdir -p ~/Downloads
cd ~/Downloads
wget -O QGroundControl-x86_64.AppImage https://d176tv9ibo4jno.cloudfront.net/latest/QGroundControl-x86_64.AppImage
chmod +x QGroundControl-x86_64.AppImage

echo "Cloning ArduPilot..."
cd ~
git clone https://github.com/ArduPilot/ardupilot.git
cd ~/ardupilot
git submodule update --init --recursive
echo "Adding custom SITL locations..."
echo ' KLZU_RWY7=33.974738,-83.970493,324,64' >> ~/ardupilot/Tools/autotest/locations.txt
echo ' TRIAL_FIELD=33.968638,-84.415519,327,6' >> ~/ardupilot/Tools/autotest/locations.txt

echo "Adding Aliases..."
cat ~/uas-lab/setup/aliases.sh >> ~/.bashrc

echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
export PATH="$HOME/.local/bin:$PATH"

source ~/.bashrc

echo "UAS Lab setup complete."
