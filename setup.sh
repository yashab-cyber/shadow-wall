#!/bin/bash

# ShadowWall AI Setup Script
# Automated setup for development and deployment environments

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PYTHON_MIN_VERSION="3.8"
PROJECT_NAME="ShadowWall AI"
VENV_NAME="shadowwall-env"

# Functions
print_banner() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                        ShadowWall AI                          ║"
    echo "║                      Setup & Installation                     ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_python() {
    log_info "Checking Python version..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    REQUIRED_VERSION=$(echo -e "$PYTHON_VERSION\n$PYTHON_MIN_VERSION" | sort -V | head -n1)
    
    if [[ "$REQUIRED_VERSION" != "$PYTHON_MIN_VERSION" ]]; then
        log_error "Python $PYTHON_MIN_VERSION or higher is required. Found: $PYTHON_VERSION"
        exit 1
    fi
    
    log_info "Python $PYTHON_VERSION is available ✓"
}

check_system_dependencies() {
    log_info "Checking system dependencies..."
    
    # Check for package manager
    if command -v apt &> /dev/null; then
        PACKAGE_MANAGER="apt"
        UPDATE_CMD="apt update"
        INSTALL_CMD="apt install -y"
    elif command -v yum &> /dev/null; then
        PACKAGE_MANAGER="yum"
        UPDATE_CMD="yum update -y"
        INSTALL_CMD="yum install -y"
    elif command -v dnf &> /dev/null; then
        PACKAGE_MANAGER="dnf"
        UPDATE_CMD="dnf update -y"
        INSTALL_CMD="dnf install -y"
    else
        log_warning "Package manager not detected. Manual dependency installation may be required."
        return
    fi
    
    # Required system packages
    REQUIRED_PACKAGES=(
        "python3-dev"
        "python3-pip" 
        "python3-venv"
        "libpcap-dev"
        "build-essential"
        "curl"
        "git"
    )
    
    # Additional packages for different distributions
    if [[ "$PACKAGE_MANAGER" == "apt" ]]; then
        REQUIRED_PACKAGES+=("python3-distutils")
    fi
    
    # Check if running as root for system package installation
    if [[ $EUID -ne 0 ]] && [[ "$1" != "--skip-system" ]]; then
        log_warning "Root privileges required for system package installation"
        log_info "Re-run with sudo or use --skip-system flag"
        exit 1
    fi
    
    # Install missing packages
    MISSING_PACKAGES=()
    for package in "${REQUIRED_PACKAGES[@]}"; do
        if ! dpkg -l | grep -q "^ii  $package " 2>/dev/null && \
           ! rpm -q "$package" &>/dev/null && \
           ! command -v "$package" &>/dev/null; then
            MISSING_PACKAGES+=("$package")
        fi
    done
    
    if [[ ${#MISSING_PACKAGES[@]} -gt 0 ]]; then
        log_info "Installing missing system packages: ${MISSING_PACKAGES[*]}"
        $UPDATE_CMD
        $INSTALL_CMD "${MISSING_PACKAGES[@]}"
    else
        log_info "All system dependencies are available ✓"
    fi
}

check_docker() {
    log_info "Checking Docker availability..."
    
    if command -v docker &> /dev/null; then
        if docker info &> /dev/null; then
            log_info "Docker is available and running ✓"
            return 0
        else
            log_warning "Docker is installed but not running"
            log_info "Start Docker service: sudo systemctl start docker"
            return 1
        fi
    else
        log_warning "Docker is not installed"
        log_info "Install Docker: https://docs.docker.com/engine/install/"
        return 1
    fi
}

setup_virtual_environment() {
    log_info "Setting up Python virtual environment..."
    
    if [[ -d "$VENV_NAME" ]]; then
        log_warning "Virtual environment already exists. Removing..."
        rm -rf "$VENV_NAME"
    fi
    
    python3 -m venv "$VENV_NAME"
    source "$VENV_NAME/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    log_info "Virtual environment created: $VENV_NAME ✓"
}

install_python_dependencies() {
    log_info "Installing Python dependencies..."
    
    # Ensure we're in the virtual environment
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        log_warning "Virtual environment not activated. Activating..."
        source "$VENV_NAME/bin/activate"
    fi
    
    # Install from requirements.txt
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        log_info "Python dependencies installed ✓"
    else
        log_error "requirements.txt not found"
        exit 1
    fi
}

setup_configuration() {
    log_info "Setting up configuration..."
    
    # Create config directory
    mkdir -p config
    
    # Copy example configuration if main config doesn't exist
    if [[ ! -f "config/config.yaml" ]]; then
        if [[ -f "config/config.example.yaml" ]]; then
            cp "config/config.example.yaml" "config/config.yaml"
            log_info "Created config/config.yaml from example"
        else
            log_warning "No example configuration found"
        fi
    fi
    
    # Create additional directories
    mkdir -p logs data/{models,honeypots,captures,reports} temp
    
    log_info "Configuration setup completed ✓"
}

setup_docker_environment() {
    log_info "Setting up Docker environment..."
    
    if check_docker; then
        # Build Docker image
        if [[ -f "Dockerfile" ]]; then
            docker build -t shadowwall-ai .
            log_info "Docker image built ✓"
        fi
        
        # Check docker-compose
        if command -v docker-compose &> /dev/null || command -v docker compose &> /dev/null; then
            log_info "Docker Compose is available ✓"
        else
            log_warning "Docker Compose not found"
        fi
    else
        log_warning "Skipping Docker setup - Docker not available"
    fi
}

run_tests() {
    log_info "Running basic tests..."
    
    # Ensure we're in the virtual environment
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        source "$VENV_NAME/bin/activate"
    fi
    
    # Test Python imports
    python3 -c "
import sys
try:
    import fastapi, uvicorn, sqlalchemy, scapy, sklearn
    print('✓ All core dependencies can be imported')
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
    "
    
    # Test configuration loading
    python3 -c "
try:
    from src.core.config.settings import load_config
    config = load_config('config/config.yaml')
    print('✓ Configuration can be loaded')
except Exception as e:
    print(f'✗ Configuration error: {e}')
    "
    
    log_info "Basic tests completed ✓"
}

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help              Show this help message"
    echo "  --skip-system       Skip system package installation"
    echo "  --skip-docker       Skip Docker setup"
    echo "  --skip-tests        Skip running tests"
    echo "  --development       Setup for development (include dev dependencies)"
    echo ""
    echo "Examples:"
    echo "  $0                  # Full setup"
    echo "  $0 --skip-system    # Skip system packages (if already installed)"
    echo "  $0 --development    # Setup for development"
}

main() {
    print_banner
    
    # Parse command line arguments
    SKIP_SYSTEM=false
    SKIP_DOCKER=false
    SKIP_TESTS=false
    DEVELOPMENT=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help)
                show_usage
                exit 0
                ;;
            --skip-system)
                SKIP_SYSTEM=true
                shift
                ;;
            --skip-docker)
                SKIP_DOCKER=true
                shift
                ;;
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --development)
                DEVELOPMENT=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    log_info "Starting $PROJECT_NAME setup..."
    
    # Core setup steps
    check_python
    
    if [[ "$SKIP_SYSTEM" != true ]]; then
        check_system_dependencies
    fi
    
    setup_virtual_environment
    install_python_dependencies
    setup_configuration
    
    if [[ "$SKIP_DOCKER" != true ]]; then
        setup_docker_environment
    fi
    
    if [[ "$SKIP_TESTS" != true ]]; then
        run_tests
    fi
    
    # Show completion message
    echo ""
    log_info "Setup completed successfully! 🎉"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Activate virtual environment: source $VENV_NAME/bin/activate"
    echo "2. Review configuration: config/config.yaml"
    echo "3. Start ShadowWall AI: python init.py"
    echo ""
    echo -e "${BLUE}Alternative start methods:${NC}"
    echo "• Development mode: python init.py --debug"
    echo "• Simulation mode: python init.py --simulate"
    echo "• Docker: docker-compose up"
    echo ""
    log_info "For help: python init.py --help"
}

# Run main function
main "$@"
