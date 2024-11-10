import pygame
import random
import sys
import math

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()

# Constants
INSTRUCTIONS = True
BALL_RADIUS = 10
PAD_WIDTH = 15
PAD_HEIGHT = 80
MIN_WIDTH = 400
MIN_HEIGHT = 300
POWER_UP_CHARGE = 1
POWER_UP_SPEED_MULTIPLIER = 5
BALL_BASE_SPEED = 5
POINT_RADIUS = 3
ENLARGE_PAD_MULTIPLIER = 2.0
CURVE_FACTOR = 2.0
CURVE_DECAY = 0.5
MAX_CURVE = 0.5
curve_effect = 0.5
BOOST_DURATION = 100
BALL_STUCK_TIME = 600  # 10 segundos a 60 FPS
BALL_STUCK_THRESHOLD = 100

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
PINK = (255, 192, 203)

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
SHOP = 5
INSTRUCTIONS = 6 

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
power_up_pending = [False, False]  # Nueva variable para rastrear si el power-up está pendiente de activación
POWER_UP_DURATION = BOOST_DURATION
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

ball_start_pos = None
ball_stuck_timer = 0
ball_reset_message = False
game_won = False

# Load sounds
menu_sound = pygame.mixer.Sound("MEGALOVANIA.mp3")
goal_sound = pygame.mixer.Sound("gols-vasco.mp3")
boost_sound = pygame.mixer.Sound("boost.mp3")  # Asegúrate de tener este archivo
win_sound = pygame.mixer.Sound("Sonidoganar.mp3")
menu_sound_playing = False
goal_sound_playing = False
goal_sound_timer = 0
last_goal_time = 0
first_spawn = True

# Paddle colors
paddle_colors = [WHITE, WHITE]  # Default colors
colorful_paddle = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(10)]

def handle_power_up_activation(player):
    global power_up_pending
    if not power_up_active[player] and not power_up_pending[player]:
        power_up_pending[player] = True
        power_up_charge[player] = 0

