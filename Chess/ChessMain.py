import pygame
import time

from Chess import ChessEngine
import MoveFinder
WIDTH, HEIGHT = 512, 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = HEIGHT
DIMENSION = 8
SQ_SIZE = WIDTH // DIMENSION
MAX_FPS = 15
IMAGES = {}

def load_images():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ',
              'bp', 'bR', 'bN', 'bB', 'bK', 'bQ'
             ]
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load('images/' + piece + '.png'), (SQ_SIZE, SQ_SIZE))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH + MOVE_LOG_PANEL_WIDTH, HEIGHT))
    pygame.display.set_caption('Chess')
    clock = pygame.time.Clock()
    screen.fill(pygame.Color('white'))
    moveLogFont = pygame.font.SysFont('Helvetica', 16, True, False)
    animate = False
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False # Flag: variable when a move is made
    load_images()
    running = True
    # No square is selected, keep track of the last click of the user
    sqSelected = ()
    playerClicks = [] # Keep track of player clicks (two tuples: [(6, 4), (4, 4)])
    gameOver = False
    playerOne = True # If a human is playing white, this will be true
    playerTwo = False # Same as above but for black
    while running:
        # Check to make sure that human's play:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Handle mouse event:
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = pygame.mouse.get_pos()
                    # (x, y): Location of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col) or col >= 8: # Click the square twice or clicked outside the board
                        sqSelected = () # deselect the square
                        playerClicks = [] # Clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2: # After 2nd click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        # print(move.getChessNotation())
                        for i in range (len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                sqSelected = ()
                                playerClicks = []
                        # This step is not successful
                        if not moveMade:
                            playerClicks = [sqSelected]

                # Key handler:
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    gs.undoMove()
                    moveMade = True
                if event.key == pygame.K_r:
                    # reset the board if type 'r':
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        # AI Move Finder:
        if not gameOver and not humanTurn:
            AImove = MoveFinder.findBestMove(gs, validMoves)
            if AImove is None:
                AImove = MoveFinder.findRandomMove(validMoves)
            gs.makeMove(AImove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)
        text = ""
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                text = 'Black wins by checkmate'
            else:
                text = 'White wins by checkmate'
        elif gs.staleMate:
            gameOver = True
            text = 'Stalemate'
        drawText(screen, text)


        clock.tick(MAX_FPS)
        pygame.display.flip()


def highlightSquare(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        row, col = sqSelected
        if gs.board[row][col][0] == ('w' if gs.whiteToMove else 'b'):
            s = pygame.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(pygame.Color('blue'))
            screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))
            s.fill(pygame.Color('yellow'))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen)
    highlightSquare(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs, moveLogFont)


def drawMoveLog(screen, gs, font):
    moveLogRect = pygame.Rect(WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    pygame.draw.rect(screen, pygame.Color('black'), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range (0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + '. ' + moveLog[i].getChessNotation() + ' - '
        if i + 1 < len(moveLog):
            moveString += moveLog[i + 1].getChessNotation()
        moveTexts.append(moveString)
    padding = 5
    lineSpacing = 2
    textY = padding
    for i in range (len(moveTexts)):
        text = moveTexts[i]
        textObject = font.render(text, True, pygame.Color('white'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing



def drawBoard(screen):
    global colors
    colors = [pygame.Color('white'), pygame.Color('gray')]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != '--':
                screen.blit(IMAGES[piece], (col * SQ_SIZE, row * SQ_SIZE))

def animateMove(move, screen, board, clock):
    global colors
    coords = []
    # list of coords that the animations will go through
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10 # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        row, col = (move.startRow + frame * dR/ frameCount, move.startCol + frame * dC/ frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # Erase the piece moved from its ending square:
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = pygame.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        pygame.draw.rect(screen, color, endSquare)
        # Draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # Draw moving piece
        screen.blit(IMAGES[move.pieceMoved], pygame.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        pygame.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = pygame.font.SysFont('Helvetica', 32, True, False)
    textObject = font.render(text, 0, pygame.Color('Black'))
    textLocation = pygame.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH // 2 - textObject.get_width() // 2, HEIGHT // 2 - textObject.get_height() // 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, pygame.Color('Red'))
    screen.blit(textObject, textLocation.move(2, 2))
if __name__ == '__main__':
    main()

