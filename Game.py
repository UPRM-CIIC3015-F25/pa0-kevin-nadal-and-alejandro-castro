import pygame, sys, random
from collections import deque

# =======================
# Global Config (Task 5)
# Change this value in different branches to cause a merge conflict.
launch_speed = 7
# =======================

# -------- Bonus Feature Toggles --------
ENABLE_MUSIC = True
ENABLE_TRAIL = True
ENABLE_FLASH = True
ENABLE_DIFFICULTY_RAMP = True

# Trail config
TRAIL_LENGTH = 10        # how many past positions
TRAIL_FADE_START = 18    # alpha for newest trail sprite (0-255)
TRAIL_FADE_END = 0       # alpha for oldest

# Flash config (on score)
FLASH_FRAMES = 8         # how many frames the flash persists
FLASH_ALPHA = 100        # transparency intensity (0-255)

# Difficulty ramp config
HITS_PER_RAMP = 3        # every N hits, speed up
SPEED_STEP = 1           # increment to speed
SPEED_CAP = 15           # max absolute speed

# Audio file names (put these files next to Game.py)
SND_HIT = "hit.wav"        # when ball hits paddle (score +1)
SND_WALL = "wall.wav"      # when ball hits walls
SND_OUT = "out.wav"        # when ball goes below (restart)
MUS_BG = "background.mp3"  # background music loop

def safe_load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None

def start_music(path, volume=0.6):
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)  # loop forever
    except Exception:
        pass

def clamp_speed_component(v, cap=SPEED_CAP):
    if v > 0:
        return min(v, cap)
    elif v < 0:
        return max(v, -cap)
    return v

def ramp_up_speed():
    """Increase both speed components slightly while keeping directions, up to SPEED_CAP."""
    global ball_speed_x, ball_speed_y
    if abs(ball_speed_x) == 0 and abs(ball_speed_y) == 0:
        return
    sx = abs(ball_speed_x) + SPEED_STEP
    sy = abs(ball_speed_y) + SPEED_STEP
    ball_speed_x = clamp_speed_component(sx if ball_speed_x > 0 else -sx)
    ball_speed_y = clamp_speed_component(sy if ball_speed_y > 0 else -sy)

def ball_movement():
    """
    Handles the movement of the ball and collision detection with the player and screen boundaries.
    """
    global ball_speed_x, ball_speed_y, score, start, flash_timer, hit_counter

    # Move the ball
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Start the ball movement when the game begins or if it's stopped
    if start or (ball_speed_x == 0 and ball_speed_y == 0):
        ball_speed_x = launch_speed * random.choice((1, -1))
        ball_speed_y = launch_speed * random.choice((1, -1))
        start = False

    # Ball collision with the player paddle (top surface check for nicer feel)
    if ball.colliderect(player):
        if abs(ball.bottom - player.top) < 12 and ball_speed_y > 0:
            score += 1
            hit_counter += 1
            ball_speed_y *= -1  # bounce upward

            # Slightly angle X based on where it hits the paddle
            offset = (ball.centerx - player.centerx) / (player.width / 2)
            ball_speed_x += int(offset * 2)

            # Limit speeds to cap
            ball_speed_x = clamp_speed_component(ball_speed_x)
            ball_speed_y = clamp_speed_component(ball_speed_y)

            # Flash effect
            if ENABLE_FLASH:
                flash_timer = FLASH_FRAMES

            # SFX
            if snd_hit:
                snd_hit.play()

            # Difficulty ramp
            if ENABLE_DIFFICULTY_RAMP and hit_counter % HITS_PER_RAMP == 0:
                ramp_up_speed()

            # Nudge the ball above the paddle to avoid sticking
            ball.bottom = player.top - 1

    # Ball collision with top boundary
    if ball.top <= 0:
        ball_speed_y *= -1
        if snd_wall:
            snd_wall.play()

    # Ball collision with left and right boundaries
    if ball.left <= 0 or ball.right >= screen_width:
        ball_speed_x *= -1
        if snd_wall:
            snd_wall.play()

    # Ball goes below the bottom boundary (missed by player)
    if ball.bottom > screen_height:
        if snd_out:
            snd_out.play()
        restart()  # Reset the game

