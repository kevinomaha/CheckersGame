from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_s3_deployment as s3deploy,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct

class CheckersGameStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 bucket for website hosting
        website_bucket = s3.Bucket(self, "CheckersWebsiteBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL
        )

        # CloudFront distribution
        distribution = cloudfront.Distribution(self, "CheckersDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(website_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
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

        # DynamoDB tables
        game_table = dynamodb.Table(self, "CheckersGameTable",
            partition_key=dynamodb.Attribute(
                name="gameId",
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        stats_table = dynamodb.Table(self, "CheckersStatsTable",
            partition_key=dynamodb.Attribute(
                name="playerId",
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        # Lambda functions
        game_lambda = _lambda.Function(self, "CheckersGameFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="game.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "GAME_TABLE": game_table.table_name,
                "STATS_TABLE": stats_table.table_name
            }
        )

        # Grant Lambda permissions to DynamoDB
        game_table.grant_read_write_data(game_lambda)
        stats_table.grant_read_write_data(game_lambda)

        # API Gateway
        api = apigateway.RestApi(self, "CheckersApi",
            rest_api_name="Checkers Game API",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=["*"],
                allow_methods=["GET", "POST", "PUT", "DELETE"],
                allow_headers=["*"]
            )
        )

        games = api.root.add_resource("games")
        games.add_method("POST", apigateway.LambdaIntegration(game_lambda))  # Create game
        games.add_method("GET", apigateway.LambdaIntegration(game_lambda))   # List games

        game = games.add_resource("{gameId}")
        game.add_method("GET", apigateway.LambdaIntegration(game_lambda))    # Get game
        game.add_method("PUT", apigateway.LambdaIntegration(game_lambda))    # Make move

        stats = api.root.add_resource("stats")
        stats.add_method("GET", apigateway.LambdaIntegration(game_lambda))   # Get stats

        # Deploy frontend to S3
        s3deploy.BucketDeployment(self, "DeployWebsite",
            sources=[s3deploy.Source.asset("frontend/build")],
            destination_bucket=website_bucket,
            distribution=distribution,
            distribution_paths=["/*"]
        )

        # Output the CloudFront URL and API endpoint
        CfnOutput(self, "WebsiteURL",
            value=f"https://{distribution.distribution_domain_name}"
        )
        
        CfnOutput(self, "ApiEndpoint",
            value=api.url
        )
