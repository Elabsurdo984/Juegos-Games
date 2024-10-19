import pygame
import random
import sys
import math

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()

# Constants
BALL_RADIUS = 10
PAD_WIDTH = 15
PAD_HEIGHT = 80
MIN_WIDTH = 400
MIN_HEIGHT = 300
POWER_UP_CHARGE = 5
POWER_UP_SPEED_MULTIPLIER = 5
ENLARGE_PAD_MULTIPLIER = 2.0

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
YELLOW = (255, 255, 0)

# Get the screen info
screen_info = pygame.display.Info()
WIDTH, HEIGHT = 800, 600

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Pong - Redimensionable con Power-ups y Efectos")

clock = pygame.time.Clock()

# Game states
MENU = 0
GAME_MODE_SELECTION = 1
PLAYING = 2
GAME_OVER = 3
PAUSED = 4

# Initialize game variables
ball_pos = [WIDTH // 2, HEIGHT // 2]
ball_vel = [0, 0]
paddle1_pos = [0, (HEIGHT - PAD_HEIGHT) // 2]
paddle2_pos = [WIDTH - PAD_WIDTH, (HEIGHT - PAD_HEIGHT) // 2]
score = [0, 0]
game_state = MENU
game_mode = None
AI_SPEED = 2

# Power-up variables
power_up_charge = [0, 0]
power_up_active = [False, False]
POWER_UP_DURATION = 180
power_up_timer = [0, 0]

# Ball effects variables
ball_rotation = 0
ball_rotation_speed = 0
fire_particles = []

# Paddle enlargement power-up variables
enlarge_pad_charge = [0, 0]
enlarge_pad_active = [False, False]
ENLARGE_PAD_DURATION = 700
enlarge_pad_timer = [0, 0]

# Load sounds
#menu_sound = pygame.mixer.Sound("MEGALOVANIA.mp3")
#goal_sound = pygame.mixer.Sound("goal_sound.wav")
#boost_sound = pygame.mixer.Sound("boost_sound.wav")
#win_sound = pygame.mixer.Sound("win_sound.wav")

def spawn_ball(direction):
    global ball_pos, ball_vel, ball_rotation_speed, power_up_active
    ball_pos = [WIDTH // 2, HEIGHT // 2]
    vel_x = random.randint(2, 3)
    vel_y = random.randint(1, 2)
    if direction == "LEFT":
        ball_vel = [-vel_x, -vel_y]
    else:
        ball_vel = [vel_x, -vel_y]
    ball_rotation_speed = random.choice([-5, 5])
    power_up_active = [False, False]  # Deactivate power-ups when spawning a new ball

def new_game():
    global paddle1_pos, paddle2_pos, score, power_up_charge, power_up_active, power_up_timer, enlarge_pad_charge, enlarge_pad_active, enlarge_pad_timer
    paddle1_pos = [0, (HEIGHT - PAD_HEIGHT) // 2]
    paddle2_pos = [WIDTH - PAD_WIDTH, (HEIGHT - PAD_HEIGHT) // 2]
    score = [0, 0]
    power_up_charge = [0, 0]
    power_up_active = [False, False]
    power_up_timer = [0, 0]
    enlarge_pad_charge = [0, 0]
    enlarge_pad_active = [False, False]
    enlarge_pad_timer = [0, 0]
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

def draw_power_up_indicator(player):
    radius = int(HEIGHT * 0.03)
    y_pos = HEIGHT - radius - 10
    if player == 0:
        x_pos = radius + 10
        key_text = "Q"
    else:
        x_pos = WIDTH - radius - 10
        key_text = "→"
    
    pygame.draw.circle(screen, WHITE, (x_pos, y_pos), radius, 5)
    
    angle = 360 * (power_up_charge[player] / POWER_UP_CHARGE)
    pygame.draw.arc(screen, YELLOW, 
                    (int(x_pos - radius), int(y_pos - radius), int(radius * 2), int(radius * 2)),
                    0, angle * (3.14159 / 180), radius)

    font = pygame.font.Font(None, int(radius))
    text_surf = font.render(key_text, True, WHITE)
    text_rect = text_surf.get_rect(center=(x_pos, y_pos))
    screen.blit(text_surf, text_rect)

def draw_enlarge_pad_indicator(player):
    radius = int(HEIGHT * 0.03)
    y_pos = HEIGHT - 3 * radius - 20
    if player == 0:
        x_pos = radius + 10
        key_text = "E"
    else:
        x_pos = WIDTH - radius - 10
        key_text = "←"
    
    pygame.draw.circle(screen, WHITE, (x_pos, y_pos), radius, 5)
    
    angle = 360 * (enlarge_pad_charge[player] / 3)
    pygame.draw.arc(screen, GREEN, 
                    (int(x_pos - radius), int(y_pos - radius), int(radius * 2), int(radius * 2)),
                    0, angle * (3.14159 / 180), radius)

    font = pygame.font.Font(None, int(radius))
    text_surf = font.render(key_text, True, WHITE)
    text_rect = text_surf.get_rect(center=(x_pos, y_pos))
    screen.blit(text_surf, text_rect)

def draw_game():
    screen.fill(TEAL)
    
    pygame.draw.line(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
    
    # Draw fire particles
    for particle in fire_particles:
        pygame.draw.circle(screen, particle['color'], (int(particle['x']), int(particle['y'])), particle['radius'])
    
    # Draw ball with rotation effect
    rotated_ball = pygame.Surface((BALL_RADIUS * 2, BALL_RADIUS * 2), pygame.SRCALPHA)
    pygame.draw.circle(rotated_ball, WHITE, (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS)
    pygame.draw.line(rotated_ball, BLACK, (BALL_RADIUS, BALL_RADIUS), (BALL_RADIUS * 2, BALL_RADIUS), 2)
    rotated_ball = pygame.transform.rotate(rotated_ball, ball_rotation)
    ball_rect = rotated_ball.get_rect(center=(int(ball_pos[0]), int(ball_pos[1])))
    screen.blit(rotated_ball, ball_rect.topleft)
    
    paddle1_color = YELLOW if power_up_active[0] else WHITE
    paddle2_color = YELLOW if power_up_active[1] else WHITE
    paddle1_height = PAD_HEIGHT * ENLARGE_PAD_MULTIPLIER if enlarge_pad_active[0] else PAD_HEIGHT
    paddle2_height = PAD_HEIGHT * ENLARGE_PAD_MULTIPLIER if enlarge_pad_active[1] else PAD_HEIGHT
    pygame.draw.rect(screen, paddle1_color, (*paddle1_pos, PAD_WIDTH, paddle1_height))
    pygame.draw.rect(screen, paddle2_color, (*paddle2_pos, PAD_WIDTH, paddle2_height))
    
    font = pygame.font.Font(None, int(HEIGHT * 0.15))
    text1 = font.render(str(score[0]), True, WHITE)
    text2 = font.render(str(score[1]), True, WHITE)
    screen.blit(text1, (WIDTH // 4, HEIGHT * 0.05))
    screen.blit(text2, (3 * WIDTH // 4 - text2.get_width(), HEIGHT * 0.05))

    draw_power_up_indicator(0)
    draw_power_up_indicator(1)
    draw_enlarge_pad_indicator(0)
    draw_enlarge_pad_indicator(1)

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

def draw_pause_menu():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))

    font = pygame.font.Font(None, int(HEIGHT * 0.125))
    title = font.render("Pausa", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT * 0.25))

    button_width = WIDTH * 0.4
    button_height = HEIGHT * 0.1

    resume_button = draw_button("Reanudar", WIDTH // 2 - button_width // 2, HEIGHT * 0.5, button_width, button_height, GREEN, BLUE)
    menu_button = draw_button("Menú Principal", WIDTH // 2 - button_width // 2, HEIGHT * 0.7, button_width, button_height, PURPLE, ORANGE)

    return resume_button, menu_button

def update_game():
    global ball_pos, ball_vel, score, game_state, power_up_charge, power_up_active, power_up_timer, ball_rotation, ball_rotation_speed, fire_particles, enlarge_pad_charge, enlarge_pad_active, enlarge_pad_timer

    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    ball_rotation += ball_rotation_speed

    if ball_pos[1] <= BALL_RADIUS or ball_pos[1] >= HEIGHT - BALL_RADIUS:
        ball_vel[1] = -ball_vel[1]
        ball_rotation_speed = -ball_rotation_speed

    paddle1_height = PAD_HEIGHT * ENLARGE_PAD_MULTIPLIER if enlarge_pad_active[0] else PAD_HEIGHT
    paddle2_height = PAD_HEIGHT * ENLARGE_PAD_MULTIPLIER if enlarge_pad_active[1] else PAD_HEIGHT

    if ball_pos[0] - BALL_RADIUS <= PAD_WIDTH and paddle1_pos[1] <= ball_pos[1] <= paddle1_pos[1] + paddle1_height:
        ball_vel[0] = abs(ball_vel[0]) * (POWER_UP_SPEED_MULTIPLIER if power_up_active[0] else 1.1)
        ball_vel[1] *= 1.1
        ball_rotation_speed = random.choice([-5, 5])
        if not power_up_active[0]:
            power_up_charge[0] = min(POWER_UP_CHARGE, power_up_charge[0] + 1)
        if power_up_active[0]:
            create_fire_particles()
    
    if ball_pos[0] + BALL_RADIUS >= WIDTH - PAD_WIDTH and paddle2_pos[1] <= ball_pos[1] <= paddle2_pos[1] + paddle2_height:
        ball_vel[0] = -abs(ball_vel[0]) * (POWER_UP_SPEED_MULTIPLIER if power_up_active[1] else 1.1)
        ball_vel[1] *= 1.1
        ball_rotation_speed = random.choice([-5, 5])
        if not power_up_active[1]:
            power_up_charge[1] = min(POWER_UP_CHARGE, power_up_charge[1] + 1)
        if power_up_active[1]:
            create_fire_particles()
    
    if ball_pos[0] < -BALL_RADIUS:
        score[1] += 1
        enlarge_pad_charge[1] = min(3, enlarge_pad_charge[1] + 1)
        spawn_ball("RIGHT")
        power_up_charge[0] = 0
        #goal_sound.play()
    elif ball_pos[0] > WIDTH + BALL_RADIUS:
        score[0] += 1
        enlarge_pad_charge[0] = min(3, enlarge_pad_charge[0] + 1)
        spawn_ball("LEFT")
        power_up_charge[1] = 0
        #goal_sound.play()
    
    for i in range(2):
        if power_up_active[i]:
            power_up_timer[i] -= 1
            if power_up_timer[i] <= 0:
                power_up_active[i] = False
        if enlarge_pad_active[i]:
            enlarge_pad_timer[i] -= 1
            if enlarge_pad_timer[i] <= 0:
                enlarge_pad_active[i] = False
    
    if power_up_active[0] or power_up_active[1]:
        create_fire_particles()
    
    for particle in fire_particles[:]:
        particle['x'] += particle['vx']
        particle['y'] += particle['vy']
        particle['radius'] -= 0.1
        if particle['radius'] <= 0:
            fire_particles.remove(particle)
    
    if score[0] >= 10 or score[1] >= 10:
        game_state = GAME_OVER
        #win_sound.play()

def create_fire_particles():
    for _ in range(5):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 3)
        fire_particles.append({
            'x': ball_pos[0],  # Start particles at the ball's position
            'y': ball_pos[1],
            'vx': ball_vel[0] * 0.5 + math.cos(angle) * speed,  # Particles move with the ball
            'vy': ball_vel[1] * 0.5 + math.sin(angle) * speed,
            'radius': random.uniform(2, 5),
            'color': random.choice([ORANGE, RED, YELLOW])
        })

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
pygame.mouse.set_visible(True)  # Make cursor visible in menus

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
                        #menu_sound.play()
                    elif exit_button:
                        running = False
                elif game_state == GAME_MODE_SELECTION:
                    multi_button, ai_button = draw_game_mode_selection()
                    if multi_button:
                        game_mode = "MULTI"
                        game_state = PLAYING
                        new_game()
                        pygame.mouse.set_visible(False)  # Hide cursor during game
                        #menu_sound.play()
                    elif ai_button:
                        game_mode = "AI"
                        game_state = PLAYING
                        new_game()
                        pygame.mouse.set_visible(False)  # Hide cursor during game
                        #menu_sound.play()
                elif game_state == GAME_OVER:
                    restart_button, menu_button = draw_game_over()
                    if restart_button:
                        new_game()
                        game_state = PLAYING
                        pygame.mouse.set_visible(False)  # Hide cursor during game
                        #menu_sound.play()
                    elif menu_button:
                        game_state = MENU
                        pygame.mouse.set_visible(True)  # Show cursor in menu
                        #menu_sound.play()
                elif game_state == PAUSED:
                    resume_button, menu_button = draw_pause_menu()
                    if resume_button:
                        game_state = PLAYING
                        pygame.mouse.set_visible(False)  # Hide cursor during game
                        #menu_sound.play()
                    elif menu_button:
                        game_state = MENU
                        pygame.mouse.set_visible(True)  # Show cursor in menu
                        #menu_sound.play()
        elif event.type == pygame.KEYDOWN:
            if game_state == PLAYING:
                if event.key == pygame.K_ESCAPE:
                    game_state = PAUSED
                    pygame.mouse.set_visible(True)  # Show cursor in pause menu
                elif event.key == pygame.K_q and power_up_charge[0] >= POWER_UP_CHARGE and not power_up_active[0]:
                    power_up_active[0] = True
                    power_up_timer[0] = POWER_UP_DURATION
                    power_up_charge[0] = 0
                    #boost_sound.play()
                elif event.key == pygame.K_RIGHT and power_up_charge[1] >= POWER_UP_CHARGE and not power_up_active[1]:
                    power_up_active[1] = True
                    power_up_timer[1] = POWER_UP_DURATION
                    power_up_charge[1] = 0
                    #boost_sound.play()
                elif event.key == pygame.K_e and enlarge_pad_charge[0] >= 3 and not enlarge_pad_active[0]:
                    enlarge_pad_active[0] = True
                    enlarge_pad_timer[0] = ENLARGE_PAD_DURATION
                    enlarge_pad_charge[0] = 0
                    #boost_sound.play()
                elif event.key == pygame.K_LEFT and enlarge_pad_charge[1] >= 3 and not enlarge_pad_active[1]:
                    enlarge_pad_active[1] = True
                    enlarge_pad_timer[1] = ENLARGE_PAD_DURATION
                    enlarge_pad_charge[1] = 0
                    #boost_sound.play()
            elif game_state == PAUSED:
                if event.key == pygame.K_ESCAPE:
                    game_state = PLAYING
                    pygame.mouse.set_visible(False)  # Hide cursor during game

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
    elif game_state == PAUSED:
        draw_pause_menu()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()