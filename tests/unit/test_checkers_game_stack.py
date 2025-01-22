import aws_cdk as core
import aws_cdk.assertions as assertions

from checkers_game.checkers_game_stack import CheckersGameStack

# example tests. To run these tests, uncomment this file along with the example
# resource in checkers_game/checkers_game_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CheckersGameStack(app, "checkers-game")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
