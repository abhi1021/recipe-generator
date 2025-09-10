#!/bin/bash

# Recipe Generator Build Script
# This script builds the application for AWS Lambda deployment

set -e  # Exit on any error

echo "🏗️  Starting Recipe Generator build process..."

# Configuration
BUILD_DIR="recipe-gen-build"
LAMBDA_ZIP="lambda.zip"
PYTHON_VERSION="3.11"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_step() {
    echo -e "${BLUE}📦 $1${NC}"
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

# Check if required commands exist
check_requirements() {
    print_step "Checking build requirements..."
    
    commands=("python3" "pip3" "zip")
    for cmd in "${commands[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            print_error "$cmd is required but not installed."
            exit 1
        fi
    done
    
    print_success "All requirements satisfied"
}

# Clean previous builds
clean_build() {
    print_step "Cleaning previous builds..."
    
    if [ -d "$BUILD_DIR" ]; then
        rm -rf "$BUILD_DIR"
        print_success "Removed $BUILD_DIR directory"
    fi
    
    if [ -f "$LAMBDA_ZIP" ]; then
        rm -f "$LAMBDA_ZIP"
        print_success "Removed $LAMBDA_ZIP"
    fi
}

# Create build directory
create_build_dir() {
    print_step "Creating build directory..."
    mkdir -p "$BUILD_DIR"
    print_success "Created $BUILD_DIR directory"
}

# Install Python dependencies
install_python_dependencies() {
    print_step "Installing Python dependencies..."
    
    # Check if virtual environment should be used
    if [ -d ".venv" ]; then
        print_warning "Using existing virtual environment"
        source .venv/bin/activate
    elif [ -d "env" ]; then
        print_warning "Using existing env directory"
        source env/bin/activate
    else
        print_warning "No virtual environment found, using system Python"
    fi
    
    # Install dependencies to build directory
    if [ -f "pyproject.toml" ]; then
        print_step "Installing from pyproject.toml..."
        pip3 install -t "$BUILD_DIR" -r <(python3 -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    data = tomllib.load(f)
    for dep in data.get('project', {}).get('dependencies', []):
        print(dep)
")
    elif [ -f "requirements.txt" ]; then
        print_step "Installing from requirements.txt..."
        pip3 install -t "$BUILD_DIR" -r requirements.txt
    else
        print_step "Installing Flask and dependencies manually..."
        pip3 install -t "$BUILD_DIR" Flask python-dotenv google-generativeai
    fi
    
    print_success "Python dependencies installed"
}

# Copy application files
copy_application_files() {
    print_step "Copying application files..."
    
    # Copy Python files
    cp *.py "$BUILD_DIR/" 2>/dev/null || print_warning "No Python files found in root"
    
    # Copy templates directory
    if [ -d "templates" ]; then
        cp -r templates "$BUILD_DIR/"
        print_success "Copied templates directory"
    fi
    
    # Copy static files
    if [ -d "static" ]; then
        cp -r static "$BUILD_DIR/"
        print_success "Copied static directory"
    fi
    
    # Copy instance directory if it exists
    if [ -d "instance" ]; then
        cp -r instance "$BUILD_DIR/"
        print_success "Copied instance directory"
    fi
    
    # Copy .env file if it exists (for local testing)
    if [ -f ".env" ]; then
        cp .env "$BUILD_DIR/"
        print_success "Copied .env file"
    fi
    
    print_success "Application files copied"
}

# Process static files
process_static_files() {
    print_step "Processing static files..."
    
    if [ -d "static" ]; then
        # Minify CSS files if available
        if command -v csso &> /dev/null; then
            find "$BUILD_DIR/static" -name "*.css" -exec csso {} --output {} \;
            print_success "CSS files minified"
        else
            print_warning "csso not found, skipping CSS minification"
        fi
        
        # Minify JS files if available
        if command -v terser &> /dev/null; then
            find "$BUILD_DIR/static" -name "*.js" -exec terser {} --output {} --compress --mangle \;
            print_success "JavaScript files minified"
        else
            print_warning "terser not found, skipping JS minification"
        fi
    fi
}

# Clean up build directory
cleanup_build_dir() {
    print_step "Cleaning up build directory..."
    
    # Remove unnecessary files
    find "$BUILD_DIR" -name "*.pyc" -delete
    find "$BUILD_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$BUILD_DIR" -name "*.dist-info" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$BUILD_DIR" -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$BUILD_DIR" -name ".DS_Store" -delete 2>/dev/null || true
    find "$BUILD_DIR" -name "*.so" -type f | head -20  # Keep only first 20 .so files to reduce size
    
    # Remove test directories
    find "$BUILD_DIR" -name "tests" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$BUILD_DIR" -name "test" -type d -exec rm -rf {} + 2>/dev/null || true
    
    print_success "Build directory cleaned"
}

# Create Lambda deployment package
create_lambda_zip() {
    print_step "Creating Lambda deployment package..."
    
    cd "$BUILD_DIR"
    zip -r "../$LAMBDA_ZIP" . -x "*.pyc" "__pycache__/*" "*.dist-info/*" "*.egg-info/*"
    cd ..
    
    # Get zip file size
    size=$(stat -f%z "$LAMBDA_ZIP" 2>/dev/null || stat -c%s "$LAMBDA_ZIP" 2>/dev/null || echo "unknown")
    size_mb=$((size / 1024 / 1024))
    
    print_success "Lambda package created: $LAMBDA_ZIP (${size_mb}MB)"
    
    # Warn if package is too large
    if [ "$size_mb" -gt 50 ]; then
        print_warning "Package size is ${size_mb}MB. Consider optimizing to stay under Lambda limits."
    fi
}

# Validate the build
validate_build() {
    print_step "Validating build..."
    
    # Check if required files exist in the zip
    required_files=("lambda_handler.py" "app.py")
    for file in "${required_files[@]}"; do
        if unzip -l "$LAMBDA_ZIP" | grep -q "$file"; then
            print_success "$file found in package"
        else
            print_error "$file missing from package"
            exit 1
        fi
    done
    
    print_success "Build validation passed"
}

# Main build process
main() {
    echo "🚀 Recipe Generator Build Script"
    echo "================================"
    
    check_requirements
    clean_build
    create_build_dir
    install_python_dependencies
    copy_application_files
    process_static_files
    cleanup_build_dir
    create_lambda_zip
    validate_build
    
    echo ""
    echo -e "${GREEN}🎉 Build completed successfully!${NC}"
    echo -e "${BLUE}📦 Lambda package: $LAMBDA_ZIP${NC}"
    echo -e "${YELLOW}💡 Next steps:${NC}"
    echo "   1. Update deployment.properties with your AWS configuration"
    echo "   2. Run: cd infrastructure && cdk deploy"
    echo "   3. Or use GitHub Actions for automated deployment"
    echo ""
}

# Handle script arguments
case "${1:-}" in
    "clean")
        clean_build
        print_success "Clean completed"
        ;;
    "deps")
        create_build_dir
        install_python_dependencies
        print_success "Dependencies installed"
        ;;
    "validate")
        validate_build
        ;;
    *)
        main
        ;;
esac