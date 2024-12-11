import pygame
import sys
import time
import random
from gpio_handler_multi import initialize_gpio, cleanup_gpio, get_joystick_input, is_switch_pressed

# basic setting
pygame.init()

# screen setting
WIDTH, HEIGHT = 610, 660
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
GRAY = (50,50,50)
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
     "game_over": False,
    },
    {
     "board": [[0 for _ in range(COLS)] for _ in range(ROWS)],
     "current_shape": shapes[1],
     "current_pos": [0, COLS // 2 - 2],
     "current_color": colors[1],
     "score": 0,
     "game_over": False,
    },
]

# board drawing function
def draw_board(player, index):
    offset_x = index*(COLS*30+10) # seperate player 1 and 2
    
    for row in range(ROWS):
        for col in range(COLS):
            block_x = col * 30 + offset_x
            block_y = row * 30
                
            if player["board"][row][col] == 0:
                pygame.draw.rect(screen, BLACK, (block_x,block_y,30,30))
                pygame.draw.rect(screen, GRAY, (block_x,block_y,30,30),1)
            else:
                pygame.draw.rect(screen, player["board"][row][col], (block_x,block_y,30,30))
                pygame.draw.rect(screen, GRAY, (block_x,block_y,30,30),1)
    
# block moving function
def move_block(player, dx, dy):
    player["current_pos"][0] += dy
    player["current_pos"][1] += dx
    
    if check_collision(player):
        player["current_pos"][0] -= dy
        player["current_pos"][1] -= dx

# handling function
last_joystick_time=[0,0]
joystick_delay=0.04

def handle_input(player, player_index):
    global last_joystick_time
    current_time = time.time()
    
    if(current_time - last_joystick_time[player_index]) < joystick_delay:
        return
    
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
    
    last_joystick_time[player_index] = current_time

# current_block_exppressing function
def draw_current_block(player, index):
    offset_x = index*(COLS*30+10) # seperate player 1 and 2
    
    for y,row in enumerate(player["current_shape"]):
        for x,cell in enumerate(row):
            if cell:
                block_x = (player["current_pos"][1]+x) * 30 + offset_x
                block_y = (player["current_pos"][0]+y) * 30
                pygame.draw.rect(screen, player["current_color"], (block_x, block_y,30,30))
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
    rotated_shape = [list(row) for row in zip(*original_shape[::-1])] # 90 degree rotation
    
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
        player["game_over"] = True

# checking line clear setting
def clear_lines(player, opponent):
    original_board = player["board"]
    
    new_board = [row for row in player["board"] if any(cell == 0 for cell in row)]
    cleared_lines = len(original_board) - len(new_board)
    
    player["board"] = [[0]*COLS for _ in range(cleared_lines)] + new_board
    
    # plus point
    if cleared_lines > 0:
        player["score"] += cleared_lines * 10
    
    # obstacle making
    if cleared_lines > 0:
        add_obstacle(opponent, cleared_lines)

# maing obstacle function
def add_obstacle(opponent, num_lines):
    for _ in range(num_lines):
        empty_index = random.randint(0, COLS-1)
        new_row = [(0 if col == empty_index else (80,80,80)) for col in range(COLS)]
        opponent["board"].append(new_row)
        
    while len(opponent["board"]) > ROWS:
        opponent["board"].pop(0)

# game ending function
def check_game_over(player):
    for cell in player["board"][0]:
        if cell != 0:
            return True
    
    if player["game_over"]:
        return True
    
    return False

# viewing point function
def draw_scores():
    font = pygame.font.Font(None, 36)
    
    for i, player in enumerate(players):
        score_text = font.render(f"Player {i+1} Score: {player['score']}", True, WHITE)
        offset_x = i * (COLS * 30 + 10)
        offset_y = ROWS * 30 + 20
        screen.blit(score_text, (offset_x + 10, offset_y))


def draw_main_menu():
    screen.fill((0,0,0)) # background color
    
    # title text
    font = pygame.font.Font(None, 72)
    title_text = font.render("Tetris", True, (255,255,255))
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_text, title_rect)
    
    # "Game Start" button
    button_font = pygame.font.Font(None, 48)
    button_text = button_font.render("Press Enter to Start", True, (255,255,255))
    button_rect = button_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(button_text, button_rect)
    
    pygame.display.update()

# main function
def main():
    running = True
    game_state = "menu"
    drop_timer = [0,0]
    
    try:
        initialize_gpio()
        
        while running:
            if game_state == "menu":
                draw_main_menu()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            game_state = "game"
            elif game_state == "game":
                screen.fill(BLACK)
                
                for i, player in enumerate(players):
                    draw_board(player, i)
                    draw_current_block(player, i)
                    
                draw_scores()
                
                for i, player in enumerate(players):
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
