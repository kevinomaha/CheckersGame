class CheckersGame {
    constructor() {
        this.gameBoard = document.getElementById('game-board');
        this.currentTurn = document.getElementById('current-turn');
        this.gameStatus = document.getElementById('game-status');
        this.newGameButton = document.getElementById('new-game');
        this.selectedPiece = null;
        this.gameId = null;
        this.currentGame = null;

        this.apiEndpoint = ''; // Will be set after deployment
        this.initializeBoard();
        this.setupEventListeners();
        this.loadStats();
    }

    initializeBoard() {
        this.gameBoard.innerHTML = '';
        this.gameBoard.className = 'game-board';

        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const square = document.createElement('div');
                square.className = `square ${(row + col) % 2 === 0 ? 'white' : 'black'}`;
                square.dataset.row = row;
                square.dataset.col = col;
                this.gameBoard.appendChild(square);
            }
        }
    }

    setupEventListeners() {
        this.gameBoard.addEventListener('click', (e) => this.handleSquareClick(e));
        this.newGameButton.addEventListener('click', () => this.createNewGame());
    }

    async createNewGame() {
        try {
            const response = await fetch(`${this.apiEndpoint}/games`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const game = await response.json();
            this.gameId = game.gameId;
            this.currentGame = game;
            this.updateBoard();
            this.updateGameStatus();
        } catch (error) {
            console.error('Error creating new game:', error);
            this.gameStatus.textContent = 'Error creating new game';
            this.gameStatus.className = 'alert alert-danger';
        }
    }

    async loadStats() {
        try {
            const response = await fetch(`${this.apiEndpoint}/stats`);
            const stats = await response.json();
            
            document.getElementById('wins').textContent = stats.wins;
            document.getElementById('losses').textContent = stats.losses;
            document.getElementById('total-games').textContent = stats.totalGames;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    updateBoard() {
        if (!this.currentGame) return;

        const board = this.currentGame.board;
        const squares = this.gameBoard.getElementsByClassName('square');

        Array.from(squares).forEach(square => {
            const row = parseInt(square.dataset.row);
            const col = parseInt(square.dataset.col);
            
            // Clear existing pieces
            square.innerHTML = '';
            
            const piece = board[row][col];
            if (piece) {
                const pieceDiv = document.createElement('div');
                pieceDiv.className = `piece ${piece.color}${piece.king ? ' king' : ''}`;
                square.appendChild(pieceDiv);
            }
        });

        this.currentTurn.textContent = this.currentGame.currentTurn;
    }

    updateGameStatus() {
        if (!this.currentGame) {
            this.gameStatus.textContent = 'No active game';
            this.gameStatus.className = 'alert alert-warning';
            return;
        }

        if (this.currentGame.status === 'completed') {
            this.gameStatus.textContent = `Game Over! ${this.currentGame.winner} wins!`;
            this.gameStatus.className = 'alert alert-success';
            this.loadStats(); // Refresh stats after game completion
        } else {
            this.gameStatus.textContent = `${this.currentGame.currentTurn}'s turn`;
            this.gameStatus.className = 'alert alert-info';
        }
    }

    async handleSquareClick(event) {
        if (!this.currentGame || this.currentGame.status === 'completed') return;

        const square = event.target.closest('.square');
        if (!square) return;

        const row = parseInt(square.dataset.row);
        const col = parseInt(square.dataset.col);

        if (this.selectedPiece) {
            // Try to make a move
            const fromSquare = this.selectedPiece.parentElement;
            const fromRow = parseInt(fromSquare.dataset.row);
            const fromCol = parseInt(fromSquare.dataset.col);

            try {
                const response = await fetch(`${this.apiEndpoint}/games/${this.gameId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        from: [fromRow, fromCol],
                        to: [row, col]
                    })
                });

                const updatedGame = await response.json();
                if (response.ok) {
                    this.currentGame = updatedGame;
                    this.updateBoard();
                    this.updateGameStatus();
                } else {
                    console.error('Invalid move:', updatedGame.error);
                }
            } catch (error) {
                console.error('Error making move:', error);
            }

            // Clear selection
            this.selectedPiece.classList.remove('selected');
            this.selectedPiece = null;
            Array.from(this.gameBoard.getElementsByClassName('valid-move'))
                .forEach(s => s.classList.remove('valid-move'));
        } else {
            // Select a piece
            const piece = square.querySelector('.piece');
            if (piece && piece.classList.contains(this.currentGame.currentTurn)) {
                this.selectedPiece = piece;
                piece.classList.add('selected');
                this.showValidMoves(row, col);
            }
        }
    }

    showValidMoves(row, col) {
        // This is a simplified version - you might want to implement more complex logic
        const directions = this.currentGame.currentTurn === 'red' ? [[-1, -1], [-1, 1]] : [[1, -1], [1, 1]];
        
        directions.forEach(([dRow, dCol]) => {
            const newRow = row + dRow;
            const newCol = col + dCol;
            
            if (newRow >= 0 && newRow < 8 && newCol >= 0 && newCol < 8) {
                const square = this.gameBoard.children[newRow * 8 + newCol];
                if (!square.querySelector('.piece')) {
                    square.classList.add('valid-move');
                }
            }
        });
    }
}

// Initialize the game when the page loads
window.addEventListener('DOMContentLoaded', () => {
    const game = new CheckersGame();
});
