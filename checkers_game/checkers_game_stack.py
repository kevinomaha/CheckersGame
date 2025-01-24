from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3_deployment as s3deploy,
    RemovalPolicy,
    CfnOutput,
    Duration,
    Tags,
    aws_iam as iam
)
from constructs import Construct
from .config import Environment
import time

class CheckersGameStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, env_config: Environment, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Add environment tag to all resources
        Tags.of(self).add('Environment', env_config.name)

        # Generate a unique bucket name using timestamp
        timestamp = str(int(time.time()))
        bucket_name = f"checkers-game-{env_config.name}-{timestamp}".lower()

        # S3 bucket for website hosting
        website_bucket = s3.Bucket(self, "WebsiteBucket",
            bucket_name=bucket_name,
            website_index_document="index.html",
            website_error_document="index.html",
            public_read_access=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
            )
        )

        # DynamoDB tables with simplified configuration
        game_table = dynamodb.Table(self, "GameTable",
            partition_key=dynamodb.Attribute(
                name="gameId",
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        stats_table = dynamodb.Table(self, "StatsTable",
            partition_key=dynamodb.Attribute(
                name="playerId",
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        # Lambda function with basic execution role
        lambda_role = iam.Role(self, "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        # Add DynamoDB permissions to Lambda role
        game_table.grant_read_write_data(lambda_role)
        stats_table.grant_read_write_data(lambda_role)

        game_lambda = lambda_.Function(self, "CheckersGameFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="game.handler",
            code=lambda_.Code.from_asset("lambda"),
            environment={
                "GAME_TABLE": game_table.table_name,
                "STATS_TABLE": stats_table.table_name
            },
            memory_size=256,
            timeout=Duration.seconds(30),
            role=lambda_role
        )

        # API Gateway with simplified configuration
        api = apigateway.RestApi(self, "CheckersApi",
            rest_api_name="Checkers Game API",
            deploy_options=apigateway.StageOptions(stage_name=env_config.name)
        )

        game_integration = apigateway.LambdaIntegration(game_lambda)
        api.root.add_method("ANY", game_integration)
        api.root.add_proxy(default_integration=game_integration)

        # CloudFront distribution with simplified configuration
        distribution = cloudfront.Distribution(self, "CheckersDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin(website_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                cache_policy=cloudfront.CachePolicy.CACHING_DISABLED
            ),
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html"
                ),
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html"
                )
            ]
        )

        # Deploy frontend to S3
        s3deploy.BucketDeployment(self, "DeployWebsite",
            sources=[s3deploy.Source.asset("frontend/build")],
            destination_bucket=website_bucket,
            distribution=distribution,
            distribution_paths=["/*"],
            memory_limit=1024,
            retain_on_delete=False,
            prune=True
        )

        # Output the CloudFront URL and API Gateway URL
        CfnOutput(self, "CloudFrontURL",
            value=f"https://{distribution.distribution_domain_name}"
        )
        
        CfnOutput(self, "APIGatewayURL",
            value=api.url
        )
