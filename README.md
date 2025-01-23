# AWS Checkers Game

A serverless checkers game built with AWS CDK, featuring real-time gameplay and statistics tracking.

## Architecture

The application consists of:
- Frontend: Static website hosted on S3 and served through CloudFront
- Backend: API Gateway + Lambda for game logic
- Database: DynamoDB for game state and player statistics

## Prerequisites

- Python 3.9 or later
- AWS CDK CLI
- AWS Account and configured credentials
- Node.js and npm (for frontend development)

## Project Structure

```
CheckersGame/
├── frontend/           # Static web frontend
│   ├── index.html     # Main HTML file
│   ├── styles.css     # Styles for the game
│   └── app.js         # Game logic
├── lambda/            # Backend Lambda functions
│   └── game.py        # Game API implementation
└── checkers_game/     # CDK infrastructure code
    └── checkers_game_stack.py
```

## Deployment Instructions

1. Create and activate a Python virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
source .venv/bin/activate  # On Unix or MacOS
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Deploy the CDK stack:
```bash
cdk deploy
```

4. After deployment, the CDK will output:
- WebsiteURL: The CloudFront URL where the game is hosted
- ApiEndpoint: The API Gateway endpoint

5. Update the API endpoint in the frontend:
   - Open `frontend/app.js`
   - Set the `apiEndpoint` variable to the API Gateway endpoint URL

## Playing the Game

1. Open the WebsiteURL in your browser
2. Click "New Game" to start a game
3. Red pieces move first
4. Click on a piece to select it, then click on a valid square to move
5. Capture opponent's pieces by jumping over them
6. Get a piece to the opposite end of the board to make it a king
7. The game ends when one player captures all opponent's pieces

## Game Rules

- Pieces can only move diagonally forward (unless they are kings)
- Kings can move diagonally both forward and backward
- Pieces must jump over opponent's pieces when possible
- Multiple jumps are allowed in a single turn
- The game ends when one player has no pieces left or cannot make a legal move

## Development

To run the frontend locally:
1. Navigate to the frontend directory
2. Open `index.html` in a web browser

To modify the game logic:
1. Edit the Lambda function in `lambda/game.py`
2. Deploy changes with `cdk deploy`

## Cleanup

To remove all AWS resources created by this project:
```bash
cdk destroy
```
