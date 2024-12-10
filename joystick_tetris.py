import pygame
import sys
import time
import random
from gpio_handler import initialize_gpio, cleanup_gpio, get_joystick_input, is_switch_pressed

# basic setting
pygame.init()

# screen setting
WIDTH, HEIGHT = 300, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")

# color setting
CYAN = (0,255,255)
YELLOW = (255,255,0)
PURPLE = (128,0,128)
BLUE = (0,0,255)
RED = (255,0,0)
GREEN = (0,255,0)
ORANGE = (255,165,0)
BLACK = (0,0,0)
WHITE = (255,255,255)


colors = [CYAN,YELLOW,PURPLE,RED,GREEN,ORANGE,BLUE]

# block setting
shapes = [
    [[1,1,1,1]],  #I
    [[1,1],[1,1]],  #O
    [[0,1,0],[1,1,1]],  #T
    [[1,1,0],[0,1,1]],  #Z
    [[0,1,1],[1,1,0]],  #S
    [[1,1,1],[1,0,0]],  #L
    [[1,1,1],[0,0,1]],  #J
]

# FPS setting
clock = pygame.time.Clock()
FPS = 30

# board setting
ROWS, COLS = 20, 10
board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
current_shape = shapes[0]
current_pos = [0, COLS // 2 - 2]
current_color = colors[0]

def draw_board():
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col] != (0,0,0):
                block_x = col * 30
                block_y = row * 30
                pygame.draw.rect(screen, board[row][col], (block_x,block_y,30,30))
                pygame.draw.rect(screen, WHITE, (block_x,block_y,30,30),1)

# block moving setting
def move_block(dx, dy):
    global current_pos
    current_pos[0] += dy
    current_pos[1] += dx
    
    if check_collision():
        current_pos[0] -= dy
        current_pos[1] -= dx

# handling setting
last_joystick_time = 0
joystick_delay = 0.05

def handle_input():
    global last_joystick_time
    current_time = time.time()
    
    if (current_time - last_joystick_time) < joystick_delay:
        return
        
    x, y, sw = get_joystick_input()
    
    if x < 300:
        move_block(-1,0)
    elif x > 700:
        move_block(1,0)
        
    if y > 700:
        move_block(0,1)
    
    if sw == 0:
        drop_block()
    
    if is_switch_pressed():
        rotate_block()
    
    last_joystick_time = current_time

# current_block_exppressing setting
def draw_current_block():
    global current_color
    for y,row in enumerate(current_shape):
        for x,cell in enumerate(row):
            if cell:
                block_x = (current_pos[1]+x) * 30
                block_y = (current_pos[0]+y) * 30
                pygame.draw.rect(screen, current_color, (block_x, block_y, 30,30))
                pygame.draw.rect(screen, WHITE, (block_x, block_y, 30,30),1)

# block dropping and collision setting
def drop_block():
    global current_pos, current_shape
    current_pos[0] += 1
    
    #collision check
    if check_collision():
        current_pos[0] -= 1
        lock_block()
        spawn_new_block()
        
def rotate_block():
    global current_shape
    
    # 90 degree rotation
    rotated_shape = [list(row) for row in zip(*current_shape[::-1])]
    
    # rotation and collision checking
    original_shape = current_shape
    current_shape = rotated_shape
    if check_collision():
        current_shape = original_shape

def check_collision():
    for y,row in enumerate(current_shape):
        for x,cell in enumerate(row):
            if cell:
                new_x = current_pos[1]+x
                new_y = current_pos[0]+y
                
                if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                    return True
                
                if new_y >= 0 and board[new_y][new_x]:
                    return True
    return False
    

def lock_block():
    for y,row in enumerate(current_shape):
        for x,cell in enumerate(row):
            if cell:
                board[current_pos[0]+y][current_pos[1]+x] = current_color

def spawn_new_block():
    global current_shape, current_pos, current_color
    idx = random.randint(0,len(shapes)-1)
    current_shape = shapes[idx]
    current_color = colors[idx]
    current_pos = [0, COLS // 2 - len(current_shape[0]) // 2]
    
    if check_collision():
        print("Game Over")
        pygame.quit()
        sys.exit()

# checking line clear setting
def clear_lines():
    global board
    new_board = [row for row in board if any(cell == 0 for cell in row)]
    cleared_lines = ROWS - len(new_board)
    board = [[0]*COLS for _ in range(cleared_lines)] + new_board

# main function
def main():
    running = True
    drop_timer = 0
    
    try:
        initialize_gpio()
        
        while running:
            screen.fill(BLACK)
            draw_board()
            draw_current_block()
            
            print("Running main loop...")
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quit event detected.")
                    running = False
            
            try:
                handle_input()
            except Exception as e:
                print(f"Error in handle_input: {e}")
            
            drop_timer += 1
            if drop_timer >= FPS // 2:
                drop_block()
                drop_timer = 0
            
            clear_lines()
            pygame.display.update()
            clock.tick(FPS)
    
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print("Cleaning up GPIO...")
        cleanup_gpio()
        print("Exiting program.")
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