def spawn_ball(direction, reset_type="goal"):
    global ball_pos, ball_vel, ball_rotation_speed, power_up_active, curve_effect
    global goal_sound_playing, goal_sound_timer, last_goal_time, first_spawn, power_up_active, power_up_timer
    global ball_start_pos, ball_stuck_timer, game_won
    
    current_time = pygame.time.get_ticks()
    
    # Solo reproducir el sonido de gol si es un gol real y no un reinicio por atasco
    if not first_spawn and reset_type == "goal" and current_time - last_goal_time > 3000 and not game_won:
        goal_sound.play()
        goal_sound_playing = True
        goal_sound_timer = 180
        last_goal_time = current_time
    
    ball_pos = [WIDTH // 2, HEIGHT // 2]
    ball_start_pos = ball_pos.copy()
    ball_stuck_timer = 0
    
    if direction == "LEFT":
        ball_vel = [-BALL_BASE_SPEED, random.choice([-1, 1]) * BALL_BASE_SPEED]
    elif direction == "RIGHT":
        ball_vel = [BALL_BASE_SPEED, random.choice([-1, 1]) * BALL_BASE_SPEED]
    else:
        ball_vel = [BALL_BASE_SPEED, random.choice([-1, 1]) * BALL_BASE_SPEED]

    ball_rotation_speed = random.choice([-5, 5])
    curve_effect = 0.5
    first_spawn = False
    
    power_up_active = [False, False]
    power_up_timer = [0, 0]




def new_game():
    global paddle1_pos, paddle2_pos, score, power_up_charge, power_up_active, power_up_timer
    global enlarge_pad_charge, enlarge_pad_active, enlarge_pad_timer
    global goal_sound_playing, goal_sound_timer, last_goal_time, power_up_pending
    global first_spawn, game_won, ball_start_pos, ball_stuck_timer, ball_reset_message
    
    first_spawn = True
    game_won = False
    ball_start_pos = None
    ball_stuck_timer = 0
    ball_reset_message = False
    paddle1_pos = [0, (HEIGHT - PAD_HEIGHT) // 2]
    paddle2_pos = [WIDTH - PAD_WIDTH, (HEIGHT - PAD_HEIGHT) // 2]
    score = [0, 0]
    power_up_charge = [0, 0]
    power_up_active = [False, False]
    power_up_pending = [False, False]
    power_up_timer = [0, 0]
    enlarge_pad_charge = [0, 0]
    enlarge_pad_active = [False, False]
    enlarge_pad_timer = [0, 0]
    goal_sound_playing = False
    goal_sound_timer = 0
    last_goal_time = 0
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
    global menu_sound_playing
    screen.fill(TEAL)
    font = pygame.font.Font(None, int(HEIGHT * 0.125))
    title = font.render("PONG", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT * 0.125))

    button_width = WIDTH * 0.3
    button_height = HEIGHT * 0.1

    play_button = draw_button("Jugar", WIDTH // 2 - button_width // 2, HEIGHT * 0.4, button_width, button_height, GREEN, BLUE)
    shop_button = draw_button("Tienda", WIDTH // 2 - button_width // 2, HEIGHT * 0.5, button_width, button_height, PURPLE, ORANGE)
    instructions_button = draw_button("Instrucciones", WIDTH // 2 - button_width // 2, HEIGHT * 0.6, button_width, button_height, SILVER, BLUE)
    exit_button = draw_button("Salir", WIDTH // 2 - button_width // 2, HEIGHT * 0.7, button_width, button_height, RED, ORANGE)

    if not menu_sound_playing:
        menu_sound.play(-1)
        menu_sound_playing = True

    return play_button, shop_button, instructions_button, exit_button

def draw_instructions():
    screen.fill(TEAL)
    font_title = pygame.font.Font(None, int(HEIGHT * 0.125))
    font_text = pygame.font.Font(None, int(HEIGHT * 0.04))
    
    title = font_title.render("Instrucciones", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT * 0.1))
    
    instructions = [
        "Controles:",
        "Jugador 1:",
        "- W/S para mover arriba/abajo",
        "- Q para activar boost de velocidad",
        "- E para aumentar tamaño de paleta",
        "",
        "Jugador 2:",
        "- ↑/↓ para mover arriba/abajo",
        "- → para activar boost de velocidad",
        "- ← para aumentar tamaño de paleta",
        "",
        "General:",
        "- ESC para pausar",
        "- Puedes redimensionar la ventana"
    ]
    
    y_pos = HEIGHT * 0.25
    for text in instructions:
        instruction = font_text.render(text, True, WHITE)
        screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, y_pos))
        y_pos += HEIGHT * 0.04

    button_width = WIDTH * 0.3
    button_height = HEIGHT * 0.1
    return draw_button("Volver", WIDTH // 2 - button_width // 2, HEIGHT * 0.8, button_width, button_height, RED, ORANGE)
    
def draw_game_mode_selection():
    global menu_sound_playing
    screen.fill(TEAL)
    font = pygame.font.Font(None, int(HEIGHT * 0.125))
    title = font.render("Seleccionar Modo", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT * 0.125))

    button_width = WIDTH * 0.4
    button_height = HEIGHT * 0.1

    multi_button = draw_button("Multijugador", WIDTH // 2 - button_width // 2, HEIGHT * 0.5, button_width, button_height, GREEN, BLUE)
    ai_button = draw_button("Vs Computadora", WIDTH // 2 - button_width // 2, HEIGHT * 0.7, button_width, button_height, PURPLE, ORANGE)

    if menu_sound_playing:
        menu_sound.stop()
        menu_sound_playing = False

    return multi_button, ai_button

def draw_shop():
    screen.fill(TEAL)
    font = pygame.font.Font(None, int(HEIGHT * 0.125))
    title = font.render("Tienda", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT * 0.125))

    button_width = WIDTH * 0.4
    button_height = HEIGHT * 0.1

    dotted_paddle_button1 = draw_button("Paleta con Puntos J1", WIDTH // 4 - button_width // 2, HEIGHT * 0.5, button_width, button_height, GREEN, BLUE)
    dotted_paddle_button2 = draw_button("Paleta con Puntos J2", 3 * WIDTH // 4 - button_width // 2, HEIGHT * 0.5, button_width, button_height, PURPLE, ORANGE)
    back_button = draw_button("Volver", WIDTH // 2 - button_width // 2, HEIGHT * 0.7, button_width, button_height, RED, ORANGE)

    return dotted_paddle_button1, dotted_paddle_button2, back_button

def draw_game():
    screen.fill(TEAL)
    
    pygame.draw.line(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
    
    # Draw ball with rotation effect
    rotated_ball = pygame.Surface((BALL_RADIUS * 2, BALL_RADIUS * 2), pygame.SRCALPHA)
    pygame.draw.circle(rotated_ball, WHITE, (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS)
    pygame.draw.line(rotated_ball, BLACK, (BALL_RADIUS, BALL_RADIUS), (BALL_RADIUS * 2, BALL_RADIUS), 2)
    rotated_ball = pygame.transform.rotate(rotated_ball, ball_rotation)
    ball_rect = rotated_ball.get_rect(center=(int(ball_pos[0]), int(ball_pos[1])))
    screen.blit(rotated_ball, ball_rect.topleft)
    
    # Draw fire particles
    for particle in fire_particles:
        pygame.draw.circle(screen, particle['color'], (int(particle['x']), int(particle['y'])), particle['radius'])
    
    # Draw paddles with boost color
    paddle1_height = PAD_HEIGHT * ENLARGE_PAD_MULTIPLIER if enlarge_pad_active[0] else PAD_HEIGHT
    paddle2_height = PAD_HEIGHT * ENLARGE_PAD_MULTIPLIER if enlarge_pad_active[1] else PAD_HEIGHT
    
    # Determinar color de las paletas basado en el estado del boost
    paddle1_color = YELLOW if power_up_active[0] else WHITE
    paddle2_color = YELLOW if power_up_active[1] else WHITE

    if ball_reset_message:
        font = pygame.font.Font(None, int(HEIGHT * 0.05))
        reset_text = font.render("Presiona R para reiniciar la pelota", True, WHITE)
        screen.blit(reset_text, (WIDTH // 2 - reset_text.get_width() // 2, HEIGHT * 0.1))
    
    # Dibujar paleta 1
    if paddle_colors[0] == "dotted":
        pygame.draw.rect(screen, paddle1_color, (*paddle1_pos, PAD_WIDTH, paddle1_height))
        for i in range(5):
            y_pos = paddle1_pos[1] + (i + 1) * paddle1_height // 6
            pygame.draw.circle(screen, PINK, (paddle1_pos[0] + PAD_WIDTH//2, y_pos), POINT_RADIUS, 0)
    else:
        pygame.draw.rect(screen, paddle1_color, (*paddle1_pos, PAD_WIDTH, paddle1_height))
    
    # Dibujar paleta 2
    if paddle_colors[1] == "dotted":
        pygame.draw.rect(screen, paddle2_color, (*paddle2_pos, PAD_WIDTH, paddle2_height))
        for i in range(5):
            y_pos = paddle2_pos[1] + (i + 1) * paddle2_height // 6
            pygame.draw.circle(screen, PINK, (paddle2_pos[0] + PAD_WIDTH//2, y_pos), POINT_RADIUS, 0)
    else:
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
    global ball_pos, ball_vel, score, game_state, power_up_charge, power_up_active, power_up_timer
    global ball_rotation, ball_rotation_speed, fire_particles, enlarge_pad_charge, enlarge_pad_active, enlarge_pad_timer
    global curve_effect, goal_sound_playing, goal_sound_timer, power_up_pending
    global ball_start_pos, ball_stuck_timer, ball_reset_message, game_won

    # Verificar si la pelota está atascada
    if ball_start_pos is not None:
        distance_moved = math.sqrt((ball_pos[0] - ball_start_pos[0])**2 + (ball_pos[1] - ball_start_pos[1])**2)
        ball_stuck_timer += 1
        
        if ball_stuck_timer >= BALL_STUCK_TIME and distance_moved < BALL_STUCK_THRESHOLD:
            ball_reset_message = True
        else:
            ball_reset_message = False

    # Actualizar el temporizador del sonido del gol
    if goal_sound_playing and not game_won:
        goal_sound_timer -= 1
        if goal_sound_timer <= 0:
            goal_sound.stop()
            goal_sound_playing = False

    try:
        ball_vel[0] += 0
        ball_vel[1] += 0
    except TypeError:
        print(f"Error: ball_vel contiene valores no numéricos: {ball_vel}")
        ball_vel = [float(ball_vel[0]), float(ball_vel[1])]

    perpendicular_vel = [-ball_vel[1], ball_vel[0]]
    ball_vel[0] += perpendicular_vel[0] * curve_effect
    ball_vel[1] += perpendicular_vel[1] * curve_effect

    base_speed = BALL_BASE_SPEED
    if power_up_active[0] or power_up_active[1]:
        base_speed *= POWER_UP_SPEED_MULTIPLIER

    speed = math.sqrt(ball_vel[0]**2 + ball_vel[1]**2)
    ball_vel[0] = ball_vel[0] / speed * base_speed
    ball_vel[1] = ball_vel[1] / speed * base_speed

    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]
    curve_effect *= CURVE_DECAY

    ball_rotation += ball_rotation_speed

    if ball_pos[1] <= BALL_RADIUS or ball_pos[1] >= HEIGHT - BALL_RADIUS:
        ball_vel[1] = -ball_vel[1]
        ball_rotation_speed = -ball_rotation_speed

    paddle1_height = PAD_HEIGHT * ENLARGE_PAD_MULTIPLIER if enlarge_pad_active[0] else PAD_HEIGHT
    paddle2_height = PAD_HEIGHT * ENLARGE_PAD_MULTIPLIER if enlarge_pad_active[1] else PAD_HEIGHT

    if ball_pos[0] - BALL_RADIUS <= PAD_WIDTH and paddle1_pos[1] <= ball_pos[1] <= paddle1_pos[1] + paddle1_height:
        base_speed = BALL_BASE_SPEED
        
        if power_up_pending[0]:
            power_up_active[0] = True
            power_up_timer[0] = POWER_UP_DURATION
            power_up_pending[0] = False
            base_speed *= POWER_UP_SPEED_MULTIPLIER
            boost_sound.play()
        elif power_up_active[0]:
            base_speed *= POWER_UP_SPEED_MULTIPLIER
            
        ball_vel[0] = base_speed
        relative_impact = (ball_pos[1] - (paddle1_pos[1] + paddle1_height / 2)) / (paddle1_height / 2)
        ball_vel[1] = relative_impact * 5
        curve_effect = relative_impact * MAX_CURVE
        if power_up_active[0]:
            create_fire_particles()
        ball_rotation_speed = random.choice([-5, 5])
        if not power_up_active[0] and not power_up_pending[0]:
            power_up_charge[0] = min(POWER_UP_CHARGE, power_up_charge[0] + 1)

    if ball_pos[0] + BALL_RADIUS >= WIDTH - PAD_WIDTH and paddle2_pos[1] <= ball_pos[1] <= paddle2_pos[1] + paddle2_height:
        base_speed = BALL_BASE_SPEED
        
        if power_up_pending[1]:
            power_up_active[1] = True
            power_up_timer[1] = POWER_UP_DURATION
            power_up_pending[1] = False
            base_speed *= POWER_UP_SPEED_MULTIPLIER
            boost_sound.play()
        elif power_up_active[1]:
            base_speed *= POWER_UP_SPEED_MULTIPLIER
            
        ball_vel[0] = -base_speed
        relative_impact = (ball_pos[1] - (paddle2_pos[1] + paddle2_height / 2)) / (paddle2_height / 2)
        ball_vel[1] = relative_impact * 5
        curve_effect = relative_impact * MAX_CURVE
        if power_up_active[1]:
            create_fire_particles()
        ball_rotation_speed = random.choice([-5, 5])
        if not power_up_active[1] and not power_up_pending[1]:
            power_up_charge[1] = min(POWER_UP_CHARGE, power_up_charge[1] + 1)

    if ball_pos[0] < -BALL_RADIUS:
        score[1] += 1
        enlarge_pad_charge[1] = min(3, enlarge_pad_charge[1] + 1)
        spawn_ball("RIGHT", "goal")
        power_up_charge[0] = 0
        power_up_pending[0] = False  
        curve_effect = 0
        power_up_active = [False, False]
    elif ball_pos[0] > WIDTH + BALL_RADIUS:
        score[0] += 1
        enlarge_pad_charge[0] = min(3, enlarge_pad_charge[0] + 1)
        spawn_ball("LEFT", "goal")
        power_up_charge[1] = 0
        power_up_pending[1] = False  
        curve_effect = 0
        power_up_active = [False, False]
        
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
        if not game_won:
            game_won = True
            win_sound.play()
            if goal_sound_playing:
                goal_sound.stop()
                goal_sound_playing = False
        game_state = GAME_OVER



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
                    0, angle * (math.pi / 180), radius)

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
                    0, angle * (math.pi / 180), radius)

    font = pygame.font.Font(None, int(radius))
    text_surf = font.render(key_text, True, WHITE)
    text_rect = text_surf.get_rect(center=(x_pos, y_pos))
    screen.blit(text_surf, text_rect)

def create_fire_particles():
    for _ in range(5):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 3)
        fire_particles.append({
            'x': ball_pos[0],
            'y': ball_pos[1],
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed,
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
                    play_button, shop_button, instructions_button, exit_button = draw_menu()
                    if play_button:
                        game_state = GAME_MODE_SELECTION
                    elif shop_button:
                        game_state = SHOP
                    elif instructions_button:
                        game_state = INSTRUCTIONS
                    elif exit_button:
                        running = False
                elif game_state == GAME_MODE_SELECTION:
                    multi_button, ai_button = draw_game_mode_selection()
                    if multi_button:
                        game_mode = "MULTI"
                        game_state = PLAYING
                        new_game()
                        pygame.mouse.set_visible(False)  # Hide cursor during game
                    elif ai_button:
                        game_mode = "AI"
                        game_state = PLAYING
                        new_game()
                        pygame.mouse.set_visible(False)  # Hide cursor during game
                elif game_state == GAME_OVER:
                    restart_button, menu_button = draw_game_over()
                    if restart_button:
                        new_game()
                        game_state = PLAYING
                        pygame.mouse.set_visible(False)  # Hide cursor during game
                    elif menu_button:
                        game_state = MENU
                        pygame.mouse.set_visible(True)  # Show cursor in menu
                elif game_state == PAUSED:
                    resume_button, menu_button = draw_pause_menu()
                    if resume_button:
                        game_state = PLAYING
                        pygame.mouse.set_visible(False)  # Hide cursor during game
                    elif menu_button:
                        game_state = MENU
                        pygame.mouse.set_visible(True)  # Show cursor in menu
                elif game_state == SHOP:
                    dotted_paddle_button1, dotted_paddle_button2, back_button = draw_shop()
                    if dotted_paddle_button1:
                        paddle_colors[0] = "dotted"
                    elif dotted_paddle_button2:
                        paddle_colors[1] = "dotted"
                    elif back_button:
                        game_state = MENU
                
                elif game_state == INSTRUCTIONS:
                    back_button = draw_instructions()
                    if back_button:
                        game_state = MENU
        elif event.type == pygame.KEYDOWN:
            if game_state == PLAYING:
                if event.key == pygame.K_ESCAPE:
                    game_state = PAUSED
                    pygame.mouse.set_visible(True)
                elif event.key == pygame.K_q and power_up_charge[0] >= POWER_UP_CHARGE:
                    handle_power_up_activation(0)
                elif event.key == pygame.K_RIGHT and power_up_charge[1] >= POWER_UP_CHARGE:
                    handle_power_up_activation(1)
                elif event.key == pygame.K_e and enlarge_pad_charge[0] >= 3 and not enlarge_pad_active[0]:
                    enlarge_pad_active[0] = True
                    enlarge_pad_timer[0] = ENLARGE_PAD_DURATION
                    enlarge_pad_charge[0] = 0
                elif event.key == pygame.K_LEFT and enlarge_pad_charge[1] >= 3 and not enlarge_pad_active[1]:
                    enlarge_pad_active[1] = True
                    enlarge_pad_timer[1] = ENLARGE_PAD_DURATION
                    enlarge_pad_charge[1] = 0
                elif event.key == pygame.K_r and ball_reset_message:
                    spawn_ball("LEFT" if ball_pos[0] > WIDTH // 2 else "RIGHT")
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
    elif game_state == SHOP:
        draw_shop()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()