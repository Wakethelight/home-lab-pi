Complete & Updated Home Lab Setup Plan
Hardware:

1x Raspberry Pi 4 (Kubernetes Control Plane: pi-master)

2x Raspberry Pi 5 (Kubernetes Worker Nodes: pi-worker1, pi-worker2 - where pi-worker2 also acts as NFS/Samba server)

3x High-quality microSD cards (32GB+ recommended)

Power supplies for all Pis

Ethernet cables (3 needed, one for each Pi to the dummy switch)

1x Dummy Network Switch (4+ ports)

USB-C cables for Pi 5 power

Software/Tools:

Raspberry Pi Imager

SSH Client (PuTTY, Windows Terminal, or built-in ssh in PowerShell/WSL)

Visual Studio Code with Remote - SSH, Python, Docker, Kubernetes, GitLens extensions

GitHub Account

Docker Hub Account (optional, but recommended for CI/CD)

Phase 1: Hardware Preparation & Initial OS Setup (All Pis)
Goal: Get all Raspberry Pis running 64-bit Raspberry Pi OS, updated, and configured for dual network interfaces (Wi-Fi for internet, Ethernet for local cluster).

Flash Raspberry Pi OS (64-bit) to SD Cards (for each Pi):

Use Raspberry Pi Imager.

Select "CHOOSE OS" -> "Raspberry Pi OS (other)" -> "Raspberry Pi OS Lite (64-bit)".

Select "CHOOSE STORAGE" and pick a microSD card.

Crucial Step - Click the Gear Icon (Advanced Options) before writing!

Set "Hostname":

For Pi 4: pi-master

For Pi 5 (Node 1): pi-worker1

For Pi 5 (Node 2): pi-worker2

Enable SSH: "Password authentication".

Set "Username and password": Create a strong password for your default user (e.g., pi or wake).

Configure wireless LAN: Set your SSID and password for your home Wi-Fi network. This will be your primary internet access.

Set "Locale settings".

Click "WRITE" for each SD card.

Initial Boot & Network Configuration (for each Pi):

Insert the flashed SD card into each Pi.

Power on all three Raspberry Pis. They should connect to your Wi-Fi network and get an IP address from your home router.

Find their Wi-Fi (wlan0) IP addresses: Check your router's DHCP client list, or ssh into each Pi using the hostname (e.g., ssh pi@pi-master.local) and run ip a.

Static IP Addresses - Dual Interface Setup (for each Pi) - Using NetworkManager (nmcli):

Conceptual Design:

Home Network (Wi-Fi - wlan0): Use your existing home network subnet (e.g., 192.168.1.0/24). It will get its IP, gateway, and DNS from your home router via DHCP.

Cluster Network (Ethernet - eth0): Create a separate, isolated subnet for the wired connection (e.g., 10.0.0.0/24). This subnet will not have a gateway or DNS servers.

SSH into each Pi using its current Wi-Fi IP: ssh <your_username>@<CURRENT_PI_WIFI_IP>

Identify Connection Names:

Bash

nmcli connection show
nmcli device status
Note down the exact names of your Wi-Fi connection (likely your SSID, e.g., MyHomeWiFi) and Ethernet connection (e.g., Wired connection 1).

Configure eth0 (Ethernet - Cluster Network) - For pi-master, pi-worker1, and pi-worker2:
(Replace "Wired connection 1" with your actual Ethernet connection name if different. Replace 10.0.0.X with the correct IP for each Pi.)

For pi-master (Pi 4):

Bash

sudo nmcli connection modify "Wired connection 1" ipv4.method manual \
ipv4.addresses 10.0.0.100/24 \
ipv4.gateway "" \
ipv4.dns "" \
connection.autoconnect yes \
ipv4.never-default yes \
connection.autoconnect-priority 200
For pi-worker1 (Pi 5 Node 1):

Bash

sudo nmcli connection modify "Wired connection 1" ipv4.method manual \
ipv4.addresses 10.0.0.101/24 \
ipv4.gateway "" \
ipv4.dns "" \
connection.autoconnect yes \
ipv4.never-default yes \
connection.autoconnect-priority 200
For pi-worker2 (Pi 5 Node 2 - also your storage Pi):

Bash

sudo nmcli connection modify "Wired connection 1" ipv4.method manual \
ipv4.addresses 10.0.0.102/24 \
ipv4.gateway "" \
ipv4.dns "" \
connection.autoconnect yes \
ipv4.never-default yes \
connection.autoconnect-priority 200
Configure wlan0 (Wi-Fi - Home Network) - For all Pis:
(Replace "MyHomeWiFi" with your actual Wi-Fi connection name.)

