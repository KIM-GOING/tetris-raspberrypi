import pygame
import sys
import time
import random
from gpio_handler_multi import initialize_gpio, cleanup_gpio, get_joystick_input, is_switch_pressed

# basic setting
pygame.init()

# screen setting
WIDTH, HEIGHT = 610, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris PVP")

# color setting
CYAN = (0,255,255)
YELLOW = (255,255,0)
PURPLE = (128,0,128)
RED = (255,0,0)
GREEN = (0,255,0)
ORANGE = (255,165,0)
BLUE = (0,0,255)
BLACK = (0,0,0)
WHITE = (255,255,255)
colors = [CYAN,YELLOW,PURPLE,RED,GREEN,ORANGE,BLUE]

# block and board setting
shapes = [
    [[1,1,1,1]],  #I
    [[1,1],[1,1]],  #O
    [[0,1,0],[1,1,1]],  #T
    [[1,1,0],[0,1,1]],  #Z
    [[0,1,1],[1,1,0]],  #S
    [[1,1,1],[1,0,0]],  #L
    [[1,1,1],[0,0,1]],  #J
]
ROWS, COLS = 20, 10

# FPS setting
clock = pygame.time.Clock()
FPS = 30

# player setting
players = [
    {
     "board": [[0 for _ in range(COLS)] for _ in range(ROWS)],
     "current_shape": shapes[0],
     "current_pos": [0, COLS // 2 - 2],
     "current_color": colors[0],
     "score": 0,
    },
    {
     "board": [[0 for _ in range(COLS)] for _ in range(ROWS)],
     "current_shape": shapes[1],
     "current_pos": [0, COLS // 2 - 2],
     "current_color": colors[1],
     "score": 0,
    },
]

# board drawing function
def draw_board(player, index):
    offset_x = index*(COLS*30+10) # seperate player 1 and 2
    
    for row in range(ROWS):
        for col in range(COLS):
            if player["board"][row][col] != 0:
                block_x = col * 30 + offset_x
                block_y = row * 30
                
                pygame.draw.rect(screen, color, (block_x,block_y,30,30))
                pygame.draw.rect(screen, WHITE, (block_x,block_y,30,30),1)

# block moving function
def move_block(player, dx, dy):
    player["current_pos"][0] += dy
    player["current_pos"][1] += dx
    
    if check_collision(player):
        player["current_pos"][0] -= dy
        player["current_pos"][1] -= dx

# handling function
def handle_input(player, player_index):
    x, y, sw = get_joystick_input(player_index)
    
    if x < 300:
        move_block(player,-1,0)
    elif x > 700:
        move_block(player,1,0)
        
    if y > 700:
        move_block(player,0,1)
    
    if sw:
        drop_block(player)
    
    if is_switch_pressed(player_index):
        rotate_block(player)

# current_block_exppressing function
def draw_current_block(player, index):
    offset_x = index*(COLS*30+10) # seperate player 1 and 2
    
    for y,row in enumerate(player["current_shape"]):
        for x,cell in enumerate(row):
            if cell:
                block_x = (player["current_pos"][1]+x) * 30
                block_y = (player["current_pos"][0]+y) * 30
                pygame.draw.rect(screen, player["current_color"], (block_x, block_y, 30,30))
                pygame.draw.rect(screen, WHITE, (block_x, block_y, 30,30),1)

# block dropping and collision function
def drop_block(player):
    player["current_pos"][0] += 1
    
    #collision check
    if check_collision(player):
        player["current_pos"][0] -= 1
        lock_block(player)
        spawn_new_block(player)

# block rotation function
def rotate_block(player):
    original_shape = player["current_shape"]
    rotated_shape = [list(row) for row in zip(*current_shape[::-1])] # 90 degree rotation
    
    player["current_shape"] = rotated_shape
    # rotation and collision checking   
    if check_collision(player):
        player["current_shape"] = original_shape

# collision checking function
def check_collision(player):
    for y,row in enumerate(player["current_shape"]):
        for x,cell in enumerate(row):
            if cell:
                new_x = player["current_pos"][1]+x
                new_y = player["current_pos"][0]+y
                
                if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                    return True
                
                if new_y >= 0 and player["board"][new_y][new_x]:
                    return True
    return False
    
# block locking function
def lock_block(player):
    for y,row in enumerate(player["current_shape"]):
        for x,cell in enumerate(row):
            if cell:
                player["board"][player["current_pos"][0]+y][player["current_pos"][1]+x] = player["current_color"]

# new block making function
def spawn_new_block(player):
    idx = random.randint(0,len(shapes)-1)
    player["current_shape"] = shapes[idx]
    player["current_color"] = colors[idx]
    player["current_pos"] = [0, COLS // 2 - len(player["current_shape"][0]) // 2]
    
    if check_collision(player):
        print("Game Over")
        pygame.quit()
        sys.exit()

# checking line clear setting
def clear_lines(player, opponent):
    new_board = [row for row in player["board"] if any(cell == 0 for cell in row)]
    cleared_lines = ROWS - len(new_board)
    player["board"] = [[0]*COLS for _ in range(cleared_lines)] + new_board
    
    # plus point
    player["score"] += cleared_lines * 10
    
    # obstacle making
    if cleared_lines >0:
        add_obstacle(opponent)

# maing obstacle function
def add_obstacle(player):
    for _ in range(1):
        new_row = [random.choice([0,0, player["current_color"]]) for _ in range(COLS)]
        player["board"].insert(0,new_row)
        player["board"].pop()

# game ending function
def check_game_over(player):
    for cell in player["board"][0]:
        if cell != 0:
            return True
        return False

# main function
def main():
    running = True
    drop_timer = [0,0]
    
    try:
        initialize_gpio()
        
        while running:
            screen.fill(BLACK)
            print("Running main loop...")
            
            for i, player in enumerate(players):
                draw_board(player, i)
                draw_current_block(player, i)
                try:
                    handle_input(player, i)
                except Exception as e:
                    print(f"Error in handle_input: {e}")
                
                drop_timer[i] += 1
                if drop_timer[i] >= FPS // 2:
                    drop_block(player)
                    drop_timer[i] = 0
            
                clear_lines(player,players[1-i])
                
                if check_game_over(player):
                    print(f"player {2-i} Wins!")
                    running = False            
            
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

