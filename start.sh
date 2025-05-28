#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 CTF Self-Instance Runner Setup${NC}"
echo "================================="
echo ""

# Check if Docker is installed
echo -e "${BLUE}🔍 Checking requirements...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose are installed${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Creating .env file from template...${NC}"
    cp .env.example .env
    
    echo ""
    echo -e "${BLUE}🔧 Configuration Setup${NC}"
    echo "Please configure your CTF instance settings (press Enter for defaults):"
    echo ""
    
    # Domain configuration
    read -p "Enter your server domain/IP (default: http://localhost): " domain
    if [ ! -z "$domain" ]; then
        sed -i.bak "s|DOMAIN=http://localhost|DOMAIN=$domain|g" .env
        rm .env.bak 2>/dev/null || true
    fi
    
    # Challenge title configuration  
    read -p "Enter challenge title (default: my ctf chall): " chall_title
    if [ ! -z "$chall_title" ]; then
        sed -i.bak "s|CHALL_TITLE=my ctf chall|CHALL_TITLE=$chall_title|g" .env
        rm .env.bak 2>/dev/null || true
    fi
    
    # Runner external port
    read -p "Enter runner port (default: 3000): " runner_port
    if [ ! -z "$runner_port" ]; then
        sed -i.bak "s|RUNNER_PORT=3000|RUNNER_PORT=$runner_port|g" .env
        rm .env.bak 2>/dev/null || true
    fi
    
    # Port range configuration
    read -p "Enter challenge port range start (default: 5000): " chall_port_range_start
    if [ ! -z "$chall_port_range_start" ]; then
        sed -i.bak "s|CHALL_PORT_RANGE_START=5000|CHALL_PORT_RANGE_START=$chall_port_range_start|g" .env
        rm .env.bak 2>/dev/null || true
    fi
    
    read -p "Enter challenge port range end (default: 6000): " chall_port_range_end
    if [ ! -z "$chall_port_range_end" ]; then
        sed -i.bak "s|CHALL_PORT_RANGE_END=6000|CHALL_PORT_RANGE_END=$chall_port_range_end|g" .env
        rm .env.bak 2>/dev/null || true
    fi
    
    # Duration configuration
    echo ""
    echo "Instance duration options:"
    echo "  1) 5 minutes (300000ms)"
    echo "  2) 15 minutes (900000ms) [default]"
    echo "  3) 30 minutes (1800000ms)"
    echo "  4) 1 hour (3600000ms)"
    echo "  5) Custom duration"
    
    read -p "Select duration option (1-5, default: 2): " duration_option
    case $duration_option in
        1)
            sed -i.bak "s|DURATION=900000|DURATION=300000|g" .env
            rm .env.bak 2>/dev/null || true
            ;;
        3)
            sed -i.bak "s|DURATION=900000|DURATION=1800000|g" .env
            rm .env.bak 2>/dev/null || true
            ;;
        4)
            sed -i.bak "s|DURATION=900000|DURATION=3600000|g" .env
            rm .env.bak 2>/dev/null || true
            ;;
        5)
            read -p "Enter custom duration in milliseconds: " custom_duration
            if [ ! -z "$custom_duration" ]; then
                sed -i.bak "s|DURATION=900000|DURATION=$custom_duration|g" .env
                rm .env.bak 2>/dev/null || true
            fi
            ;;
    esac
    
    echo ""
    echo -e "${GREEN}✅ .env file configured${NC}"
else
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
fi

# Make scripts executable
echo -e "${YELLOW}🔧 Making scripts executable...${NC}"
chmod +x chall/start.sh chall/stop.sh 2>/dev/null || true

# Build and start the application
echo -e "${YELLOW}🚀 Starting the application...${NC}"
docker-compose up --build -d