# home-lab-pi

This is an excellent refinement! Having a dedicated, high-speed ethernet network for inter-Pi communication (especially for Kubernetes and NFS) while maintaining Wi-Fi for general internet access and external connectivity is a highly robust and common setup for home labs.

The key here is to configure your Raspberry Pis with two network interfaces on different IP subnets and manage routing.

Here's how we'll update the plan:

Comprehensive Home Lab Setup Plan (Updated for Dual Network Interfaces)
Hardware:

1x Raspberry Pi 4 (Kubernetes Control Plane)

2x Raspberry Pi 5 (Kubernetes Worker Nodes, one also acting as a Network File Share Server)

3x High-quality microSD cards (32GB+ recommended)

Power supplies for all Pis

Ethernet cables (3 needed, one for each Pi to the dummy switch)

Dummy Network Switch (4+ ports)

USB-C cable for Pi 5 power

Software/Tools:

Raspberry Pi Imager

SSH Client (PuTTY, Windows Terminal, or built-in ssh in PowerShell/WSL)

Visual Studio Code with Remote - SSH, Python, Docker, Kubernetes, GitLens extensions

GitHub Account

Docker Hub Account (optional, but recommended for CI/CD)

Phase 1: Hardware Preparation & Initial OS Setup (All Pis)
Goal: Get all Raspberry Pis running 64-bit Raspberry Pi OS, updated, and configured for two distinct network interfaces (Wi-Fi for internet, Ethernet for local cluster).

Flash Raspberry Pi OS (64-bit) to SD Cards (for each Pi):

Use Raspberry Pi Imager.

Select "CHOOSE OS" -> "Raspberry Pi OS Lite (64-bit)".

Select "CHOOSE STORAGE" and pick a microSD card.

Crucial Step - Click the Gear Icon (Advanced Options) before writing!

Set "Hostname":

For Pi 4: pi-master

For Pi 5 (Node 1): pi-worker1

For Pi 5 (Node 2): pi-worker2

Enable SSH: "Password authentication".

Set "Username and password": Create a strong password for the default pi user.

Configure wireless LAN: Set your SSID and password. This will be your primary internet access.

Set "Locale settings".

Click "WRITE" for each SD card.

Initial Boot & Network Configuration (for each Pi):

Insert the flashed SD card into each Pi.

Power on all three Raspberry Pis. They should connect to your Wi-Fi network and get an IP address from your home router.

Find their Wi-Fi (wlan0) IP addresses: Check your router's DHCP client list, or use ip a after SSHing in.

Static IP Addresses - Dual Interface Setup (for each Pi):

We'll assign static IPs to both wlan0 (Wi-Fi) and eth0 (Ethernet).

Conceptual Design:

Home Network (Wi-Fi - wlan0): Use your existing home network subnet (e.g., 192.168.1.0/24). DHCP from your home router is fine for this, or you can assign static IPs within your router's DHCP range. For simplicity, we'll keep wlan0 as DHCP for internet access, so it gets DNS and gateway automatically.

Cluster Network (Ethernet - eth0): Create a separate, isolated subnet for the wired connection (e.g., 10.0.0.0/24). This subnet will not have a gateway or DNS servers, as its sole purpose is high-speed internal communication.

SSH into each Pi using its current Wi-Fi IP: ssh pi@<CURRENT_PI_WIFI_IP>

Edit the dhcpcd.conf file: sudo nano /etc/dhcpcd.conf

For pi-master (Pi 4):

Keep the Wi-Fi section (if any) as DHCP or comment it out if you already assigned a static IP via imager and confirmed it works. The goal for wlan0 is simply internet access.

Add the following for eth0 (your dedicated cluster network):

# Configuration for the Wi-Fi interface (wlan0) - usually DHCP
# No explicit static config here unless you specifically need it
# and manage it carefully to avoid conflicts with your router's DHCP.
# It will get IP, gateway, DNS from your home router via DHCP.

# Configuration for the wired (Ethernet) cluster network (eth0)
interface eth0
static ip_address=10.0.0.100/24
# No static routers or domain_name_servers for this interface
# as it's purely for local cluster communication.
# Ensure this interface does NOT try to be the default gateway.
metric 200 # Assign a higher metric to eth0 to prioritize wlan0 for internet
For pi-worker1 (Pi 5 Node 1):

# Configuration for the Wi-Fi interface (wlan0)
# (similar to pi-master, likely DHCP)

# Configuration for the wired (Ethernet) cluster network (eth0)
interface eth0
static ip_address=10.0.0.101/24
metric 200
For pi-worker2 (Pi 5 Node 2 - also your storage Pi):

# Configuration for the Wi-Fi interface (wlan0)
# (similar to pi-master, likely DHCP)

