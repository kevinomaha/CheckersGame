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
    
    # Initialize the board
    board = [
        ['b', '', 'b', '', 'b', '', 'b', ''],  # 0
        ['', 'b', '', 'b', '', 'b', '', 'b'],  # 1
        ['b', '', 'b', '', 'b', '', 'b', ''],  # 2
        ['', '', '', '', '', '', '', ''],      # 3
        ['', '', '', '', '', '', '', ''],      # 4
        ['', 'r', '', 'r', '', 'r', '', 'r'],  # 5
        ['r', '', 'r', '', 'r', '', 'r', ''],  # 6
        ['', 'r', '', 'r', '', 'r', '', 'r']   # 7
    ]
    
    # Create game state
    game = {
        'gameId': game_id,
        'board': board,
        'currentPlayer': 'red',
        'status': 'active',
        'createdAt': datetime.utcnow().isoformat(),
        'updatedAt': datetime.utcnow().isoformat(),
        'players': {
            'red': event['requestContext']['identity'].get('cognitoIdentityId', 'anonymous'),
            'black': None
        }
    }
    
    print(f"Creating new game: {game_id}")
    print("Initial board:")
    for row in board:
        print(" ".join(piece if piece else "_" for piece in row))
    
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

def has_valid_jumps(board, row, col, player_color):
    """Check if a piece has any valid jumps available"""
    piece = board[row][col]
    if not piece:
        return False
        
    is_king = piece.isupper()
    directions = []
    
    # Determine valid directions based on piece type
    if player_color == 'red' or is_king:
        directions.append(-1)  # Up
    if player_color == 'black' or is_king:
        directions.append(1)   # Down
        
    # Check all possible jump directions
    for row_dir in directions:
        for col_dir in [-1, 1]:  # Left and right
            jumped_row = row + row_dir
            jumped_col = col + col_dir
            target_row = row + (row_dir * 2)
            target_col = col + (col_dir * 2)
            
            # Check if jump is within bounds
            if not (0 <= target_row < 8 and 0 <= target_col < 8):
                continue
                
            # Check if there's an opponent's piece to jump over
            if not board[jumped_row][jumped_col]:
                continue
                
            jumped_piece = board[jumped_row][jumped_col]
            if player_color == 'red' and jumped_piece.lower() != 'b':
                continue
            if player_color == 'black' and jumped_piece.lower() != 'r':
                continue
                
            # Check if landing square is empty
            if not board[target_row][target_col]:
                return True
                
    return False

def update_game(event):
    """Update a game with a move"""
    try:
        game_id = event['pathParameters']['gameId']
        body = json.loads(event['body'])
        
        # Get move coordinates
        from_row = int(body.get('fromRow'))
        from_col = int(body.get('fromCol'))
        to_row = int(body.get('toRow'))
        to_col = int(body.get('toCol'))
        
        print(f"Move request: from ({from_row}, {from_col}) to ({to_row}, {to_col})")
        
        # Get current game state
        response = game_table.get_item(Key={'gameId': game_id})
        if 'Item' not in response:
            print("Game not found")
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Game not found'})
            }
        
        game = response['Item']
        board = game['board']
        current_player = game['currentPlayer']
        
        print(f"Current game state:")
        print(f"Player: {current_player}")
        print("Board:")
        for row in board:
            print(" ".join(piece if piece else "_" for piece in row))
        
        # Validate move
        if not is_valid_move(board, (from_row, from_col), (to_row, to_col), current_player):
            print(f"Invalid move detected:")
            print(f"From: ({from_row}, {from_col}) - Piece: {board[from_row][from_col]}")
            print(f"To: ({to_row}, {to_col}) - Piece: {board[to_row][to_col]}")
            print(f"Current player: {current_player}")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Invalid move',
                    'details': {
                        'from': {'row': from_row, 'col': from_col, 'piece': board[from_row][from_col]},
                        'to': {'row': to_row, 'col': to_col, 'piece': board[to_row][to_col]},
                        'currentPlayer': current_player
                    }
                })
            }
        
        # Make the move
        piece = board[from_row][from_col]
        board[from_row][from_col] = ''
        board[to_row][to_col] = piece
        
        print(f"Moving piece {piece} from ({from_row}, {from_col}) to ({to_row}, {to_col})")
        
        # Handle jump captures
        captured = False
        if abs(to_row - from_row) == 2:
            jumped_row = (from_row + to_row) // 2
            jumped_col = (from_col + to_col) // 2
            captured_piece = board[jumped_row][jumped_col]
            board[jumped_row][jumped_col] = ''
            captured = True
            print(f"Captured piece {captured_piece} at ({jumped_row}, {jumped_col})")
        
        # Handle king promotion
        was_promoted = False
        if (current_player == 'red' and to_row == 0) or (current_player == 'black' and to_row == 7):
            board[to_row][to_col] = board[to_row][to_col].upper()
            was_promoted = True
            print(f"Piece promoted to king at ({to_row}, {to_col})")
        
        # Check for additional jumps
        has_more_jumps = False
        if captured and not was_promoted:
            has_more_jumps = has_valid_jumps(board, to_row, to_col, current_player)
            print(f"Additional jumps available: {has_more_jumps}")
        
        # Only switch players if no more jumps are available
        if not has_more_jumps:
            current_player = 'black' if current_player == 'red' else 'red'
        
        # Check for winner
        winner = check_winner(board, current_player)
        if winner:
            print(f"Game over! {winner} wins!")
            game['status'] = 'finished'
            game['winner'] = winner
        
        # Update game state
        game['board'] = board
        game['currentPlayer'] = current_player
        game['updatedAt'] = datetime.utcnow().isoformat()
        
        print("\nUpdated game state:")
        print(f"Next player: {current_player}")
        print("Board:")
        for row in board:
            print(" ".join(piece if piece else "_" for piece in row))
        
        game_table.put_item(Item=game)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                **game,
                'hasMoreJumps': has_more_jumps
            })
        }
        
    except Exception as e:
        print(f"Error processing move: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': f'Error processing move: {str(e)}',
                'details': {
                    'event': event,
                    'traceback': traceback.format_exc()
                }
            })
        }

