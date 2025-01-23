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
  const apiEndpoint = 'https://w9cqnnyhbi.execute-api.us-east-1.amazonaws.com/prod';

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

      const data = await response.json();
      console.log('API Response:', data);
      
      if (typeof data === 'string') {
        const newGame = JSON.parse(data);
        console.log('Parsed new game state:', newGame);
        setGame(newGame);
      } else {
        console.log('Setting game state directly:', data);
        setGame(data);
      }
      
      setSelectedSquare(null);
      setValidMoves([]);
    } catch (error) {
      console.error('Error creating game:', error);
      alert('Failed to create new game. Please try again.');
    }
  };

  const countPieces = (color: 'r' | 'b'): number => {
    let count = 0;
    for (let row = 0; row < 8; row++) {
      for (let col = 0; col < 8; col++) {
        const piece = game.board[row][col];
        if (piece && piece.toLowerCase() === color) {
          count++;
        }
      }
    }
    return count;
  };

  const checkWinner = (): string | null => {
    const redPieces = countPieces('r');
    const blackPieces = countPieces('b');

    console.log('Piece count:', { red: redPieces, black: blackPieces });

    if (redPieces === 0) return 'black';
    if (blackPieces === 0) return 'red';
    return null;
  };

  const calculateValidMoves = (row: number, col: number): Move[] => {
    const piece = game.board[row][col];
    console.log('Calculating moves for piece:', {
      row,
      col,
      piece,
      isKing: piece === piece.toUpperCase(),
      isBlackSquare: (row + col) % 2 === 0
    });
    
    if (!piece) return [];

    const isKing = piece === piece.toUpperCase();
    const moves: Move[] = [];

    // Determine valid directions based on piece type and color
    const directions: number[] = [];
    if (piece.toLowerCase() === 'r') {
      directions.push(-1); // Red pieces move up
    } else if (piece.toLowerCase() === 'b') {
      directions.push(1);  // Black pieces move down
    }
    if (isKing) {
      // Kings can move both up and down
      if (!directions.includes(-1)) directions.push(-1);
      if (!directions.includes(1)) directions.push(1);
    }

    console.log('Movement directions:', directions);

    // First check for jumps (these are mandatory)
    const jumps: Move[] = [];
    for (const rowDir of directions) {
      for (const colDir of [-1, 1]) { // Left and right
        const jumpedRow = row + rowDir;
        const jumpedCol = col + colDir;
        const newRow = row + (rowDir * 2);
        const newCol = col + (colDir * 2);

        console.log('Checking jump:', {
          from: { row, col },
          over: { row: jumpedRow, col: jumpedCol, piece: game.board[jumpedRow]?.[jumpedCol] },
          to: { row: newRow, col: newCol },
          isBlackSquare: (newRow + newCol) % 2 === 0
        });

        // Check if jump is within bounds
        if (newRow < 0 || newRow > 7 || newCol < 0 || newCol > 7) {
          console.log('Jump out of bounds');
          continue;
        }
        
        // Check if there's an opponent's piece to jump over
        const jumpedPiece = game.board[jumpedRow][jumpedCol];
        if (!jumpedPiece) {
          console.log('No piece to jump over');
          continue;
        }
        
        // Check if landing square is empty
        if (game.board[newRow][newCol]) {
          console.log('Landing square occupied');
          continue;
        }
        
        const isOpponentPiece = 
          (piece.toLowerCase() === 'r' && jumpedPiece.toLowerCase() === 'b') ||
          (piece.toLowerCase() === 'b' && jumpedPiece.toLowerCase() === 'r');

        console.log('Jump validation:', {
          isOpponentPiece,
          isBlackSquare: (newRow + newCol) % 2 === 0
        });

        // Only allow jumps over opponent's pieces to black squares
        if (isOpponentPiece && (newRow + newCol) % 2 === 0) {
          jumps.push({ row: newRow, col: newCol });
          console.log('Valid jump found:', { row: newRow, col: newCol });
        }
      }
    }

    // If there are jumps available, they are mandatory
    if (jumps.length > 0) {
      console.log('Mandatory jumps found:', jumps);
      return jumps;
    }

    // If no jumps are available, check for regular moves
    for (const rowDir of directions) {
      for (const colDir of [-1, 1]) { // Left and right
        const newRow = row + rowDir;
        const newCol = col + colDir;

        console.log('Checking regular move:', {
          from: { row, col },
          to: { row: newRow, col: newCol },
          isBlackSquare: (newRow + newCol) % 2 === 0
        });

        // Check if move is within bounds
        if (newRow < 0 || newRow > 7 || newCol < 0 || newCol > 7) {
          console.log('Move out of bounds');
          continue;
        }
        
        // Check if destination square is empty
        if (game.board[newRow][newCol]) {
          console.log('Destination square occupied');
          continue;
        }

        // Only allow moves to black squares
        const isBlackSquare = (newRow + newCol) % 2 === 0;
        console.log('Square color check:', {
          newRow,
          newCol,
          sum: newRow + newCol,
          isBlackSquare
        });

        if (isBlackSquare) {
          moves.push({ row: newRow, col: newCol });
          console.log('Valid move found:', { row: newRow, col: newCol });
        } else {
          console.log('Not a black square');
        }
      }
    }

    console.log('Final valid moves:', moves);
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

      // Check for winner after move
      const winner = checkWinner();
      if (winner) {
        setGame(prev => ({
          ...prev,
          status: 'finished',
          winner: winner
        }));
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
        {game.status === 'finished' && game.winner ? `Game Over - ${game.winner.charAt(0).toUpperCase() + game.winner.slice(1)} Wins!` : `Current Turn: ${game.currentPlayer.charAt(0).toUpperCase() + game.currentPlayer.slice(1)}`}
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
              const isBlackSquare = (rowIndex + colIndex) % 2 === 0;
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
            backgroundColor: '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            marginBottom: '20px'
          }}
        >
          {game.status === 'finished' ? 'Play Again' : game.gameId ? 'Restart Game' : 'New Game'}
        </button>
      </div>
    </div>
  );
}

export default App;
