import configparser
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_route53 as route53,
    aws_route53_targets as route53_targets,
    aws_certificatemanager as acm,
)
from constructs import Construct

class RecipeGenieStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Read configuration
        config = configparser.ConfigParser()
        config.read('config.ini')

        aws_config = config['aws']
        domain_name = aws_config['domain_name']
        certificate_arn = aws_config['certificate_arn']

        # S3 bucket for static assets
        site_bucket = s3.Bucket(
            self, "SiteBucket",
            bucket_name=domain_name,
            website_index_document="index.html",
            public_read_access=True,
        )

        # Deploy static assets to S3
        s3_deployment.BucketDeployment(
            self, "DeployWebsite",
            sources=[s3_deployment.Source.asset("../static")],
            destination_bucket=site_bucket,
        )

        # Lambda function for the Flask app
        flask_lambda = _lambda.Function(
            self, "FlaskLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="app.handler",
            code=_lambda.Code.from_asset("../lambda.zip")
        )

        # API Gateway
        api = apigw.LambdaRestApi(
            self, "Endpoint",
            handler=flask_lambda,
            proxy=True,
        )

        # Route 53
        hosted_zone = route53.HostedZone.from_lookup(
            self, "HostedZone",
            domain_name=domain_name.split(".", 1)[-1] # get the root domain
        )

        # Certificate
        certificate = acm.Certificate.from_certificate_arn(
            self, "Certificate",
            certificate_arn=certificate_arn,
        )

        # DNS record
        route53.ARecord(
            self, "AliasRecord",
            zone=hosted_zone,
            record_name=domain_name,
            target=route53.RecordTarget.from_alias(
                route53_targets.ApiGateway(api)
            ),
        )
