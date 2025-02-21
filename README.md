# AWS Checkers Game

A serverless checkers game built with AWS CDK, featuring real-time gameplay and statistics tracking. This project demonstrates modern cloud architecture patterns and serverless application development using AWS services.

## Architecture Overview

### Infrastructure Components
- **Frontend Hosting**:
  - S3 bucket for static website hosting
  - CloudFront distribution for global content delivery
  - SSL/TLS encryption for secure communication

- **Backend Services**:
  - API Gateway for RESTful API endpoints
  - Lambda functions for serverless game logic
  - DynamoDB for persistent game state storage
  - IAM roles and policies for secure service communication

### System Design Patterns
- **Serverless Architecture**: Eliminates infrastructure management and provides automatic scaling
- **Event-Driven Design**: Game state changes trigger appropriate system responses
- **RESTful API**: Standard HTTP methods for game operations (GET, POST, PUT, DELETE)
- **Single-Page Application**: React-based frontend for smooth user experience

## Technical Stack

### Frontend Technologies
- **React**: Modern UI framework for component-based development
- **TypeScript**: Type-safe JavaScript for better development experience
- **CSS3**: Custom styling for game board and pieces
- **AWS SDK**: Browser-based AWS service integration

### Backend Technologies
- **Python 3.9+**: Core backend logic implementation
- **AWS CDK**: Infrastructure as Code (IaC) for AWS resource management
- **DynamoDB**: NoSQL database for game state persistence
- **Lambda Runtime**: Python-based serverless compute

## Project Structure

```
CheckersGame/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── App.tsx          # Main game component
│   │   ├── components/      # Reusable UI components
│   │   ├── types/          # TypeScript type definitions
│   │   └── utils/          # Helper functions
│   ├── public/             # Static assets
│   └── package.json        # Frontend dependencies
├── lambda/                 # Backend Lambda functions
│   ├── game.py            # Game logic implementation
│   └── utils/             # Backend helper functions
├── checkers_game/         # CDK infrastructure code
│   ├── checkers_game_stack.py  # Main stack definition
│   └── config.py          # Environment configuration
├── tests/                 # Test suites
└── requirements.txt       # Python dependencies
```

## Core Concepts

### Game State Management
- Game state stored in DynamoDB with the following structure:
  ```json
  {
    "gameId": "unique-identifier",
    "board": [[...], [...], ...],
    "currentPlayer": "red/black",
    "status": "active/finished",
    "validMoves": [[x1,y1], [x2,y2], ...],
    "timestamp": "ISO-8601-timestamp"
  }
  ```

### Move Validation
- Implemented in Lambda function using:
  - Piece movement rules (diagonal only)
  - Jump detection and validation
  - King piece special rules
  - Multiple jump sequence handling

### Player Interaction Flow
1. Player initiates move by selecting a piece
2. Frontend validates basic move patterns
3. Backend validates complete move legality
4. Game state updates in DynamoDB
5. Frontend reflects new game state

## Security Considerations

### Authentication & Authorization
- CloudFront for SSL/TLS encryption
- IAM roles for service-to-service communication
- API Gateway resource policies

### Data Protection
- DynamoDB encryption at rest
- HTTPS for all API communications
- Minimal required IAM permissions

## Deployment Environments

### Development
- Separate S3 bucket and API Gateway stage
- CloudFront distribution with development domain
- Isolated DynamoDB tables for testing

### Production
- Production-grade infrastructure with:
  - Higher capacity DynamoDB settings
  - CloudFront caching optimizations
  - Enhanced monitoring and logging

## Prerequisites

- Python 3.9 or later
- AWS CDK CLI v2.x
- AWS Account and configured credentials
- Node.js 14+ and npm
- AWS CLI v2

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
cd frontend && npm install
```

3. Deploy the CDK stack:
```bash
cdk deploy CheckersGameStackDev  # For development
cdk deploy CheckersGameStackProd # For production
```

4. After deployment, note the outputs:
- `WebsiteURL`: CloudFront distribution domain
- `ApiEndpoint`: API Gateway endpoint URL

## Game Rules

### Basic Movement
- Pieces move diagonally forward only
- Kings can move diagonally in any direction
- One space per move unless jumping

### Capturing
- Jumps are mandatory when available
- Multiple jumps must be completed in one turn
- Captured pieces are removed immediately

### Special Rules
- Kings are created upon reaching opposite end
- Game ends when a player:
  - Loses all pieces
  - Has no legal moves available

## Development Workflow

### Local Development
1. Start frontend development server:
```bash
cd frontend
npm start
```

2. Run tests:
```bash
# Frontend tests
cd frontend && npm test

# Backend tests
pytest tests/
```

### Making Changes
1. Frontend modifications:
   - Edit React components in `frontend/src`
   - Test changes locally
   - Build and deploy to S3

2. Backend modifications:
   - Update Lambda function code
   - Deploy using CDK
   - Test in development environment

## Monitoring and Maintenance

### CloudWatch Metrics
- API Gateway request/response metrics
- Lambda execution metrics
- DynamoDB throughput and latency

### Logging
- Lambda function logs
- API Gateway access logs
- CloudFront access logs

## Cleanup

To remove all AWS resources:
```bash
cdk destroy CheckersGameStackDev  # Remove dev environment
cdk destroy CheckersGameStackProd # Remove prod environment
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Submit pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
