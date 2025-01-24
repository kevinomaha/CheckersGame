#!/usr/bin/env python3
import os
import aws_cdk as cdk
from checkers_game.checkers_game_stack import CheckersGameStack
from checkers_game.config import Config

app = cdk.App()

account = os.getenv('CDK_DEFAULT_ACCOUNT', '811402695427')
region = os.getenv('CDK_DEFAULT_REGION', 'us-east-1')

env = cdk.Environment(
    account=account,
    region=region
)

# Deploy development stack
dev_stack = CheckersGameStack(
    app, 
    "CheckersGameStackDev",
    env_config=Config.DEV,
    env=env
)

# Deploy production stack
prod_stack = CheckersGameStack(
    app,
    "CheckersGameStackProd",
    env_config=Config.PROD,
    env=env
)

app.synth()
