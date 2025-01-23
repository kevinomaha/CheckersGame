import React, { useState } from 'react';

interface GameState {
  gameId: string;
  board: string[][];
  currentPlayer: 'red' | 'black';
  status: 'active' | 'finished';
  winner?: string;
  createdAt: string;
  updatedAt: string;
  hasMoreJumps?: boolean;
}

interface Square {
  row: number;
  col: number;
  piece: string;
}

interface Move {
  row: number;
  col: number;
}

function App() {
  const [game, setGame] = useState<GameState>({
    gameId: '',
    board: Array(8).fill(null).map(() => Array(8).fill('')),
    currentPlayer: 'red',
    status: 'active',
    createdAt: '',
    updatedAt: ''
  });
  const [selectedSquare, setSelectedSquare] = useState<Square | null>(null);
  const [validMoves, setValidMoves] = useState<Move[]>([]);
  const apiEndpoint = 'https://rd2ll5az83.execute-api.us-east-1.amazonaws.com/prod';

  const getGameStatus = () => {
    if (!game.gameId) {
      return "Click 'New Game' to start playing!";
    }
    if (game.status === 'finished') {
      return `Game Over! ${game.winner?.toUpperCase()} wins! 🎉`;
    }
    return `Current Turn: ${game.currentPlayer.toUpperCase()}`;
  };

  const createNewGame = async () => {
    try {
      const response = await fetch(`${apiEndpoint}/games`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        mode: 'cors'
      });
      
      if (!response.ok) {
        throw new Error('Failed to create game');
      }

      const newGame = await response.json();
      console.log('New game state:', newGame);
      setGame(newGame);
      setSelectedSquare(null);
      setValidMoves([]);
    } catch (error) {
      console.error('Error creating game:', error);
      alert('Failed to create new game. Please try again.');
    }
  };

  const calculateValidMoves = (row: number, col: number): Move[] => {
    const piece = game.board[row][col];
    if (!piece) return [];

    const isKing = piece === piece.toUpperCase();
    const moves: Move[] = [];

    // Determine valid directions based on piece type
    const directions: number[] = [];
    if (piece.toLowerCase() === 'r' || isKing) directions.push(-1); // Up
    if (piece.toLowerCase() === 'b' || isKing) directions.push(1);  // Down

    // Check for regular moves
    for (const rowDir of directions) {
      for (const colDir of [-1, 1]) { // Left and right
        const newRow = row + rowDir;
        const newCol = col + colDir;

        if (newRow < 0 || newRow > 7 || newCol < 0 || newCol > 7) continue;
        if (game.board[newRow][newCol]) continue;

        // Only allow moves to black squares
        if ((newRow + newCol) % 2 === 1) {
          moves.push({ row: newRow, col: newCol });
        }
      }
    }

    // Check for jumps
    for (const rowDir of directions) {
      for (const colDir of [-1, 1]) { // Left and right
        const jumpedRow = row + rowDir;
        const jumpedCol = col + colDir;
        const newRow = row + (rowDir * 2);
        const newCol = col + (colDir * 2);

        if (newRow < 0 || newRow > 7 || newCol < 0 || newCol > 7) continue;
        if (!game.board[jumpedRow][jumpedCol]) continue;
        if (game.board[newRow][newCol]) continue;

        const jumpedPiece = game.board[jumpedRow][jumpedCol];
        const isOpponentPiece = 
          (piece.toLowerCase() === 'r' && jumpedPiece.toLowerCase() === 'b') ||
          (piece.toLowerCase() === 'b' && jumpedPiece.toLowerCase() === 'r');

        if (isOpponentPiece && (newRow + newCol) % 2 === 1) {
          moves.push({ row: newRow, col: newCol });
        }
      }
    }

    return moves;
  };

  const handleSquareClick = async (row: number, col: number) => {
    if (!game.gameId || game.status === 'finished') return;
    
    const piece = game.board?.[row]?.[col];
    console.log('Clicked square:', {row, col, piece});
    console.log('Game state:', {
      currentPlayer: game.currentPlayer,
      selectedSquare,
      validMoves
    });

    // First click - selecting a piece
    if (!selectedSquare) {
      if (!piece) {
        console.log('Clicked empty square');
        return;
      }

      const isCurrentPlayersPiece = 
        (game.currentPlayer === 'red' && piece.toLowerCase() === 'r') ||
        (game.currentPlayer === 'black' && piece.toLowerCase() === 'b');

      if (!isCurrentPlayersPiece) {
        alert("You can only move your own pieces!");
        return;
      }

      const moves = calculateValidMoves(row, col);
      console.log('Calculated valid moves:', moves);
      
      if (moves.length === 0) {
        alert("This piece has no valid moves!");
        return;
      }

      setSelectedSquare({ row, col, piece });
      setValidMoves(moves);
      return;
    }

    // Second click - making a move
    if (selectedSquare.row === row && selectedSquare.col === col) {
      console.log('Deselecting piece');
      setSelectedSquare(null);
      setValidMoves([]);
      return;
    }

    // Check if this is a valid move
    const isValidDestination = validMoves.some(move => move.row === row && move.col === col);
    console.log('Move validation:', {
      isValidDestination,
      selectedSquare,
      targetSquare: {row, col}
    });

    if (!isValidDestination) {
      console.log('Invalid move - not in valid moves list');
      setSelectedSquare(null);
      setValidMoves([]);
      return;
    }

    try {
      const moveData = {
        fromRow: selectedSquare.row,
        fromCol: selectedSquare.col,
        toRow: row,
        toCol: col
      };
      console.log('Sending move to API:', moveData);

      const response = await fetch(`${apiEndpoint}/games/${game.gameId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        mode: 'cors',
        body: JSON.stringify(moveData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('API Error:', {
          status: response.status,
          statusText: response.statusText,
          errorData
        });
        throw new Error(errorData.error || 'Invalid move');
      }

      const updatedGame = await response.json();
      console.log('Move successful:', updatedGame);
      
      setGame(updatedGame);
      
      // Only clear selection if there are no more jumps available
      if (!updatedGame.hasMoreJumps) {
        setSelectedSquare(null);
        setValidMoves([]);
      } else {
        // Update selected square to new position for next jump
        setSelectedSquare({
          row,
          col,
          piece: updatedGame.board[row][col]
        });
        // Calculate new valid moves from the new position
        setValidMoves(calculateValidMoves(row, col));
      }
    } catch (error) {
      console.error('Error making move:', error);
      alert(error instanceof Error ? error.message : 'Invalid move. Please try again.');
      setSelectedSquare(null);
      setValidMoves([]);
    }
  };

  return (
    <div className="App" style={{ padding: '20px', textAlign: 'center' }}>
      <h1>Checkers Game</h1>
      <div className="game-status" style={{ 
        fontSize: '1.5em', 
        marginBottom: '20px',
        fontWeight: 'bold',
        color: game.status === 'finished' ? '#4CAF50' : '#2196F3'
      }}>
        {getGameStatus()}
      </div>
      <div className="game-board" style={{
        display: 'inline-block',
        border: '2px solid #333',
        backgroundColor: '#fff'
      }}>
        {game.board.map((row, rowIndex) => (
          <div key={rowIndex} className="board-row" style={{
            display: 'flex'
          }}>
            {row.map((piece, colIndex) => {
              const isBlackSquare = (rowIndex + colIndex) % 2 === 1;
              const isSelected = selectedSquare?.row === rowIndex && selectedSquare?.col === colIndex;
              const isValidMove = validMoves.some(move => move.row === rowIndex && move.col === colIndex);
              
              return (
                <div
                  key={colIndex}
                  onClick={() => handleSquareClick(rowIndex, colIndex)}
                  style={{
                    width: '60px',
                    height: '60px',
                    backgroundColor: isBlackSquare ? '#666' : '#fff',
                    border: isSelected ? '3px solid yellow' : '1px solid #999',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    cursor: 'pointer',
                    position: 'relative',
                    boxSizing: 'border-box'
                  }}
                >
                  {piece && (
                    <div style={{
                      width: '80%',
                      height: '80%',
                      borderRadius: '50%',
                      backgroundColor: piece.toLowerCase() === 'r' ? '#ff4444' : '#333',
                      border: '2px solid #fff',
                      boxShadow: '0 0 10px rgba(0,0,0,0.3)',
                      position: 'relative'
                    }}>
                      {piece === piece.toUpperCase() && (
                        <div style={{
                          position: 'absolute',
                          top: '50%',
                          left: '50%',
                          transform: 'translate(-50%, -50%)',
                          color: piece.toLowerCase() === 'r' ? '#ffcccc' : '#666',
                          fontSize: '24px'
                        }}>
                          ♔
                        </div>
                      )}
                    </div>
                  )}
                  {isValidMove && (
                    <div style={{
                      position: 'absolute',
                      width: '20px',
                      height: '20px',
                      borderRadius: '50%',
                      backgroundColor: 'rgba(0, 255, 0, 0.5)',
                      border: '2px solid rgba(0, 255, 0, 0.8)'
                    }} />
                  )}
                </div>
              );
            })}
          </div>
        ))}
      </div>
      <div style={{ marginTop: '20px' }}>
        <button 
          onClick={createNewGame}
          style={{
            padding: '10px 20px',
            fontSize: '16px',
            backgroundColor: game.status === 'finished' ? '#4CAF50' : '#ccc',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: game.status === 'finished' ? 'pointer' : 'not-allowed',
            marginBottom: '20px'
          }}
          disabled={game.status !== 'finished' && game.gameId !== ''}
        >
          {!game.gameId ? 'New Game' : game.status === 'finished' ? 'Play Again' : 'Game in Progress'}
        </button>
      </div>
    </div>
  );
}

export default App;
