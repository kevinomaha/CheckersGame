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
    board = [[None] * 8 for _ in range(8)]
    
    # Place black pieces (top of board)
    for row in range(3):
        for col in range(8):
            if (row + col) % 2 == 1:
                board[row][col] = {'color': 'black', 'king': False}
    
    # Place red pieces (bottom of board)
    for row in range(5, 8):
        for col in range(8):
            if (row + col) % 2 == 1:
                board[row][col] = {'color': 'red', 'king': False}
    
    return board

def create_game(event):
    """Create a new game"""
    game_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    game = {
        'gameId': game_id,
        'board': create_initial_board(),
        'currentTurn': 'red',
        'status': 'active',
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
    if not piece or piece['color'] != player_color:
        return False
    
    # Check if destination is empty
    if board[to_row][to_col]:
        return False
    
    # Check if destination is on a black square
    if (to_row + to_col) % 2 == 0:
        return False
    
    # Movement rules
    is_king = piece['king']
    row_diff = to_row - from_row
    col_diff = abs(to_col - from_col)
    
    # Regular move
    if col_diff == 1:
        if player_color == 'red' and row_diff == -1:
            return True
        if player_color == 'black' and row_diff == 1:
            return True
        if is_king and abs(row_diff) == 1:
            return True
    
    # Jump move
    elif col_diff == 2:
        mid_row = (from_row + to_row) // 2
        mid_col = (from_col + to_col) // 2
        jumped_piece = board[mid_row][mid_col]
        
        if jumped_piece and jumped_piece['color'] != player_color:
            if player_color == 'red' and row_diff == -2:
                return True
            if player_color == 'black' and row_diff == 2:
                return True
            if is_king and abs(row_diff) == 2:
                return True
    
    return False

def make_move(event):
    """Make a move in the game"""
    game_id = event['pathParameters']['gameId']
    body = json.loads(event['body'])
    from_pos = body['from']
    to_pos = body['to']
    
    # Get current game state
    response = game_table.get_item(Key={'gameId': game_id})
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Game not found'})
        }
    
    game = response['Item']
    board = game['board']
    current_turn = game['currentTurn']
    
    # Validate move
    if not is_valid_move(board, from_pos, to_pos, current_turn):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid move'})
        }
    
    # Make the move
    piece = board[from_pos[0]][from_pos[1]]
    board[from_pos[0]][from_pos[1]] = None
    board[to_pos[0]][to_pos[1]] = piece
    
    # Check if piece becomes king
    if (current_turn == 'red' and to_pos[0] == 0) or (current_turn == 'black' and to_pos[0] == 7):
        piece['king'] = True
    
    # Handle jumps
    if abs(to_pos[0] - from_pos[0]) == 2:
        mid_row = (from_pos[0] + to_pos[0]) // 2
        mid_col = (from_pos[1] + to_pos[1]) // 2
        board[mid_row][mid_col] = None
    
    # Update game state
    game['board'] = board
    game['currentTurn'] = 'black' if current_turn == 'red' else 'red'
    game['updatedAt'] = datetime.utcnow().isoformat()
    
    # Check for winner
    red_pieces = black_pieces = 0
    for row in board:
        for cell in row:
            if cell:
                if cell['color'] == 'red':
                    red_pieces += 1
                else:
                    black_pieces += 1
    
    if red_pieces == 0:
        game['status'] = 'completed'
        game['winner'] = 'black'
        update_stats(game['players']['black'], True)
        update_stats(game['players']['red'], False)
    elif black_pieces == 0:
        game['status'] = 'completed'
        game['winner'] = 'red'
        update_stats(game['players']['red'], True)
        update_stats(game['players']['black'], False)
    
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
