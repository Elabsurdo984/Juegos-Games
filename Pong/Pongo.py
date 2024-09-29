import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
BALL_RADIUS = 10
PAD_WIDTH = 15
PAD_HEIGHT = 80
MIN_WIDTH = 400
MIN_HEIGHT = 300

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
TEAL = (0, 128, 128)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
SILVER = (192, 192, 192)

# Get the screen info
screen_info = pygame.display.Info()
WIDTH, HEIGHT = 800, 600  # Start with a default size

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Pong - Redimensionable")

clock = pygame.time.Clock()

# Game states
MENU = 0
GAME_MODE_SELECTION = 1
PLAYING = 2
GAME_OVER = 3

# Initialize game variables
ball_pos = [WIDTH // 2, HEIGHT // 2]
ball_vel = [0, 0]
paddle1_pos = [0, (HEIGHT - PAD_HEIGHT) // 2]
paddle2_pos = [WIDTH - PAD_WIDTH, (HEIGHT - PAD_HEIGHT) // 2]
score = [0, 0]
game_state = MENU
game_mode = None
AI_SPEED = 2  # Slow speed for easy AI

def spawn_ball(direction):
    global ball_pos, ball_vel
    ball_pos = [WIDTH // 2, HEIGHT // 2]
    vel_x = random.randint(2, 3)
    vel_y = random.randint(1, 2)
    if direction == "LEFT":
        ball_vel = [-vel_x, -vel_y]
    else:
        ball_vel = [vel_x, -vel_y]

def new_game():
    global paddle1_pos, paddle2_pos, score
    paddle1_pos = [0, (HEIGHT - PAD_HEIGHT) // 2]
    paddle2_pos = [WIDTH - PAD_WIDTH, (HEIGHT - PAD_HEIGHT) // 2]
    score = [0, 0]
    spawn_ball(random.choice(["LEFT", "RIGHT"]))

def draw_button(text, x, y, width, height, inactive_color, active_color):
    mouse = pygame.mouse.get_pos()

    if x < mouse[0] < x + width and y < mouse[1] < y + height:
        pygame.draw.rect(screen, active_color, (x, y, width, height))
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, width, height))
    
    font = pygame.font.Font(None, int(height * 0.6))
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect()
    text_rect.center = (x + width // 2, y + height // 2)
    screen.blit(text_surf, text_rect)
    
    return x < mouse[0] < x + width and y < mouse[1] < y + height

def draw_menu():
    screen.fill(TEAL)
    font = pygame.font.Font(None, int(HEIGHT * 0.125))
    title = font.render("PONG", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT * 0.125))

    button_width = WIDTH * 0.3
    button_height = HEIGHT * 0.1

    play_button = draw_button("Jugar", WIDTH // 2 - button_width // 2, HEIGHT * 0.5, button_width, button_height, GREEN, BLUE)
    exit_button = draw_button("Salir", WIDTH // 2 - button_width // 2, HEIGHT * 0.7, button_width, button_height, RED, ORANGE)

    # Add resize instructions
    font = pygame.font.Font(None, int(HEIGHT * 0.04))
    instructions = font.render("Arrastra los bordes de la ventana para redimensionar", True, WHITE)
    screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT * 0.9))

    return play_button, exit_button

def draw_game_mode_selection():
    screen.fill(TEAL)
    font = pygame.font.Font(None, int(HEIGHT * 0.125))
    title = font.render("Seleccionar Modo", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT * 0.125))

    button_width = WIDTH * 0.4
    button_height = HEIGHT * 0.1

    multi_button = draw_button("Multijugador", WIDTH // 2 - button_width // 2, HEIGHT * 0.5, button_width, button_height, GREEN, BLUE)
    ai_button = draw_button("Vs Computadora", WIDTH // 2 - button_width // 2, HEIGHT * 0.7, button_width, button_height, PURPLE, ORANGE)

    return multi_button, ai_button

def draw_game():
    screen.fill(TEAL)
    
    # Draw middle line
    pygame.draw.line(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
    
    # Draw ball
    pygame.draw.circle(screen, WHITE, [int(ball_pos[0]), int(ball_pos[1])], BALL_RADIUS)
    
    # Draw paddles
    pygame.draw.rect(screen, WHITE, (*paddle1_pos, PAD_WIDTH, PAD_HEIGHT))
    pygame.draw.rect(screen, WHITE, (*paddle2_pos, PAD_WIDTH, PAD_HEIGHT))
    
    # Draw scores
    font = pygame.font.Font(None, int(HEIGHT * 0.15))
    text1 = font.render(str(score[0]), True, WHITE)
    text2 = font.render(str(score[1]), True, WHITE)
    screen.blit(text1, (WIDTH // 4, HEIGHT * 0.05))
    screen.blit(text2, (3 * WIDTH // 4 - text2.get_width(), HEIGHT * 0.05))

def draw_game_over():
    screen.fill(TEAL)
    font = pygame.font.Font(None, int(HEIGHT * 0.125))
    if score[0] >= 10:
        winner_text = font.render("¡Jugador 1 Gana!", True, WHITE)
    else:
        winner_text = font.render("¡Jugador 2 Gana!", True, WHITE)
    screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT * 0.25))

    button_width = WIDTH * 0.4
    button_height = HEIGHT * 0.1

    restart_button = draw_button("Reiniciar", WIDTH // 2 - button_width // 2, HEIGHT * 0.5, button_width, button_height, GREEN, BLUE)
    menu_button = draw_button("Menú Principal", WIDTH // 2 - button_width // 2, HEIGHT * 0.7, button_width, button_height, PURPLE, ORANGE)

    return restart_button, menu_button

def update_game():
    global ball_pos, ball_vel, score, game_state

    # Update ball position
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # Ball collision with top/bottom
    if ball_pos[1] <= BALL_RADIUS or ball_pos[1] >= HEIGHT - BALL_RADIUS:
        ball_vel[1] = -ball_vel[1]

    # Ball collision with paddles
    if PAD_WIDTH <= ball_pos[0] <= PAD_WIDTH + BALL_RADIUS:
        if paddle1_pos[1] <= ball_pos[1] <= paddle1_pos[1] + PAD_HEIGHT:
            ball_vel[0] = abs(ball_vel[0]) * 1.1
            ball_vel[1] *= 1.1
    
    if WIDTH - PAD_WIDTH - BALL_RADIUS <= ball_pos[0] <= WIDTH - PAD_WIDTH:
        if paddle2_pos[1] <= ball_pos[1] <= paddle2_pos[1] + PAD_HEIGHT:
            ball_vel[0] = -abs(ball_vel[0]) * 1.1
            ball_vel[1] *= 1.1
    
    # Scoring (ball completely passes the screen edge)
    if ball_pos[0] < -BALL_RADIUS:
        score[1] += 1
        spawn_ball("RIGHT")
    elif ball_pos[0] > WIDTH + BALL_RADIUS:
        score[0] += 1
        spawn_ball("LEFT")
    
    # Check for game over
    if score[0] >= 10 or score[1] >= 10:
        game_state = GAME_OVER

def ai_move():
    if ball_pos[1] > paddle2_pos[1] + PAD_HEIGHT // 2:
        paddle2_pos[1] = min(HEIGHT - PAD_HEIGHT, paddle2_pos[1] + AI_SPEED)
    elif ball_pos[1] < paddle2_pos[1] + PAD_HEIGHT // 2:
        paddle2_pos[1] = max(0, paddle2_pos[1] - AI_SPEED)

def resize_game(new_width, new_height):
    global WIDTH, HEIGHT, ball_pos, paddle1_pos, paddle2_pos, screen
    WIDTH = max(new_width, MIN_WIDTH)
    HEIGHT = max(new_height, MIN_HEIGHT)
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    ball_pos = [WIDTH // 2, HEIGHT // 2]
    paddle1_pos = [0, (HEIGHT - PAD_HEIGHT) // 2]
    paddle2_pos = [WIDTH - PAD_WIDTH, (HEIGHT - PAD_HEIGHT) // 2]

new_game()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            resize_game(event.w, event.h)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if game_state == MENU:
                    play_button, exit_button = draw_menu()
                    if play_button:
                        game_state = GAME_MODE_SELECTION
                    elif exit_button:
                        running = False
                elif game_state == GAME_MODE_SELECTION:
                    multi_button, ai_button = draw_game_mode_selection()
                    if multi_button:
                        game_mode = "MULTI"
                        game_state = PLAYING
                        new_game()
                    elif ai_button:
                        game_mode = "AI"
                        game_state = PLAYING
                        new_game()
                elif game_state == GAME_OVER:
                    restart_button, menu_button = draw_game_over()
                    if restart_button:
                        new_game()
                        game_state = PLAYING
                    elif menu_button:
                        game_state = MENU
    
    if game_state == MENU:
        draw_menu()
    elif game_state == GAME_MODE_SELECTION:
        draw_game_mode_selection()
    elif game_state == PLAYING:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and paddle1_pos[1] > 0:
            paddle1_pos[1] -= 5
        if keys[pygame.K_s] and paddle1_pos[1] < HEIGHT - PAD_HEIGHT:
            paddle1_pos[1] += 5
        
        if game_mode == "MULTI":
            if keys[pygame.K_UP] and paddle2_pos[1] > 0:
                paddle2_pos[1] -= 5
            if keys[pygame.K_DOWN] and paddle2_pos[1] < HEIGHT - PAD_HEIGHT:
                paddle2_pos[1] += 5
        else:  # AI mode
            ai_move()
        
        update_game()
        draw_game()
    elif game_state == GAME_OVER:
        draw_game_over()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()