# Configuration for the wired (Ethernet) cluster network (eth0)
interface eth0
static ip_address=10.0.0.102/24
metric 200
Explanation of metric 200: This tells dhcpcd to prefer the wlan0 interface for general internet routing (it will have a lower default metric, usually 100 or less). Traffic destined for the 10.0.0.0/24 subnet will explicitly use eth0. All other traffic (internet) will go out wlan0.

Save (Ctrl+X, Y, Enter).

Connect all three Pis to the dummy switch via Ethernet cables.

Reboot each Pi: sudo reboot.

Verify:

After reboot, SSH into each Pi using its Wi-Fi IP (pi@192.168.1.xxx).

Run ip a to confirm both wlan0 and eth0 have their expected IPs.

Run ip r to check routing. You should see a default route via wlan0 (e.g., default via 192.168.1.1 dev wlan0) and direct routes for the 10.0.0.0/24 network via eth0.

Test inter-Pi communication over Ethernet: ping 10.0.0.100 from pi-worker1, etc.

Test internet access: ping google.com from any Pi.

System Updates & SSH Key Authentication (for each Pi):

SSH into each Pi using its Wi-Fi IP address (pi@192.168.1.xxx).

Perform a full system update: sudo apt update && sudo apt upgrade -y

Set up SSH Key-Based Authentication (Highly Recommended):

On your Windows machine (using Git Bash, PowerShell, or WSL terminal):

Bash

ssh-keygen -t rsa -b 4096 # Press Enter for defaults, optionally set a passphrase
Copy your public key to each Raspberry Pi. You'll now copy it using their Wi-Fi IP for external access:

Bash

ssh-copy-id pi@192.168.1.100 # For pi-master (Wi-Fi IP)
ssh-copy-id pi@1968.1.101 # For pi-worker1 (Wi-Fi IP)
ssh-copy-id pi@192.168.1.102 # For pi-worker2 (Wi-Fi IP)
You'll be prompted for the Pi user's password once for each Pi.

Test: ssh pi@192.168.1.100 should now connect without a password (or only asking for your SSH key passphrase).

Phase 2: VS Code Integration & GitHub Workflow (on Windows & Pis)
Goal: Establish your central code repository on GitHub and configure VS Code for seamless remote development on your Pis.

Install VS Code & Extensions (on your Windows machine): (No change)

Download and install Visual Studio Code.

Install extensions: Remote - SSH, Python, Docker, Kubernetes, GitLens.

Configure VS Code Remote SSH:

Open VS Code's "Remote Explorer".

Add new SSH hosts using the Wi-Fi IP addresses for external access:

ssh pi@192.168.1.100 for pi-master

ssh pi@192.168.1.101 for pi-worker1

ssh pi@192.168.1.102 for pi-worker2

VS Code will save these connections. You can now right-click a host and choose "Connect to Host in New Window". VS Code will install its server component on the Pi.

GitHub Repository Setup: (No change)

Create a new private repository on GitHub (e.g., raspberry-pi-homelab).

Initialize it with README.md and a Python .gitignore template.

Clone the repository to your Windows machine (optional).

Install Git on Raspberry Pis & Clone Repo: (No change)

On each Raspberry Pi (via SSH or VS Code Remote SSH terminal, connected via Wi-Fi IP):

Bash