def player_movement():
    """
    Handles the movement of the player paddle, keeping it within the screen boundaries.
    """
    player.x += player_speed  # Move the player paddle horizontally

    # Prevent the paddle from moving out of the screen boundaries
    if player.left <= 0:
        player.left = 0
    if player.right >= screen_width:
        player.right = screen_width

def restart():
    """
    Resets the ball and player score to the initial state.
    """
    global ball_speed_x, ball_speed_y, score, start, hit_counter
    ball.center = (screen_width / 2, screen_height / 2)  # Reset ball position to center
    ball_speed_y, ball_speed_x = 0, 0  # Stop ball movement
    score = 0  # Reset player score
    hit_counter = 0
    start = False  # Ball will auto-restart by logic in ball_movement()

# ---- Init ----
pygame.mixer.pre_init(44100, -16, 2, 1024)
pygame.init()
clock = pygame.time.Clock()

# Window
screen_width = 500
screen_height = 500
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Pong')

# Colors
bg_color = pygame.Color('grey12')
paddle_color = pygame.Color('cornflowerblue')
ball_color = pygame.Color('aquamarine')  # requested
text_color = paddle_color

# GameRects
ball = pygame.Rect(screen_width / 2 - 15, screen_height / 2 - 15, 30, 30)

# Paddle (Task 1: bigger)
player_height = 15
player_width = 200
player = pygame.Rect(screen_width/2 - player_width//2, screen_height - 20, player_width, player_height)

# Game vars
ball_speed_x = 0
ball_speed_y = 0
player_speed = 0
score = 0
hit_counter = 0
start = False  # SPACE still works, but ball also auto-starts

# Fonts
basic_font = pygame.font.Font('freesansbold.ttf', 32)

# Load sounds
snd_hit = safe_load_sound(SND_HIT)
snd_wall = safe_load_sound(SND_WALL)
snd_out  = safe_load_sound(SND_OUT)

# Music
if ENABLE_MUSIC:
    start_music(MUS_BG, volume=0.5)

# Flash timer (bonus effect)
flash_timer = 0

# Trail buffer (bonus effect)
trail_points = deque(maxlen=TRAIL_LENGTH)

# Main game loop
while True:
    name = "Kevin Nadal"

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_speed -= 6
            if event.key == pygame.K_RIGHT:
                player_speed += 6
            if event.key == pygame.K_SPACE:
                start = True  # optional manual start
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                player_speed += 6
            if event.key == pygame.K_RIGHT:
                player_speed -= 6

    # Update logic
    ball_movement()
    player_movement()

    # Record trail point
    if ENABLE_TRAIL:
        trail_points.appendleft((ball.centerx, ball.centery))

    # Draw
    screen.fill(bg_color)

    # Draw trail (on separate alpha surface)
    if ENABLE_TRAIL and len(trail_points) > 1:
        trail_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        for idx, (tx, ty) in enumerate(trail_points):
            # Interpolate alpha from TRAIL_FADE_START -> TRAIL_FADE_END
            alpha = TRAIL_FADE_START + (TRAIL_FADE_END - TRAIL_FADE_START) * (idx / (len(trail_points) - 1))
            alpha = max(0, min(255, int(alpha)))
            # Draw small blurred-ish ellipses for the trail
            r = max(6, 14 - idx)  # decreasing radius
            trail_color = (ball_color.r, ball_color.g, ball_color.b, alpha)
            pygame.draw.ellipse(trail_surface, trail_color, pygame.Rect(tx - r, ty - r, 2*r, 2*r))
        screen.blit(trail_surface, (0, 0))

    # Paddle & ball
    pygame.draw.rect(screen, paddle_color, player)    # paddle in cornflower blue
    pygame.draw.ellipse(screen, ball_color, ball)     # ball in aquamarine

    # Score
    score_text = basic_font.render(f'{score}', True, text_color)
    screen.blit(score_text, (screen_width/2 - 15, 10))

    # Flash overlay
    if ENABLE_FLASH and flash_timer > 0:
        flash_surf = pygame.Surface((screen_width, screen_height))
        flash_surf.set_alpha(FLASH_ALPHA)
        flash_surf.fill((255, 255, 255))
        screen.blit(flash_surf, (0, 0))
        flash_timer -= 1

    # Flip
    pygame.display.flip()
    clock.tick(60)