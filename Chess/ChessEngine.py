class GameState:
    def __init__(self):
        # Board is an 8 * 8 2D List, each element has 2 attributes:
        # First attribute represents color: 'b', 'w'
        # Second attribute represents type of piece: 'K', 'Q', 'R', 'B', 'N', 'P'
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]
        self.whiteToMove = True
        self.moveLog = []

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        # We can undo later using moveLog
        self.moveLog.append(move)
        # Swap player turn after making move:
        self.whiteToMove = not self.whiteToMove

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove



    def getValidMoves(self):
        return self.getAllPossibleMoves()

    def getAllPossibleMoves(self):
        # Basic method for get all possible moves:
        # Make the move
        # Generate all possible moves for the opposite player
        # See if any of the moves attacks your king
        # If your king is safe, it's a valid move by doing the following
        moves = [Move((6, 4), (4, 4), self.board)]
        for row in range (len(self.board)):
            for col in range (len(self.board[row])):
                turn = self.board[row][col][0]
                # To determine the turn of the game is for black player or white player
                if (turn == 'w' and self.whiteToMove) and (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    if piece == 'p':
                        self.getPawnMoves(row, col, moves)
                    elif piece == 'R':
                        self.getRookMoves(row, col, moves)
        return moves
    def getPawnMoves(self, row, col, moves):
        pass

    def getRookMoves(self, row, col, moves):
        pass



class Move:
    # Maps keys to values:
    ranksToRows = {
        '1': 7,
        '2': 6,
        '3': 5,
        '4': 4,
        '5': 3,
        '6': 2,
        '7': 1,
        '8': 0
    }
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {
        'a': 0,
        'b': 1,
        'c': 2,
        'd': 3,
        'e': 4,
        'f': 5,
        'g': 6,
        'h': 7,
    }
    colsToFiles = {v: k for k, v in filesToCols.items()}
    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
    # Overriding the equals method:
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    def getRankFile(self, row, col):
        # a1, b2, b5
        return self.colsToFiles[col] + self.rowsToRanks[row]