sudo apt install git -y
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
On pi-master and pi-worker2 (the Pis where you'll be developing/building):

Via VS Code Remote SSH, navigate to /home/pi.

Clone your GitHub repo:

Bash

git clone https://github.com/<your-username>/raspberry-pi-homelab.git
Use a GitHub Personal Access Token (PAT) for security.

Open /home/pi/raspberry-pi-homelab as a folder in VS Code.

Phase 3: Building Your Kubernetes Cluster (Revised Setup)
Goal: Establish a K3s Kubernetes cluster using the dedicated Ethernet network for inter-node communication.

Prepare Raspberry Pis for Kubernetes (on pi-master, pi-worker1, pi-worker2): (No change in commands, but ensure you execute them on all three Pis after eth0 is configured with its static IP).

Disable Swap

Enable Cgroup Memory

Load Kernel Modules

Configure Sysctl Parameters

Reboot all three Pis (sudo reboot)

Install K3s on pi-master (Control Plane):

SSH into pi-master (using its Wi-Fi IP if you prefer, but K3s will bind to its local IP).

Crucially, specify the eth0 IP for K3s binding:

Bash

curl -sfL https://get.k3s.io | K3S_TOKEN="<YOUR_K3S_SECRET_TOKEN>" INSTALL_K3S_EXEC="--node-ip 10.0.0.100" sh -
Replace <YOUR_K3S_SECRET_TOKEN> with a strong, random string you generate. This token will be used for joining workers.

INSTALL_K3S_EXEC="--node-ip 10.0.0.100" forces K3s to use the eth0 interface for its internal communication.

Get Kubeconfig and Token:

Bash

sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config
sudo cat /var/lib/rancher/k3s/server/node-token # Copy this token down!
Join Worker Nodes (on pi-worker1 and pi-worker2):

SSH into pi-worker1 (pi@192.168.1.101).

SSH into pi-worker2 (pi@192.168.1.102).

For each worker, run:

Bash

curl -sfL https://get.k3s.io | K3S_URL=https://10.0.0.100:6443 K3S_TOKEN="<YOUR_K3S_TOKEN>" INSTALL_K3S_EXEC="--node-ip <WORKER_ETH0_IP>" sh -
Replace <YOUR_K3S_TOKEN> with the token from pi-master.

Replace <WORKER_ETH0_IP> with 10.0.0.101 for pi-worker1 and 10.0.0.102 for pi-worker2.

Verify Cluster (from pi-master or your Windows machine):

On pi-master: kubectl get nodes

On your Windows Machine:

Ensure kubectl is installed.

Copy Kubeconfig: SSH into pi-master and copy the content of /etc/rancher/k3s/k3s.yaml.

On your Windows machine, create C:\Users\<YourUser>\.kube\ and a file named config inside it. Paste the content.

Crucially, edit the server: line in C:\Users\<YourUser>\.kube\config from https://127.0.0.1:6443 to https://192.168.1.100:6443 (your pi-master's Wi-Fi IP). This is because your Windows machine will connect over Wi-Fi. The internal K3s communication among Pis will still use 10.0.0.x.

Test from Windows PowerShell/CMD: kubectl get nodes

You should now see pi-master, pi-worker1, and pi-worker2 all listed as "Ready". Kubernetes will primarily use the 10.0.0.x network for internal pod and service communication.

Phase 4: Network File Storage with Web Interface (on pi-worker2)
Goal: Set up a robust file share and a user-friendly web interface on pi-worker2 (your storage-enabled worker node), accessible via its Wi-Fi IP from Windows, but used via its Ethernet IP by Kubernetes.

Install Docker (on pi-worker2): (No change)

Bash

  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  sudo usermod -aG docker pi # Log out/in or reboot for effect
Create Shared Directory: (No change)

mkdir /home/pi/network_share

Install & Configure Samba (SMB/CIFS for Windows access):

Configure Samba to listen on the Wi-Fi interface (wlan0) IP for access from your Windows machine.

Bash

  sudo apt install samba samba-common-bin -y
Edit Samba config: sudo nano /etc/samba/smb.conf

In the [global] section, add:

interfaces = 192.168.1.102/24 wlan0
bind interfaces only = yes
This ensures Samba only listens on the Wi-Fi interface.

Add your share definition at the end (as before):

[NetworkShare]
comment = Raspberry Pi Shared Folder
path = /home/pi/network_share
browseable = yes
writeable = yes
create mask = 0777
directory mask = 0777
public = yes
guest ok = yes
Save and restart Samba: sudo systemctl restart smbd nmbd

Test from Windows: Open File Explorer and type \\192.168.1.102 (Wi-Fi IP) in the address bar. You should see NetworkShare.

Install & Configure NFS Server (for Kubernetes Persistent Volumes):

Configure NFS to listen on the Ethernet interface (eth0) IP for access from other Kubernetes nodes.

Bash

  sudo apt install nfs-kernel-server -y
Edit /etc/exports: sudo nano /etc/exports

Add this line, specifying the eth0 subnet of your cluster (replace 10.0.0.0/24 if you chose a different subnet):

/home/pi/network_share 10.0.0.0/24(rw,sync,no_subtree_check,no_root_squash,insecure)
Export the share: sudo exportfs -a

Restart NFS service: sudo systemctl restart nfs-kernel-server

Test NFS from a Kubernetes Worker Node (pi-worker1):

Bash

  # On pi-worker1 (via SSH to its Wi-Fi IP)
  sudo apt install nfs-common -y
  sudo mkdir -p /mnt/nfs_test
  # Mount using the ETHERNET IP of pi-worker2
  sudo mount -t nfs 10.0.0.102:/home/pi/network_share /mnt/nfs_test
  ls /mnt/nfs_test
  sudo umount /mnt/nfs_test
  sudo rmdir /mnt/nfs_test
Deploy Filebrowser Web Interface (Containerized on pi-worker2):

You'll expose Filebrowser via the Wi-Fi IP for access from your Windows machine.

SSH into pi-worker2 (pi@192.168.1.102).

Run the Filebrowser container, explicitly binding to the Wi-Fi interface's IP:

Bash

docker run -d \
  --name filebrowser \
  --restart=always \
  -p 192.168.1.102:8080:8080 \
  -v /home/pi/network_share:/srv \
  filebrowser/filebrowser:latest-arm64
-p 192.168.1.102:8080:8080: This is the key change. It binds Filebrowser's port 8080 to only listen on the wlan0 IP address on the host, preventing it from binding to eth0 as well, though it generally won't cause issues if it does.

Access the Web Interface: Open a browser on your Windows machine and navigate to http://192.168.1.102:8080.

Phase 5: Python Web Apps & Kubernetes Deployment
Goal: Create a sample Python web application, containerize it, and deploy it to your Kubernetes cluster, leveraging your NFS share for persistence over the dedicated cluster network.

Project Structure: (No change)

apps/my-flask-app/ (with app.py, requirements.txt, Dockerfile)

k8s/my-flask-app/ (with deployment.yaml, service.yaml, pv.yaml, pvc.yaml)

.github/workflows/ (for CI/CD)

Kubernetes Manifests (k8s/my-flask-app/):

pv.yaml (Persistent Volume - crucial change):

YAML

apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  mountOptions:
    - hard
    - nfsvers=4.1
  nfs:
    path: /home/pi/network_share # Path on your NFS server Pi (pi-worker2)
    server: 10.0.0.102 # **Crucially: Use the ETHERNET IP of your pi-worker2 (NFS server)**
pvc.yaml, deployment.yaml, service.yaml: (No changes needed to these files themselves, as they reference the PV/PVC abstractly, and the service will expose via NodePort on the worker's Wi-Fi IP, as that's your internet-facing network for external access).

Local Docker Build & Push (Initial Manual Step / Pre-CI/CD): (No change)

On a Pi (e.g., pi-master via VS Code Remote SSH):

Bash

cd /home/pi/raspberry-pi-homelab/apps/my-flask-app
docker build -t your-dockerhub-username/my-python-app:latest .
docker login
docker push your-dockerhub-username/my-python-app:latest
Deploy to Kubernetes: (No change in commands)

On pi-master (via VS Code Remote SSH terminal or direct SSH):

Bash

cd /home/pi/raspberry-pi-homelab/k8s/my-flask-app
kubectl apply -f pv.yaml
kubectl apply -f pvc.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
Verify Deployment:

Bash

kubectl get pv
kubectl get pvc
kubectl get deployments
kubectl get pods -o wide # See which nodes your pods are running on
kubectl get services my-python-app-service
Find the NodePort from kubectl get services (e.g., 80:3xxxx/TCP).

Access your app: Open a browser on your Windows machine to http://192.168.1.101:<NODEPORT> or http://192.168.1.102:<NODEPORT> (your worker's Wi-Fi IPs).

Test persistence by writing/reading files through the app.

Phase 6: Scaling and Management (No Change)
Phase 7: GitHub Actions for CI/CD Workflows
Goal: Automate building, pushing, and deploying your Docker image when you push changes to GitHub.

Set up a Self-Hosted GitHub Actions Runner (on pi-master): (No change, runner will connect via Wi-Fi IP)

Follow GitHub instructions (Settings -> Actions -> Runners -> New self-hosted runner) to set up the runner as a service on pi-master.

Create GitHub Secrets: (No change)

DOCKER_USERNAME

DOCKER_PASSWORD

KUBECONFIG_BASE64: Ensure the server: field within your k3s.yaml (obtained from pi-master) explicitly uses the Wi-Fi IP address of pi-master (e.g., https://192.168.1.100:6443), as your GitHub Actions runner will connect to the API server via the Wi-Fi network for external connectivity.

Create CI/CD Workflow (.github/workflows/ci-cd.yaml): (No change)

The workflow will remain the same. The runner will communicate with Docker Hub (internet) via wlan0, and kubectl commands to the K3s API server on pi-master will also go via wlan0 (which is routed through your home router).

This setup provides a robust and efficient environment:

Fast Inter-Pi Communication: Kubernetes pods, kube-apiserver on master, kubelet on workers, and NFS traffic will primarily use the dedicated 10.0.0.x Ethernet network, ensuring low latency and high bandwidth for your cluster operations and shared storage.

External Access: Your Windows machine and the GitHub Actions runner will connect to the Pis and their exposed services (like your Python web app or Filebrowser) using the 192.168.1.x Wi-Fi IPs, which are accessible from your home network.

Internet Access: All Pis will use their Wi-Fi connection for general internet access (e.g., apt update, docker pull, git clone, etc.).

Clean Separation: Two distinct network segments prevent broadcast storms or unnecessary traffic from interfering with your cluster's performance.

This is a professional and resilient home lab configuration!
