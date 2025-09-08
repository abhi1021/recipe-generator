#!/bin/bash
set -e

# Create a build directory
rm -rf build lambda.zip
mkdir -p build

# Install dependencies into the build directory
pip install -r requirements.txt -t build/

# Copy application code into the build directory
cp app.py build/
cp auth_service.py build/
cp recipe_service.py build/

# Create a zip file for the Lambda function
cd build
zip -r ../lambda.zip .
cd ..

echo "Lambda package created at lambda.zip"

# The static assets will be deployed by the CDK directly from the `static` folder.
# No need to copy them in this script.
echo "Build successful"
