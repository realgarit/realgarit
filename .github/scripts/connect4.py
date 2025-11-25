import os
import sys
from PIL import Image, ImageDraw

# Constants
ROWS = 6
COLS = 7
TILE_SIZE = 100
PADDING = 10
BG_COLOR = (13, 17, 23)  # GitHub Dark Mode Background
BOARD_COLOR = (22, 27, 34) # Slightly lighter dark
PLAYER_1_COLOR = (216, 62, 62) # Red (Your theme)
PLAYER_2_COLOR = (255, 215, 0) # Gold/Yellow
EMPTY_COLOR = (48, 54, 61)     # Empty slot color

def create_board_image(board_state, output_path="connect4.png"):
    width = COLS * TILE_SIZE + (COLS + 1) * PADDING
    height = ROWS * TILE_SIZE + (ROWS + 1) * PADDING
    
    img = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Draw Board Background
    draw.rectangle(
        [0, 0, width, height],
        fill=BOARD_COLOR,
        outline=None
    )

    for r in range(ROWS):
        for c in range(COLS):
            x = PADDING + c * (TILE_SIZE + PADDING)
            y = PADDING + r * (TILE_SIZE + PADDING)
            
            # Determine color based on state
            # 0 = Empty, 1 = Player 1, 2 = Player 2
            state = board_state[r][c]
            if state == 1:
                color = PLAYER_1_COLOR
            elif state == 2:
                color = PLAYER_2_COLOR
            else:
                color = EMPTY_COLOR
            
            draw.ellipse([x, y, x + TILE_SIZE, y + TILE_SIZE], fill=color)
            
    img.save(output_path)

def load_state(state_str):
    # Expected format: "0000000,0000000,..." (6 rows of 7 digits)
    if not state_str:
        return [[0]*COLS for _ in range(ROWS)]
    
    rows = state_str.split(',')
    board = []
    for r in rows:
        board.append([int(x) for x in r])
    return board

def save_state(board):
    return ",".join(["".join(map(str, row)) for row in board])

def drop_piece(board, col, player):
    if col < 0 or col >= COLS:
        return False, "Invalid column"
    
    # Find lowest empty spot
    for r in range(ROWS-1, -1, -1):
        if board[r][col] == 0:
            board[r][col] = player
            return True, None
            
    return False, "Column full"

def check_win(board, player):
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS-3):
            if all(board[r][c+i] == player for i in range(4)):
                return True

    # Vertical
    for r in range(ROWS-3):
        for c in range(COLS):
            if all(board[r+i][c] == player for i in range(4)):
                return True

    # Diagonal /
    for r in range(3, ROWS):
        for c in range(COLS-3):
            if all(board[r-i][c+i] == player for i in range(4)):
                return True

    # Diagonal \
    for r in range(ROWS-3):
        for c in range(COLS-3):
            if all(board[r+i][c+i] == player for i in range(4)):
                return True
                
    return False

def main():
    # Get arguments from environment
    # STATE_FILE: path to text file storing "0000000,..."
    # MOVE: column number (1-7) from issue title
    # ACTOR: who triggered it
    
    move_col = int(os.environ.get('MOVE_COL', '0')) - 1 # Convert 1-based to 0-based
    actor = os.environ.get('ACTOR', 'Unknown')
    
    # Initialize or Load State
    state_file = 'connect4_state.txt'
    if os.path.exists(state_file):
        with open(state_file, 'r') as f:
            current_state_str = f.read().strip()
    else:
        current_state_str = ""
        
    board = load_state(current_state_str)
    
    # Determine current player
    # Simple logic: Count pieces. If even, Player 1. If odd, Player 2.
    total_pieces = sum(row.count(1) + row.count(2) for row in board)
    current_player = 1 if total_pieces % 2 == 0 else 2
    
    print(f"Player {current_player} ({actor}) moving to column {move_col+1}")
    
    success, msg = drop_piece(board, move_col, current_player)
    
    if success:
        # Check win
        if check_win(board, current_player):
            print(f"WINNER: Player {current_player}!")
            # Optional: Reset board or add visual indicator?
            # For now, let's just reset after a win for endless play?
            # Or keep it and require manual reset. Let's auto-reset for fun.
            board = [[0]*COLS for _ in range(ROWS)] # Reset
            
        # Save new state
        new_state_str = save_state(board)
        with open(state_file, 'w') as f:
            f.write(new_state_str)
            
        # Generate Image
        create_board_image(board)
        print("Board updated.")
        
    else:
        print(f"Move failed: {msg}")
        # Still generate image to be safe
        create_board_image(board)

if __name__ == "__main__":
    main()

