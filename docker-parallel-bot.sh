#!/bin/bash

# =============================================================================
# KAEL Parallel Trading Bot - Docker Management Script
# =============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

COMPOSE_FILE="docker-compose.parallel.yml"
CONTAINER_NAME="kael-parallel-trading-bot"

# Function to print colored messages
print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        print_error ".env file not found!"
        print_info "Please create a .env file with your IQ Option credentials."
        exit 1
    fi
}

# Function to build the image
build() {
    print_info "Building Docker image..."
    docker-compose -f ${COMPOSE_FILE} build --no-cache
    print_success "Build completed!"
}

# Function to start the bot
start() {
    print_info "Starting KAEL Parallel Trading Bot..."
    docker-compose -f ${COMPOSE_FILE} up -d
    print_success "Bot started!"
    print_info "View logs with: ./docker-parallel-bot.sh logs"
    print_info "Monitor with: ./monitor_parallel_bot.sh"
}

# Function to stop the bot
stop() {
    print_info "Stopping KAEL Parallel Trading Bot..."
    docker-compose -f ${COMPOSE_FILE} stop
    print_success "Bot stopped!"
}

# Function to restart the bot
restart() {
    print_info "Restarting KAEL Parallel Trading Bot..."
    docker-compose -f ${COMPOSE_FILE} restart
    print_success "Bot restarted!"
}

# Function to view logs
logs() {
    print_info "Showing logs (Ctrl+C to exit)..."
    docker-compose -f ${COMPOSE_FILE} logs -f
}

# Function to view status
status() {
    print_info "Container Status:"
    docker-compose -f ${COMPOSE_FILE} ps
    echo ""
    
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_info "Bot Statistics:"
        curl -s http://localhost:5001/statistics | python3 -m json.tool 2>/dev/null || print_warning "API not responding yet"
    else
        print_warning "Container is not running"
    fi
}

# Function to remove everything
clean() {
    print_warning "This will remove the container and image. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_info "Cleaning up..."
        docker-compose -f ${COMPOSE_FILE} down -v
        docker rmi $(docker images -q kael-parallel-trading-bot) 2>/dev/null || true
        print_success "Cleanup completed!"
    else
        print_info "Cleanup cancelled"
    fi
}

# Function to show help
show_help() {
    echo "=========================================================================="
    echo -e "  ${CYAN}🤖 KAEL Parallel Trading Bot - Docker Manager${NC}"
    echo "=========================================================================="
    echo ""
    echo "Usage: ./docker-parallel-bot.sh [command]"
    echo ""
    echo "Commands:"
    echo "  build      Build the Docker image"
    echo "  start      Start the bot"
    echo "  stop       Stop the bot"
    echo "  restart    Restart the bot"
    echo "  logs       View bot logs (live)"
    echo "  status     Show bot status and statistics"
    echo "  clean      Remove container and image"
    echo "  monitor    Start the monitoring dashboard"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./docker-parallel-bot.sh build"
    echo "  ./docker-parallel-bot.sh start"
    echo "  ./docker-parallel-bot.sh logs"
    echo ""
    echo "=========================================================================="
}

# Main script
main() {
    check_docker
    
    case "${1:-help}" in
        build)
            check_env
            build
            ;;
        start)
            check_env
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        logs)
            logs
            ;;
        status)
            status
            ;;
        clean)
            clean
            ;;
        monitor)
            if [ -f monitor_parallel_bot.sh ]; then
                chmod +x monitor_parallel_bot.sh
                ./monitor_parallel_bot.sh
            else
                print_error "monitor_parallel_bot.sh not found!"
            fi
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
