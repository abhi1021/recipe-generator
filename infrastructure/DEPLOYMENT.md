# Recipe Generator Deployment Guide

This guide explains how to deploy the Recipe Generator application to AWS using CDK and GitHub Actions.

## Architecture

The application is deployed with the following AWS services:

- **AWS Lambda**: Runs the Flask application
- **API Gateway HTTP API**: Handles incoming requests
- **CloudFront**: CDN for global distribution
- **Route53**: DNS management
- **WAF**: Web Application Firewall for security
- **Secrets Manager**: Secure storage of API keys
- **CloudWatch**: Monitoring and logging

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **Domain name** managed by Route53
3. **SSL Certificate** in ACM (us-east-1 region for CloudFront)
4. **Google API Key** for Gemini AI
5. **AWS CLI** configured locally
6. **Node.js** and **Python 3.11+** installed

## Configuration

### 1. Update deployment.properties

Copy and modify the `deployment.properties` file with your specific values:

```bash
# Required changes:
AWS_ACCOUNT_ID=your-aws-account-id
DOMAIN_NAME=yourdomain.com
SUBDOMAIN=recipe
CERTIFICATE_ARN=arn:aws:acm:us-east-1:account:certificate/cert-id
GOOGLE_API_KEY=your-google-api-key
FLASK_SECRET=your-secure-random-string
```

### 2. GitHub Secrets (for GitHub Actions deployment)

Configure the following secrets in your GitHub repository:

**Required Secrets:**
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key  
- `AWS_ACCOUNT_ID`: Your AWS account ID
- `DOMAIN_NAME`: Your domain (e.g., example.com)
- `SUBDOMAIN`: Subdomain for production (e.g., recipe)
- `CERTIFICATE_ARN`: ACM certificate ARN
- `GOOGLE_API_KEY`: Google Gemini API key
- `FLASK_SECRET`: Flask session secret

**Development Secrets (optional):**
- `DEV_DOMAIN_NAME`: Development domain
- `DEV_CERTIFICATE_ARN`: Development certificate ARN

## Deployment Methods

### Option 1: Manual Deployment

1. **Install dependencies:**
```bash
# Install CDK
npm install -g aws-cdk@latest

# Install Python dependencies
cd infrastructure
pip install -r requirements.txt
```

2. **Build the application:**
```bash
./build.sh
```

3. **Deploy with CDK:**
```bash
cd infrastructure
cdk bootstrap  # Only needed once per account/region
cdk deploy
```

### Option 2: GitHub Actions (Recommended)

GitHub Actions will automatically deploy when you push to:
- `develop` branch → Development environment
- `main` branch → Production environment

**Workflow includes:**
1. Run tests
2. Build application package
3. Deploy infrastructure
4. Update Lambda function
5. Run post-deployment verification

## Build Script Features

The `build.sh` script provides several options:

```bash
# Full build (default)
./build.sh

# Clean previous builds
./build.sh clean

# Install dependencies only
./build.sh deps

# Validate build
./build.sh validate
```

**Build process includes:**
- Python dependency installation
- Static file optimization (CSS/JS minification)
- Lambda package creation
- Build validation

## Infrastructure Components

### Lambda Function
- **Runtime**: Python 3.11
- **Memory**: Configurable (512MB default)
- **Timeout**: 30 seconds
- **Environment**: Retrieves secrets from Secrets Manager

### API Gateway HTTP API
- **Type**: HTTP API (lower latency than REST API)
- **CORS**: Configured for web browsers
- **Integration**: Lambda proxy integration

### CloudFront Distribution
- **Origin**: API Gateway
- **SSL**: Custom certificate
- **Caching**: Disabled for dynamic content
- **Compression**: Enabled

### WAF Web ACL
- **Rate limiting**: 2000 requests per 5 minutes per IP
- **AWS Managed Rules**: Core rule set protection
- **Scope**: CloudFront (global)

### Route53
- **Record type**: A record (alias to CloudFront)
- **TTL**: 5 minutes

## Monitoring

### CloudWatch Metrics
- Lambda function metrics
- API Gateway metrics  
- CloudFront metrics
- WAF metrics

### Log Groups
- Lambda function logs: `/aws/lambda/{project-name}`
- Retention: Configurable (14 days default)

## Security

### Secrets Management
- API keys stored in AWS Secrets Manager
- Lambda retrieves secrets at runtime
- No secrets in code or environment variables

### WAF Protection
- Rate limiting per IP
- AWS managed rule sets
- Custom rules configurable

### HTTPS Enforcement
- CloudFront redirects HTTP to HTTPS
- Security headers can be added via Lambda@Edge

## Cost Optimization

### Lambda
- Pay per request and compute time
- Memory allocation affects cost
- Cold starts minimized with provisioned concurrency (if needed)

### CloudFront
- Free tier: 1TB data transfer, 10M requests/month
- Price class 100 (North America, Europe) for cost savings

### API Gateway
- HTTP API cheaper than REST API
- Pay per request

## Troubleshooting

### Common Issues

1. **Certificate not found**
   - Ensure certificate is in us-east-1 region
   - Verify certificate ARN is correct

2. **Domain validation failed**
   - Check Route53 hosted zone exists
   - Verify domain ownership

3. **Lambda timeout**
   - Increase timeout in deployment.properties
   - Check function logs in CloudWatch

4. **Build failures**
   - Ensure Python 3.11+ is installed
   - Check dependencies in pyproject.toml

### Useful Commands

```bash
# View CDK diff before deploy
cd infrastructure
cdk diff

# Destroy infrastructure (careful!)
cdk destroy

# View CloudFormation events
aws cloudformation describe-stack-events --stack-name recipe-generator-stack

# Test Lambda function locally
aws lambda invoke --function-name recipe-generator-function response.json
```

## Production Checklist

Before deploying to production:

- [ ] Update all secrets in deployment.properties
- [ ] Test build script locally
- [ ] Verify certificate is valid and in us-east-1
- [ ] Configure GitHub secrets
- [ ] Test deployment in development environment
- [ ] Set up monitoring alerts
- [ ] Configure backup strategy
- [ ] Review WAF rules
- [ ] Test application functionality
- [ ] Monitor costs after deployment

## Support

For issues with deployment:

1. Check CloudFormation stack events
2. Review Lambda function logs
3. Verify all configuration values
4. Test components individually
5. Consult AWS documentation

## Updates and Maintenance

### Application Updates
- Push to appropriate branch (develop/main)
- GitHub Actions will handle deployment

### Infrastructure Updates
- Modify CDK code in `infrastructure/stacks/`
- Test with `cdk diff` before deployment
- Deploy with `cdk deploy`

### Dependency Updates
- Update `pyproject.toml` or `requirements.txt`
- Rebuild and redeploy

Remember to monitor costs and performance after deployment!