apt update -y && apt upgrade -y
# Hetzner boxes need the newer kernel for non shit network card driver
apt install --install-recommends linux-generic-hwe-18.04