Bash

sudo nmcli connection modify "MyHomeWiFi" ipv4.method auto \
ipv4.route-metric 100 \
connection.autoconnect yes
Connect all three Pis to the dummy switch via Ethernet cables.

Apply Changes and Reboot all Pis:

Bash

sudo reboot
Verify Network (after reboot):

SSH into each Pi using its Wi-Fi IP (ssh <your_username>@192.168.1.xxx).

Run ip a to confirm both wlan0 and eth0 have their expected IPs.

Run ip r to check routing (ensure wlan0 has a default route and eth0 has 10.0.0.0/24 routes).

Test inter-Pi communication over Ethernet: ping 10.0.0.100 from pi-worker1.

Test internet access: ping google.com from any Pi.

System Updates & SSH Key Authentication (for each Pi):

SSH into each Pi (using its Wi-Fi IP address).

Perform a full system update:

Bash

sudo apt update && sudo apt upgrade -y
sudo apt autoremove -y
Set up SSH Key-Based Authentication (on your Windows machine):

Bash

ssh-keygen -t rsa -b 4096 # Press Enter for defaults, optionally set a passphrase
ssh-copy-id <your_username>@192.168.1.100 # For pi-master (Wi-Fi IP)
ssh-copy-id <your_username>@192.168.1.101 # For pi-worker1 (Wi-Fi IP)
ssh-copy-id <your_username>@192.168.1.102 # For pi-worker2 (Wi-Fi IP)
Test: ssh <your_username>@192.168.1.100 should now connect without a password.

Phase 2: VS Code Integration & GitHub Workflow (on Windows & Pis)
Goal: Establish your central code repository on GitHub and configure VS Code for seamless remote development on your Pis.

Install VS Code & Extensions (on your Windows machine):

Install Visual Studio Code.

Install extensions: Remote - SSH, Python, Docker, Kubernetes, GitLens.

Configure VS Code Remote SSH:

Open VS Code's "Remote Explorer".

Add new SSH hosts using the Wi-Fi IP addresses for external access:

ssh <your_username>@192.168.1.100 for pi-master

ssh <your_username>@192.168.1.101 for pi-worker1

ssh <your_username>@192.168.1.102 for pi-worker2

GitHub Repository Setup:

Create a new private repository on GitHub (e.g., raspberry-pi-homelab).

Initialize it with README.md and a Python .gitignore template.

(Optional: Clone the repository to your Windows machine for local backups/testing.)

Install Git on Raspberry Pis & Clone Repo:

On each Raspberry Pi (via SSH or VS Code Remote SSH terminal):

Bash

