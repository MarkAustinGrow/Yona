# Yona Deployment Guide

This guide explains how to deploy the Yona application to a Linode server using Docker and Docker Compose.

## 1. Setting Up a Linode Instance

### 1.1 Create a Linode Instance

1. Sign up for a Linode account if you don't have one already.
2. Create a new Linode instance:
   - Select Ubuntu 22.04 LTS as the operating system
   - Choose a plan with at least 2GB RAM (Shared CPU 2GB is a good starting point)
   - Select a region close to your users
   - Set a strong root password
   - Add SSH keys if you have them

### 1.2 Connect to Your Linode

```bash
ssh root@your-linode-ip
```

### 1.3 Update the System

```bash
apt update && apt upgrade -y
```

## 2. Installing Docker and Docker Compose

### 2.1 Install Docker

```bash
# Install prerequisites
apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io

# Verify Docker installation
docker --version
```

### 2.2 Install Docker Compose

```bash
# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verify Docker Compose installation
docker-compose --version
```

## 3. Deploying the Application

### 3.1 Create a Non-Root User (Optional but Recommended)

```bash
# Create a new user
adduser yona

# Add user to the Docker group
usermod -aG docker yona

# Set up sudo
apt install -y sudo
usermod -aG sudo yona

# Switch to the new user
su - yona
```

### 3.2 Set Up the Application Directory

```bash
# Create application directory
mkdir -p ~/yona
cd ~/yona
```

### 3.3 Transfer Files to the Server

You have several options:

#### Option 1: Using SCP

From your local machine:

```bash
scp -r ./* yona@your-linode-ip:~/yona/
```

#### Option 2: Using Git (if your code is in a repository)

On the Linode server:

```bash
git clone https://your-repository-url.git ~/yona
cd ~/yona
```

### 3.4 Set Up Environment Variables

The .env file contains sensitive information like API keys and should be handled securely.

**Important**: The .env file is excluded from the Docker image via .dockerignore for security reasons.

Create the .env file on the server:

```bash
nano ~/yona/.env
```

Add your environment variables:

```
# YouTube API Credentials
YOUTUBE_API_KEY=your_youtube_api_key
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret

# MusicAPI/Suno API Key
MUSICAPI_KEY=your_musicapi_key

# OpenAI API Key
OPENAI_KEY=your_openai_key

# Supabase Credentials
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

Save the file (Ctrl+O, then Enter, then Ctrl+X).

Alternatively, you can securely transfer your existing .env file:

```bash
scp .env yona@your-linode-ip:~/yona/
```

### 3.5 Create a Logs Directory

```bash
mkdir -p ~/yona/logs
```

### 3.6 Build and Start the Containers

```bash
cd ~/yona
docker-compose build
docker-compose up -d
```

### 3.7 Verify the Deployment

```bash
# Check if containers are running
docker-compose ps

# Check the logs
docker-compose logs -f
```

## 4. Setting Up a Reverse Proxy (Nginx)

If you want to expose your application using a domain name, you can set up Nginx as a reverse proxy.

### 4.1 Install Nginx

```bash
sudo apt install -y nginx
```

### 4.2 Configure Nginx

Create a new Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/yona
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the configuration:

```bash
sudo ln -s /etc/nginx/sites-available/yona /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4.3 Set Up SSL with Let's Encrypt (Optional)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 5. Monitoring and Maintenance

### 5.1 Set Up Automatic Updates

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 5.2 Set Up Log Rotation

Create a logrotate configuration:

```bash
sudo nano /etc/logrotate.d/yona
```

Add the following:

```
/home/yona/yona/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 yona yona
}
```

### 5.3 Monitoring with Docker Stats

```bash
# View container resource usage
docker stats
```

### 5.4 Backup Strategy

#### Database Backups

Since you're using Supabase, make sure you have a backup strategy for your Supabase data.

#### Configuration Backups

Regularly backup your .env file and any other configuration files:

```bash
# Create a backup directory
mkdir -p ~/backups

# Backup the .env file
cp ~/yona/.env ~/backups/env-backup-$(date +%Y%m%d)
```

## 6. Updating the Application

When you need to update the application:

```bash
# Pull the latest code (if using Git)
cd ~/yona
git pull

# Or transfer the updated files using SCP

# Rebuild and restart the containers
docker-compose down
docker-compose build
docker-compose up -d
```

## 7. Troubleshooting

### 7.1 Checking Logs

```bash
# View logs for all services
docker-compose logs

# View logs for a specific service
docker-compose logs yona-api
docker-compose logs yona-feedback-processor

# Follow logs in real-time
docker-compose logs -f
```

### 7.2 Restarting Services

```bash
# Restart all services
docker-compose restart

# Restart a specific service
docker-compose restart yona-api
```

### 7.3 Checking Container Status

```bash
docker-compose ps
```

## 8. Security Considerations

- Keep your system and Docker updated
- Use strong passwords
- Consider setting up a firewall (UFW)
- Regularly review logs for suspicious activity
- Use SSL for all public-facing services
