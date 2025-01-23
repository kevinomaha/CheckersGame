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
    Duration
)
from constructs import Construct

class CheckersGameStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 bucket for website hosting
        website_bucket = s3.Bucket(self, "WebsiteBucket",
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

        # CloudFront distribution
        distribution = cloudfront.Distribution(self, "CheckersDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(website_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                cache_policy=cloudfront.CachePolicy(self, "CheckersCachePolicy",
                    cache_policy_name="CheckersCachePolicy",
                    min_ttl=Duration.seconds(0),
                    default_ttl=Duration.seconds(0),
                    max_ttl=Duration.seconds(1),
                    enable_accept_encoding_brotli=True,
                    enable_accept_encoding_gzip=True,
                    comment="Cache policy for Checkers Game"
                )
            ),
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.seconds(0)
                ),
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.seconds(0)
                )
            ],
            enable_logging=True,
            price_class=cloudfront.PriceClass.PRICE_CLASS_100
        )

        # DynamoDB tables
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

        # Lambda function
        game_lambda = lambda_.Function(self, "CheckersGameFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="game.handler",
            code=lambda_.Code.from_asset("lambda"),
            environment={
                "GAME_TABLE": game_table.table_name,
                "STATS_TABLE": stats_table.table_name
            },
            memory_size=256,
            timeout=Duration.seconds(30)
        )

        # Grant Lambda permissions
        game_table.grant_read_write_data(game_lambda)
        stats_table.grant_read_write_data(game_lambda)

        # API Gateway
        api = apigateway.RestApi(self, "CheckersApi",
            rest_api_name="Checkers Game API",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=["*"],
                allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                allow_headers=["Content-Type", "Accept", "Authorization", "Origin", "X-Requested-With"],
                allow_credentials=True,
                max_age=Duration.days(1)
            )
        )

        # Add CORS response headers to all methods
        method_responses = [
            apigateway.MethodResponse(
                status_code="200",
                response_parameters={
                    'method.response.header.Access-Control-Allow-Origin': True,
                    'method.response.header.Access-Control-Allow-Headers': True,
                    'method.response.header.Access-Control-Allow-Methods': True,
                    'method.response.header.Access-Control-Allow-Credentials': True
                }
            )
        ]

        integration_responses = [
            apigateway.IntegrationResponse(
                status_code="200",
                response_parameters={
                    'method.response.header.Access-Control-Allow-Origin': "'*'",
                    'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                    'method.response.header.Access-Control-Allow-Methods': "'GET,POST,PUT,DELETE,OPTIONS'",
                    'method.response.header.Access-Control-Allow-Credentials': "'true'"
                }
            )
        ]

        # Lambda integration with CORS
        lambda_integration = apigateway.LambdaIntegration(
            game_lambda,
            proxy=True,
            integration_responses=integration_responses
        )

        games = api.root.add_resource("games")
        games.add_method(
            "POST",
            lambda_integration,
            method_responses=method_responses
        )
        games.add_method(
            "GET",
            lambda_integration,
            method_responses=method_responses
        )

        game = games.add_resource("{gameId}")
        game.add_method(
            "GET",
            lambda_integration,
            method_responses=method_responses
        )
        game.add_method(
            "PUT",
            lambda_integration,
            method_responses=method_responses
        )

        stats = api.root.add_resource("stats")
        stats.add_method(
            "GET",
            lambda_integration,
            method_responses=method_responses
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

        # Output the CloudFront URL and API endpoint
        CfnOutput(self, "WebsiteURL",
            value=distribution.distribution_domain_name
        )

        CfnOutput(self, "ApiEndpoint",
            value=api.url
        )
