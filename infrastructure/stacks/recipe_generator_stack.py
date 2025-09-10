import os
from typing import Dict, Any
from constructs import Construct
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as integrations,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_certificatemanager as acm,
    aws_wafv2 as wafv2,
    aws_secretsmanager as secretsmanager,
    aws_logs as logs,
    aws_iam as iam,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
)


class RecipeGeneratorStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: Dict[str, Any], **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.config = config
        
        # Create Secrets Manager secret for application secrets
        self.create_secrets()
        
        # Create Lambda function
        self.lambda_function = self.create_lambda_function()
        
        # Create API Gateway
        self.api_gateway = self.create_api_gateway()
        
        # Create CloudFront distribution
        self.cloudfront_distribution = self.create_cloudfront_distribution()
        
        # Create Route53 record
        self.create_route53_record()
        
        # Create WAF if enabled
        if self.config.get('ENABLE_WAF', 'true').lower() == 'true':
            self.create_waf()
    
    def create_secrets(self):
        """Create AWS Secrets Manager secret for application configuration"""
        secret_value = {
            'GOOGLE_API_KEY': self.config.get('GOOGLE_API_KEY', ''),
            'FLASK_SECRET': self.config.get('FLASK_SECRET', ''),
        }
        
        self.app_secrets = secretsmanager.Secret(
            self, "AppSecrets",
            secret_name=f"{self.config.get('PROJECT_NAME', 'recipe-generator')}-secrets",
            description="Application secrets for Recipe Generator",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{}',
                generate_string_key='placeholder'
            ),
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Update the secret with actual values
        self.app_secrets.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.ServicePrincipal('lambda.amazonaws.com')],
                actions=['secretsmanager:GetSecretValue'],
                resources=['*']
            )
        )
    
    def create_lambda_function(self):
        """Create the Lambda function for the Flask application"""
        
        # Create CloudWatch Log Group
        log_group = logs.LogGroup(
            self, "LambdaLogGroup",
            log_group_name=f"/aws/lambda/{self.config.get('PROJECT_NAME', 'recipe-generator')}",
            retention=logs.RetentionDays(int(self.config.get('LOG_RETENTION_DAYS', 14))),
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Create Lambda execution role
        lambda_role = iam.Role(
            self, "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        
        # Add permissions to read from Secrets Manager
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["secretsmanager:GetSecretValue"],
                resources=[self.app_secrets.secret_arn]
            )
        )
        
        # Create Lambda function
        lambda_function = _lambda.Function(
            self, "RecipeGeneratorFunction",
            function_name=f"{self.config.get('PROJECT_NAME', 'recipe-generator')}-function",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_handler.handler",
            code=_lambda.Code.from_asset("../lambda.zip"),
            timeout=Duration.seconds(int(self.config.get('LAMBDA_TIMEOUT', 30))),
            memory_size=int(self.config.get('LAMBDA_MEMORY_SIZE', 512)),
            role=lambda_role,
            log_group=log_group,
            environment={
                'SECRETS_NAME': self.app_secrets.secret_name,
                'AWS_REGION': self.config.get('AWS_REGION', 'us-east-1'),
                'ENVIRONMENT': self.config.get('ENVIRONMENT', 'production')
            }
        )
        
        return lambda_function
    
    def create_api_gateway(self):
        """Create API Gateway HTTP API"""
        api = apigwv2.HttpApi(
            self, "RecipeGeneratorAPI",
            api_name=f"{self.config.get('PROJECT_NAME', 'recipe-generator')}-api",
            description="Recipe Generator HTTP API",
            cors_preflight=apigwv2.CorsPreflightOptions(
                allow_credentials=True,
                allow_headers=["*"],
                allow_methods=[
                    apigwv2.CorsHttpMethod.GET,
                    apigwv2.CorsHttpMethod.POST,
                    apigwv2.CorsHttpMethod.PUT,
                    apigwv2.CorsHttpMethod.DELETE,
                    apigwv2.CorsHttpMethod.OPTIONS
                ],
                allow_origins=["*"],
                max_age=Duration.days(10)
            )
        )
        
        # Create Lambda integration
        lambda_integration = integrations.HttpLambdaIntegration(
            "LambdaIntegration",
            self.lambda_function
        )
        
        # Add catch-all route
        api.add_routes(
            path="/{proxy+}",
            methods=[apigwv2.HttpMethod.ANY],
            integration=lambda_integration
        )
        
        # Add root route
        api.add_routes(
            path="/",
            methods=[apigwv2.HttpMethod.ANY],
            integration=lambda_integration
        )
        
        # Output the API URL
        cdk.CfnOutput(
            self, "ApiUrl",
            value=api.url,
            description="API Gateway URL"
        )
        
        return api
    
    def create_cloudfront_distribution(self):
        """Create CloudFront distribution"""
        
        # Import existing certificate
        certificate = acm.Certificate.from_certificate_arn(
            self, "Certificate",
            certificate_arn=self.config.get('CERTIFICATE_ARN')
        )
        
        # Create CloudFront distribution
        distribution = cloudfront.Distribution(
            self, "CloudFrontDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.HttpOrigin(
                    f"{self.api_gateway.http_api_id}.execute-api.{self.config.get('AWS_REGION', 'us-east-1')}.amazonaws.com"
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                cached_methods=cloudfront.CachedMethods.CACHE_GET_HEAD_OPTIONS,
                cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER,
                compress=True
            ),
            domain_names=[self.config.get('FULL_DOMAIN')],
            certificate=certificate,
            minimum_protocol_version=cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,
            enabled=True,
            comment=f"CloudFront distribution for {self.config.get('PROJECT_NAME', 'recipe-generator')}",
            default_root_object="/"
        )
        
        # Output CloudFront URL
        cdk.CfnOutput(
            self, "CloudFrontUrl",
            value=f"https://{distribution.distribution_domain_name}",
            description="CloudFront Distribution URL"
        )
        
        return distribution
    
    def create_route53_record(self):
        """Create Route53 record pointing to CloudFront"""
        
        # Import existing hosted zone
        hosted_zone = route53.HostedZone.from_lookup(
            self, "HostedZone",
            domain_name=self.config.get('DOMAIN_NAME')
        )
        
        # Create A record pointing to CloudFront
        route53.ARecord(
            self, "AliasRecord",
            zone=hosted_zone,
            record_name=self.config.get('SUBDOMAIN'),
            target=route53.RecordTarget.from_alias(
                targets.CloudFrontTarget(self.cloudfront_distribution)
            ),
            ttl=Duration.minutes(5)
        )
        
        # Output the domain URL
        cdk.CfnOutput(
            self, "DomainUrl",
            value=f"https://{self.config.get('FULL_DOMAIN')}",
            description="Custom Domain URL"
        )
    
    def create_waf(self):
        """Create WAF Web ACL for CloudFront"""
        
        # Rate limiting rule
        rate_limit_rule = wafv2.CfnWebACL.RuleProperty(
            name="RateLimitRule",
            priority=1,
            statement=wafv2.CfnWebACL.StatementProperty(
                rate_based_statement=wafv2.CfnWebACL.RateBasedStatementProperty(
                    limit=int(self.config.get('RATE_LIMIT_PER_5MIN', 2000)),
                    aggregate_key_type="IP"
                )
            ),
            action=wafv2.CfnWebACL.ActionProperty(
                block={}
            ),
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                sampled_requests_enabled=True,
                cloud_watch_metrics_enabled=True,
                metric_name="RateLimitRule"
            )
        )
        
        # AWS Managed Core Rule Set
        aws_managed_rules = wafv2.CfnWebACL.RuleProperty(
            name="AWSManagedRulesCore",
            priority=2,
            override_action=wafv2.CfnWebACL.OverrideActionProperty(
                none={}
            ),
            statement=wafv2.CfnWebACL.StatementProperty(
                managed_rule_group_statement=wafv2.CfnWebACL.ManagedRuleGroupStatementProperty(
                    vendor_name="AWS",
                    name="AWSManagedRulesCommonRuleSet"
                )
            ),
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                sampled_requests_enabled=True,
                cloud_watch_metrics_enabled=True,
                metric_name="AWSManagedRulesCore"
            )
        )
        
        # Create WAF Web ACL
        web_acl = wafv2.CfnWebACL(
            self, "WebACL",
            scope="CLOUDFRONT",
            default_action=wafv2.CfnWebACL.ActionProperty(
                allow={}
            ),
            rules=[rate_limit_rule, aws_managed_rules],
            visibility_config=wafv2.CfnWebACL.VisibilityConfigProperty(
                sampled_requests_enabled=True,
                cloud_watch_metrics_enabled=True,
                metric_name=f"{self.config.get('PROJECT_NAME', 'recipe-generator')}-WebACL"
            ),
            name=f"{self.config.get('PROJECT_NAME', 'recipe-generator')}-WebACL",
            description="WAF Web ACL for Recipe Generator"
        )
        
        # Output WAF ARN
        cdk.CfnOutput(
            self, "WebACLArn",
            value=web_acl.attr_arn,
            description="WAF Web ACL ARN"
        )
        
        return web_acl