def is_valid_move(board, from_pos, to_pos, player_color):
    """Validate a move according to checkers rules"""
    from_row, from_col = from_pos
    to_row, to_col = to_pos
    
    print(f"Validating move: {from_pos} -> {to_pos} for {player_color}")
    
    # Basic boundary checks
    if not (0 <= from_row < 8 and 0 <= from_col < 8 and 0 <= to_row < 8 and 0 <= to_col < 8):
        print("Invalid: Out of bounds")
        return False
    
    # Check if there's a piece at the start position
    piece = board[from_row][from_col]
    if not piece:
        print("Invalid: No piece at start position")
        return False
    
    # Check if it's the right color piece
    if player_color == 'red' and piece.lower() != 'r':
        print("Invalid: Not a red piece")
        return False
    if player_color == 'black' and piece.lower() != 'b':
        print("Invalid: Not a black piece")
        return False
    
    # Check if destination is empty
    if board[to_row][to_col]:
        print("Invalid: Destination is not empty")
        return False
    
    # Get move details
    is_king = piece.isupper()
    row_diff = to_row - from_row
    col_diff = abs(to_col - from_col)
    
    print(f"Move details: row_diff={row_diff}, col_diff={col_diff}, is_king={is_king}")
    
    # Regular move - one square diagonally forward
    if col_diff == 1:
        if player_color == 'red' and row_diff == -1:
            print("Valid: Regular red move forward")
            return True
        if player_color == 'black' and row_diff == 1:
            print("Valid: Regular black move forward")
            return True
        if is_king and abs(row_diff) == 1:
            print("Valid: King move")
            return True
        print("Invalid: Invalid regular move direction")
        return False
    
    # Jump move - two squares diagonally
    if col_diff == 2 and abs(row_diff) == 2:
        jumped_row = (from_row + to_row) // 2
        jumped_col = (from_col + to_col) // 2
        jumped_piece = board[jumped_row][jumped_col]
        
        print(f"Jump move: jumped_piece={jumped_piece}")
        
        # Must be jumping over an opponent's piece
        if not jumped_piece:
            print("Invalid: No piece to jump over")
            return False
        
        if player_color == 'red' and jumped_piece.lower() != 'b':
            print("Invalid: Red must jump over black")
            return False
        
        if player_color == 'black' and jumped_piece.lower() != 'r':
            print("Invalid: Black must jump over red")
            return False
        
        # Regular pieces can only jump forward
        if not is_king:
            if player_color == 'red' and row_diff != -2:
                print("Invalid: Red must jump forward")
                return False
            if player_color == 'black' and row_diff != 2:
                print("Invalid: Black must jump forward")
                return False
        
        print("Valid: Jump move")
        return True
    
    print("Invalid: Not a valid move pattern")
    return False

def has_any_moves(board, player_color):
    """Check if a player has any valid moves available"""
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if not piece:
                continue
                
            # Check if this is the player's piece
            if (player_color == 'red' and piece.lower() != 'r') or \
               (player_color == 'black' and piece.lower() != 'b'):
                continue
            
            # Check for any jumps
            if has_valid_jumps(board, row, col, player_color):
                return True
                
            # Check for regular moves
            is_king = piece.isupper()
            directions = []
            
            # Determine valid directions based on piece type
            if player_color == 'red' or is_king:
                directions.append(-1)  # Up
            if player_color == 'black' or is_king:
                directions.append(1)   # Down
                
            # Check all possible move directions
            for row_dir in directions:
                for col_dir in [-1, 1]:  # Left and right
                    target_row = row + row_dir
                    target_col = col + col_dir
                    
                    # Check if move is within bounds
                    if not (0 <= target_row < 8 and 0 <= target_col < 8):
                        continue
                        
                    # Check if target square is empty
                    if not board[target_row][target_col]:
                        return True
                        
    return False

def count_pieces(board, player_color):
    """Count how many pieces a player has"""
    count = 0
    for row in board:
        for piece in row:
            if not piece:
                continue
            if (player_color == 'red' and piece.lower() == 'r') or \
               (player_color == 'black' and piece.lower() == 'b'):
                count += 1
    return count

def check_winner(board, current_player):
    """Check if there's a winner"""
    opponent = 'black' if current_player == 'red' else 'red'
    
    # Check if opponent has any pieces left
    opponent_pieces = count_pieces(board, opponent)
    if opponent_pieces == 0:
        return current_player
        
    # Check if opponent has any valid moves
    if not has_any_moves(board, opponent):
        return current_player
        
    return None

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
                response = update_game(event)
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
