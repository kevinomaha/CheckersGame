import React, { useState } from 'react';

interface GameState {
  gameId?: string;
  board?: string[][];
  currentPlayer?: 'red' | 'black';
  status?: 'waiting' | 'in_progress' | 'finished';
}

interface Square {
  row: number;
  col: number;
  piece: string;
}

function App() {
  const [game, setGame] = useState<GameState>({});
  const [selectedSquare, setSelectedSquare] = useState<Square | null>(null);
  const [debugBoard, setDebugBoard] = useState<string>('');
  const apiEndpoint = 'https://rd2ll5az83.execute-api.us-east-1.amazonaws.com/prod';

  const createNewGame = async () => {
    try {
      const response = await fetch(`${apiEndpoint}/games`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to create game');
      }

      const newGame = await response.json();
      console.log('New game state:', newGame);
      setDebugBoard(JSON.stringify(newGame.board, null, 2));
      
      // Initialize the board if it's not provided
      if (!newGame.board) {
        newGame.board = [
          ['b', '', 'b', '', 'b', '', 'b', ''],
          ['', 'b', '', 'b', '', 'b', '', 'b'],
          ['b', '', 'b', '', 'b', '', 'b', ''],
          ['', '', '', '', '', '', '', ''],
          ['', '', '', '', '', '', '', ''],
          ['', 'r', '', 'r', '', 'r', '', 'r'],
          ['r', '', 'r', '', 'r', '', 'r', ''],
          ['', 'r', '', 'r', '', 'r', '', 'r']
        ];
      }
      
      setGame(newGame);
      setSelectedSquare(null);
    } catch (error) {
      console.error('Error creating game:', error);
      alert('Failed to create new game. Please try again.');
    }
  };

  const handleSquareClick = async (row: number, col: number) => {
    if (!game.gameId || game.status === 'finished') return;
    
    const piece = game.board?.[row]?.[col];
    console.log('Clicked square:', row, col);
    console.log('Current piece:', piece);

    // If no square is selected and the clicked square has a piece of the current player's color
    if (!selectedSquare && piece && 
        ((game.currentPlayer === 'red' && piece.toLowerCase() === 'r') ||
         (game.currentPlayer === 'black' && piece.toLowerCase() === 'b'))) {
      setSelectedSquare({ row, col, piece });
      return;
    }

    // If a square is already selected, try to make a move
    if (selectedSquare) {
      try {
        const response = await fetch(`${apiEndpoint}/games/${game.gameId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            fromRow: selectedSquare.row,
            fromCol: selectedSquare.col,
            toRow: row,
            toCol: col
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to make move');
        }

        const updatedGame = await response.json();
        console.log('Updated game state:', updatedGame);
        setGame(updatedGame);
        setSelectedSquare(null);
      } catch (error) {
        console.error('Error making move:', error);
        alert('Invalid move. Please try again.');
      }
    }
  };

  const renderPiece = (piece: string) => {
    console.log('Rendering piece:', piece);
    if (piece === 'r') return '🔴';
    if (piece === 'b') return '⚫';
    if (piece === 'R') return '👑🔴';
    if (piece === 'B') return '👑⚫';
    return '';
  };

  const renderBoard = () => {
    if (!game.board) return null;

    return (
      <div>
        <div style={{ 
          display: 'inline-block',
          border: '2px solid #333',
          borderRadius: '4px',
          padding: '10px',
          backgroundColor: '#ddd'
        }}>
          {game.board.map((row, rowIndex) => (
            <div key={rowIndex} style={{ display: 'flex' }}>
              {row.map((piece, colIndex) => {
                const isSelected = selectedSquare?.row === rowIndex && selectedSquare?.col === colIndex;
                return (
                  <div
                    key={`${rowIndex}-${colIndex}`}
                    onClick={() => handleSquareClick(rowIndex, colIndex)}
                    style={{
                      width: '60px',
                      height: '60px',
                      backgroundColor: isSelected ? '#90EE90' : (rowIndex + colIndex) % 2 === 0 ? '#fff' : '#666',
                      display: 'flex',
                      justifyContent: 'center',
                      alignItems: 'center',
                      fontSize: '40px',
                      cursor: 'pointer',
                      userSelect: 'none',
                      border: isSelected ? '2px solid #32CD32' : 'none'
                    }}
                  >
                    {renderPiece(piece)}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
        <div style={{ marginTop: '20px', textAlign: 'left', whiteSpace: 'pre', fontFamily: 'monospace' }}>
          Debug Board State:
          {debugBoard}
        </div>
      </div>
    );
  };

  return (
    <div className="App" style={{ padding: '20px', textAlign: 'center' }}>
      <h1>Checkers Game</h1>
      
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
        New Game
      </button>

      {game.gameId && (
        <div>
          <p style={{ marginBottom: '10px' }}>
            <strong>Game ID:</strong> {game.gameId} | 
            <strong> Status:</strong> {game.status} |
            <strong> Current Player:</strong> {game.currentPlayer}
          </p>
          {renderBoard()}
        </div>
      )}

      {!game.gameId && (
        <div>Click "New Game" to start playing!</div>
      )}
    </div>
  );
}

export default App;