sudo apt install git -y
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
On pi-master and pi-worker2 (the Pis where you'll be developing/building):

Via VS Code Remote SSH, navigate to /home/<your_username>.

Clone your GitHub repo:

Bash

git clone https://github.com/<your-username>/raspberry-pi-homelab.git
Use a GitHub Personal Access Token (PAT) for security when prompted.

Open /home/<your_username>/raspberry-pi-homelab as a folder in VS Code.

Phase 3: Kubernetes Cluster Setup (Pi 4 Master, Pi 5 Workers)
Goal: Establish a K3s Kubernetes cluster using the dedicated Ethernet network for inter-node communication.

Prepare Raspberry Pis for Kubernetes (on pi-master, pi-worker1, pi-worker2):

SSH into each Pi.

Disable Swap:

Bash

sudo swapoff -a
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab
Enable Cgroup Memory:

Bash

sudo nano /boot/firmware/cmdline.txt
# Add 'cgroup_enable=cpuset cgroup_enable=memory cgroup_memory=1' to the END of the single line, separated by a space. DO NOT create a new line.
Load Kernel Modules:

Bash

sudo modprobe overlay
sudo modprobe br_netfilter
sudo tee /etc/modules-load.d/k8s.conf <<EOF
overlay
br_netfilter
EOF
Configure Sysctl Parameters:

Bash

sudo tee /etc/sysctl.d/k8s.conf <<EOF
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF
sudo sysctl --system
Reboot all three Pis: sudo reboot

Install K3s on pi-master (Control Plane) - WITH CORRECT CONFIGURATION & FIXES:

SSH into pi-master (<your_username>@192.168.1.100 after reboot).

Generate a strong K3s token:

Bash

K3S_SECRET_TOKEN=$(openssl rand -hex 32)
echo "Your K3s Token: $K3S_SECRET_TOKEN"
Copy this token down securely! You'll need it for the workers.

Install K3s with --node-ip and --write-kubeconfig-mode:

Bash

curl -sfL https://get.k3s.io | K3S_TOKEN="${K3S_SECRET_TOKEN}" INSTALL_K3S_EXEC="--node-ip 10.0.0.100 --write-kubeconfig-mode 0644" sh -
Get Kubeconfig and ensure user permissions (Crucial Fix):

Bash

mkdir -p ~/.kube                                  # Create the .kube directory
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config  # Copy the kubeconfig
sudo chown $(whoami):$(whoami) ~/.kube/config       # Change ownership to your user
chmod 600 ~/.kube/config                          # Set permissions for your user only
Set KUBECONFIG environment variable (for your user):

Bash

echo 'export KUBECONFIG=$HOME/.kube/config' >> ~/.bashrc
source ~/.bashrc
Verify K3s token (same as the one you copied):

Bash

sudo cat /var/lib/rancher/k3s/server/node-token
Join Worker Nodes (on pi-worker1 and pi-worker2):

SSH into pi-worker1 (<your_username>@192.168.1.101).

SSH into pi-worker2 (<your_username>@192.168.1.102).

For each worker, run:

Bash

curl -sfL https://get.k3s.io | K3S_URL=https://10.0.0.100:6443 K3S_TOKEN="<THE_K3S_TOKEN_FROM_MASTER>" INSTALL_K3S_EXEC="--node-ip <WORKER_ETH0_IP>" sh -
Replace <THE_K3S_TOKEN_FROM_MASTER> with the token you got from sudo cat /var/lib/rancher/k3s/server/node-token on pi-master.

Replace <WORKER_ETH0_IP> with 10.0.0.101 for pi-worker1 and 10.0.0.102 for pi-worker2.

Force Wired Connection for Inter-Pi Hostname Resolution (on all three Pis):

SSH into each Pi (you can use their Wi-Fi IPs).

Edit /etc/hosts file:

Bash

sudo nano /etc/hosts
Add entries for all your Pis, using their Ethernet IP addresses:

# Cluster hostnames (use Ethernet IPs)
10.0.0.100      pi-master
10.0.0.101      pi-worker1
10.0.0.102      pi-worker2
(Add these lines at the end of the file. Ensure the existing 127.0.1.1 <hostname> line is for the correct hostname of that specific Pi).

Save (Ctrl+X, Y, Enter).

(Optional, but good for immediate effect): sudo systemd-resolve --flush-caches

Test: From any Pi, ping pi-master, ping pi-worker1, ping pi-worker2. They should resolve to their 10.0.0.x IPs.

Verify Kubernetes Cluster (from pi-master):

Bash

  kubectl get nodes
You should now see pi-master, pi-worker1, and pi-worker2 all listed as "Ready".

On your Windows Machine:

Install kubectl: Follow instructions here.

Copy Kubeconfig: SSH into pi-master and copy the content of /home/<your_username>/.kube/config.

On your Windows machine, create C:\Users\<YourUser>\.kube\ and a file named config inside it. Paste the content.

Crucially, edit the server: line in C:\Users\<YourUser>\.kube\config from https://10.0.0.100:6443 to https://192.168.1.100:6443 (your pi-master's Wi-Fi IP). This is because your Windows machine will connect over Wi-Fi.

Test from Windows PowerShell/CMD: kubectl get nodes

Phase 4: Network File Storage with Web Interface (on pi-worker2)
Goal: Set up a robust file share and a user-friendly web interface on pi-worker2 (your storage-enabled worker node).

Install Docker (on pi-worker2):

SSH into pi-worker2.

Bash

  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  sudo usermod -aG docker <your_username> # Log out/in or reboot for effect
Create Shared Directory:

Bash

  mkdir /home/<your_username>/network_share
Install & Configure Samba (SMB/CIFS for Windows access):

Configure Samba to listen on the Wi-Fi interface (wlan0) IP for access from your Windows machine.

SSH into pi-worker2.

Bash

  sudo apt install samba samba-common-bin -y
Edit Samba config: sudo nano /etc/samba/smb.conf

In the [global] section, add:

interfaces = 192.168.1.102/24 wlan0
bind interfaces only = yes
Add your share definition at the end:

[NetworkShare]
comment = Raspberry Pi Shared Folder
path = /home/<your_username>/network_share
browseable = yes
writeable = yes
create mask = 0777
directory mask = 0777
public = yes
guest ok = yes
(Security Note: For production, set up Samba users instead of public = yes).

Save and restart Samba: sudo systemctl restart smbd nmbd

Test from Windows: Open File Explorer and type \\192.168.1.102 (Wi-Fi IP) in the address bar. You should see NetworkShare.

Install & Configure NFS Server (for Kubernetes Persistent Volumes):

Configure NFS to listen on the Ethernet interface (eth0) IP for access from other Kubernetes nodes.

SSH into pi-worker2.

Bash

  sudo apt install nfs-kernel-server -y
Edit /etc/exports: sudo nano /etc/exports

Add this line (replace 10.0.0.0/24 with your cluster network CIDR):

/home/<your_username>/network_share 10.0.0.0/24(rw,sync,no_subtree_check,no_root_squash,insecure)
Export the share: sudo exportfs -a

Restart NFS service: sudo systemctl restart nfs-kernel-server

Test NFS from a Kubernetes Worker Node (pi-worker1):

SSH into pi-worker1.

Bash

  sudo apt install nfs-common -y # If not already installed
  sudo mkdir -p /mnt/nfs_test
  sudo mount -t nfs 10.0.0.102:/home/<your_username>/network_share /mnt/nfs_test
  ls /mnt/nfs_test
  sudo umount /mnt/nfs_test
  sudo rmdir /mnt/nfs_test
Deploy Filebrowser Web Interface (Containerized on pi-worker2):

Expose Filebrowser via the Wi-Fi IP for access from your Windows machine.

SSH into pi-worker2.

Bash

  docker run -d \
    --name filebrowser \
    --restart=always \
    -p 192.168.1.102:8080:8080 \
    -v /home/<your_username>/network_share:/srv \
    filebrowser/filebrowser:latest-arm64
Access the Web Interface: Open a browser on your Windows machine and navigate to http://192.168.1.102:8080. (Remember to change default admin password admin:admin immediately!)

Phase 5: Python Web Apps & Kubernetes Deployment
Goal: Create a sample Python web application, containerize it, and deploy it to your Kubernetes cluster, leveraging your NFS share for persistence over the dedicated cluster network.

Project Structure (in your raspberry-pi-homelab Git repo):

raspberry-pi-homelab/
├── apps/
│   └── my-flask-app/
│       ├── app.py
│       ├── requirements.txt
│       └── Dockerfile
├── k8s/
│   └── my-flask-app/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── pv.yaml
│       └── pvc.yaml
└── .github/
    └── workflows/
        └── ci-cd.yaml
apps/my-flask-app/app.py (Example): (Provided in previous instruction)

apps/my-flask-app/requirements.txt: Flask

apps/my-flask-app/Dockerfile: (Provided in previous instruction)

Kubernetes Manifests (k8s/my-flask-app/):

pv.yaml (Persistent Volume - links to NFS via Ethernet IP):

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
    path: /home/<your_username>/network_share
    server: 10.0.0.102 # **Crucially: Use the ETHERNET IP of your pi-worker2 (NFS server)**
pvc.yaml (Persistent Volume Claim): (Provided in previous instruction)

deployment.yaml (ensure Docker Hub image name is correct): (Provided in previous instruction)

image: your-dockerhub-username/my-python-app:latest

service.yaml (type NodePort for external access): (Provided in previous instruction)

Local Docker Build & Push (Initial Manual Step / Pre-CI/CD):

On pi-master or pi-worker2 (any Pi with Docker installed and access to your Git repo via VS Code Remote SSH):

Bash

cd /home/<your_username>/raspberry-pi-homelab/apps/my-flask-app
docker build -t your-dockerhub-username/my-python-app:latest .
docker login # Enter your Docker Hub credentials
docker push your-dockerhub-username/my-python-app:latest
Deploy to Kubernetes:

On pi-master (via VS Code Remote SSH terminal or direct SSH):

Bash

cd /home/<your_username>/raspberry-pi-homelab/k8s/my-flask-app
kubectl apply -f pv.yaml
kubectl apply -f pvc.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
Verify Deployment:

Bash

kubectl get pv
kubectl get pvc
kubectl get deployments
kubectl get pods -o wide
kubectl get services my-python-app-service
Find the NodePort from kubectl get services (e.g., 80:3xxxx/TCP).

Access your app: Open a browser on your Windows machine to http://192.168.1.101:<NODEPORT> or http://192.168.1.102:<NODEPORT> (your worker's Wi-Fi IPs).

Test persistence (write/read files via the app) and check the actual file on pi-worker2 in /home/<your_username>/network_share.

Phase 6: Scaling and Management
Goal: Understand how to scale your applications and manage your Kubernetes cluster effectively.

Scaling Applications:

Modify replicas in k8s/my-flask-app/deployment.yaml and kubectl apply -f deployment.yaml.

Or use the command line: kubectl scale deployment my-python-app --replicas=3

Observe how Kubernetes distributes pods across pi-worker1 and pi-worker2.

Basic Kubernetes Management Commands:

kubectl logs <pod_name>

kubectl describe pod <pod_name>

kubectl exec -it <pod_name> -- bash

kubectl delete -f <yaml_file>

kubectl top nodes / kubectl top pods

Phase 7: GitHub Actions for CI/CD Workflows
Goal: Automate building, pushing, and deploying your Docker image when you push changes to GitHub.

Set up a Self-Hosted GitHub Actions Runner (on pi-master):

Go to your GitHub repository -> Settings -> Actions -> Runners -> New self-hosted runner.

Follow the instructions to download, configure, and run the runner application as a service on pi-master.

Create GitHub Secrets:

Go to your GitHub repository -> Settings -> Secrets and variables -> Actions -> New repository secret.

Add the following secrets:

DOCKER_USERNAME: Your Docker Hub username.

DOCKER_PASSWORD: Your Docker Hub password or a Personal Access Token (PAT).

KUBECONFIG_BASE64:

On your pi-master, get the content of /home/<your_username>/.kube/config.

Ensure the server: field within that YAML uses the Wi-Fi IP address of pi-master (e.g., https://192.168.1.100:6443), not 10.0.0.100.

Base64 encode this entire modified YAML content:

Bash

cat /home/<your_username>/.kube/config | base64 -w 0
Copy the output and paste it as the value for KUBECONFIG_BASE64.

Create CI/CD Workflow (.github/workflows/ci-cd.yaml):

Create this file in your Git repository.

Content for ci-cd.yaml:

YAML

name: Python App CI/CD

on:
  push:
    branches:
      - main # Trigger on pushes to the main branch
    paths:
      - 'apps/my-flask-app/**' # Only run if app code changes
      - 'k8s/my-flask-app/**' # Or K8s manifests change
  workflow_dispatch: # Allows manual trigger from GitHub UI

jobs:
  build-and-push:
    runs-on: self-hosted # Use your Raspberry Pi runner (pi-master)
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r apps/my-flask-app/requirements.txt
      working-directory: ./apps/my-flask-app

    - name: Lint with Flake8
      run: |
        pip install flake8
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
      working-directory: ./apps/my-flask-app

    - name: Build Docker image
      run: |
        docker build -t ${{ secrets.DOCKER_USERNAME }}/my-python-app:${{ github.sha }} -t ${{ secrets.DOCKER_USERNAME }}/my-python-app:latest ./apps/my-flask-app

    - name: Log in to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}

    - name: Push Docker image
      run: |
        docker push ${{ secrets.DOCKER_USERNAME }}/my-python-app:${{ github.sha }}
        docker push ${{ secrets.DOCKER_USERNAME }}/my-python-app:latest

  deploy:
    needs: build-and-push
    runs-on: self-hosted
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Kubeconfig
      run: |
        mkdir -p ~/.kube
        echo "${{ secrets.KUBECONFIG_BASE64 }}" | base64 -d > ~/.kube/config
        chmod 600 ~/.kube/config

    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f k8s/my-flask-app/pv.yaml
        kubectl apply -f k8s/my-flask-app/pvc.yaml
        kubectl apply -f k8s/my-flask-app/deployment.yaml
        kubectl apply -f k8s/my-flask-app/service.yaml
      working-directory: ./k8s/my-flask-app
Final Steps: Test and Iterate
Commit and Push: After creating all files (Python app, Dockerfile, Kubernetes manifests, CI/CD workflow), commit them to your Git repository (git add ., git commit -m "Initial home lab setup", git push).

Monitor GitHub Actions: Go to your GitHub repo -> "Actions" tab. You should see your workflow trigger and run. Watch the logs for success or errors.

Verify Deployment: Once the GitHub Action completes successfully, check your Kubernetes cluster again: kubectl get pods -o wide, kubectl get svc. Access your web app and test the file write/read functionality to ensure NFS persistence is working.

You're well on your way to a powerful and well-configured home lab! Good luck with the remaining steps!
