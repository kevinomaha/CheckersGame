import os
import json
import uuid
import boto3
from datetime import datetime

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
game_table = dynamodb.Table(os.environ['GAME_TABLE'])
stats_table = dynamodb.Table(os.environ['STATS_TABLE'])

def create_initial_board():
    """Create the initial checkers board state"""
    board = [
        ['b', '', 'b', '', 'b', '', 'b', ''],
        ['', 'b', '', 'b', '', 'b', '', 'b'],
        ['b', '', 'b', '', 'b', '', 'b', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', 'r', '', 'r', '', 'r', '', 'r'],
        ['r', '', 'r', '', 'r', '', 'r', ''],
        ['', 'r', '', 'r', '', 'r', '', 'r']
    ]
    return board

def create_game(event):
    """Create a new game"""
    game_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    game = {
        'gameId': game_id,
        'board': create_initial_board(),
        'currentPlayer': 'red',
        'status': 'in_progress',
        'createdAt': timestamp,
        'updatedAt': timestamp,
        'players': {
            'red': event['requestContext']['identity'].get('cognitoIdentityId', 'anonymous'),
            'black': None
        }
    }
    
    game_table.put_item(Item=game)
    return {
        'statusCode': 201,
        'body': json.dumps(game)
    }

def get_game(event):
    """Get game state"""
    game_id = event['pathParameters']['gameId']
    
    response = game_table.get_item(Key={'gameId': game_id})
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Game not found'})
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps(response['Item'])
    }

def is_valid_move(board, from_pos, to_pos, player_color):
    """Validate a move according to checkers rules"""
    from_row, from_col = from_pos
    to_row, to_col = to_pos
    
    # Basic boundary checks
    if not (0 <= from_row < 8 and 0 <= from_col < 8 and 0 <= to_row < 8 and 0 <= to_col < 8):
        return False
    
    # Check if there's a piece at the start position and it's the right color
    piece = board[from_row][from_col]
    if not piece or (piece != 'r' and piece != 'b') or (player_color == 'red' and piece != 'r') or (player_color == 'black' and piece != 'b'):
        return False
    
    # Check if destination is empty
    if board[to_row][to_col]:
        return False
    
    # Check if destination is on a black square
    if (to_row + to_col) % 2 == 0:
        return False
    
    # Movement rules
    row_diff = to_row - from_row
    col_diff = abs(to_col - from_col)
    
    # Regular move
    if col_diff == 1:
        if player_color == 'red' and row_diff == -1:
            return True
        if player_color == 'black' and row_diff == 1:
            return True
    
    # Jump move
    elif col_diff == 2:
        mid_row = (from_row + to_row) // 2
        mid_col = (from_col + to_col) // 2
        jumped_piece = board[mid_row][mid_col]
        
        if jumped_piece and jumped_piece != '' and jumped_piece != piece:
            if player_color == 'red' and row_diff == -2:
                return True
            if player_color == 'black' and row_diff == 2:
                return True
    
    return False

def make_move(event):
    """Make a move in the game"""
    game_id = event['pathParameters']['gameId']
    body = json.loads(event['body'])
    
    # Extract move coordinates
    from_row = body.get('fromRow')
    from_col = body.get('fromCol')
    to_row = body.get('toRow')
    to_col = body.get('toCol')
    
    if any(x is None for x in [from_row, from_col, to_row, to_col]):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing move coordinates'})
        }
    
    # Get current game state
    response = game_table.get_item(Key={'gameId': game_id})
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Game not found'})
        }
    
    game = response['Item']
    board = game['board']
    current_player = game['currentPlayer']
    
    # Convert coordinates to tuples for validation
    from_pos = (from_row, from_col)
    to_pos = (to_row, to_col)
    
    # Validate move
    if not is_valid_move(board, from_pos, to_pos, current_player):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid move'})
        }
    
    # Make the move
    piece = board[from_row][from_col]
    board[from_row][from_col] = ''
    board[to_row][to_col] = piece
    
    # Check if piece becomes king
    if (piece == 'r' and to_row == 0) or (piece == 'b' and to_row == 7):
        board[to_row][to_col] = piece.upper()
    
    # Handle jumps
    if abs(to_row - from_row) == 2:
        mid_row = (from_row + to_row) // 2
        mid_col = (from_col + to_col) // 2
        board[mid_row][mid_col] = ''
    
    # Update game state
    game['board'] = board
    game['currentPlayer'] = 'black' if current_player == 'red' else 'red'
    game['updatedAt'] = datetime.utcnow().isoformat()
    
    # Check for winner
    red_pieces = 0
    black_pieces = 0
    for row in board:
        for cell in row:
            if cell.lower() == 'r':
                red_pieces += 1
            elif cell.lower() == 'b':
                black_pieces += 1
    
    if red_pieces == 0:
        game['status'] = 'finished'
        game['winner'] = 'black'
    elif black_pieces == 0:
        game['status'] = 'finished'
        game['winner'] = 'red'
    
    # Save updated game state
    game_table.put_item(Item=game)
    
    return {
        'statusCode': 200,
        'body': json.dumps(game)
    }

def update_stats(player_id, is_winner):
    """Update player statistics"""
    if player_id == 'anonymous':
        return
    
    try:
        response = stats_table.get_item(Key={'playerId': player_id})
        stats = response.get('Item', {
            'playerId': player_id,
            'wins': 0,
            'losses': 0,
            'totalGames': 0
        })
        
        stats['totalGames'] += 1
        if is_winner:
            stats['wins'] += 1
        else:
            stats['losses'] += 1
        
        stats_table.put_item(Item=stats)
    except Exception as e:
        print(f"Error updating stats for player {player_id}: {str(e)}")

def get_stats(event):
    """Get player statistics"""
    player_id = event['requestContext']['identity'].get('cognitoIdentityId')
    if not player_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Player not authenticated'})
        }
    
    response = stats_table.get_item(Key={'playerId': player_id})
    stats = response.get('Item', {
        'playerId': player_id,
        'wins': 0,
        'losses': 0,
        'totalGames': 0
    })
    
    return {
        'statusCode': 200,
        'body': json.dumps(stats)
    }

def handler(event, context):
    """Main Lambda handler"""
    http_method = event['httpMethod']
    resource = event['resource']
    
    # Add CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET,PUT,DELETE'
    }
    
    try:
        if resource == '/games':
            if http_method == 'POST':
                response = create_game(event)
            elif http_method == 'GET':
                response = list_games(event)
        elif resource == '/games/{gameId}':
            if http_method == 'GET':
                response = get_game(event)
            elif http_method == 'PUT':
                response = make_move(event)
        elif resource == '/stats':
            if http_method == 'GET':
                response = get_stats(event)
        else:
            response = {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid endpoint'})
            }
        
        response['headers'] = headers
        return response
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
