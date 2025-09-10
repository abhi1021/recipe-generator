#!/usr/bin/env python3
import os
import configparser
import aws_cdk as cdk
from stacks.recipe_generator_stack import RecipeGeneratorStack

def load_config():
    config = configparser.ConfigParser()
    
    # Load from deployment.properties file
    properties_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'deployment.properties')
    
    if not os.path.exists(properties_file):
        raise FileNotFoundError(f"Configuration file not found: {properties_file}")
    
    # Read the properties file manually since ConfigParser expects sections
    config_dict = {}
    with open(properties_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config_dict[key.strip()] = value.strip()
    
    return config_dict

def main():
    config = load_config()
    
    app = cdk.App()
    
    # Environment configuration
    env = cdk.Environment(
        account=config.get('AWS_ACCOUNT_ID'),
        region=config.get('AWS_REGION', 'us-east-1')
    )
    
    # Create the main stack
    RecipeGeneratorStack(
        app, 
        f"{config.get('PROJECT_NAME', 'recipe-generator')}-stack",
        config=config,
        env=env,
        description="Recipe Generator Application Infrastructure"
    )
    
    app.synth()

if __name__ == "__main__":
    main()