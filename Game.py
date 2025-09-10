import pygame, sys, random
from collections import deque

launch_speed = 7


ENABLE_MUSIC = True
ENABLE_TRAIL = True
ENABLE_FLASH = True
ENABLE_DIFFICULTY_RAMP = True

# Trail config
TRAIL_LENGTH = 10
TRAIL_FADE_START = 18
TRAIL_FADE_END = 0


FLASH_FRAMES = 8
FLASH_ALPHA = 100


HITS_PER_RAMP = 3
SPEED_STEP = 1
SPEED_CAP = 15


SND_HIT = "hit.wav"
SND_WALL = "wall.wav"
SND_OUT = "out.wav"
MUS_BG = "background.mp3"

def safe_load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None

def start_music(path, volume=0.6):
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
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


    ball.x += ball_speed_x
    ball.y += ball_speed_y


    if start or (ball_speed_x == 0 and ball_speed_y == 0):
        ball_speed_x = launch_speed * random.choice((1, -1))
        ball_speed_y = launch_speed * random.choice((1, -1))
        start = False


    if ball.colliderect(player):
        if abs(ball.bottom - player.top) < 12 and ball_speed_y > 0:
            score += 1
            hit_counter += 1
            ball_speed_y *= -1


            offset = (ball.centerx - player.centerx) / (player.width / 2)
            ball_speed_x += int(offset * 2)


            ball_speed_x = clamp_speed_component(ball_speed_x)
            ball_speed_y = clamp_speed_component(ball_speed_y)


            if ENABLE_FLASH:
                flash_timer = FLASH_FRAMES


            if snd_hit:
                snd_hit.play()


            if ENABLE_DIFFICULTY_RAMP and hit_counter % HITS_PER_RAMP == 0:
                ramp_up_speed()


            ball.bottom = player.top - 1


    if ball.top <= 0:
        ball_speed_y *= -1
        if snd_wall:
            snd_wall.play()


    if ball.left <= 0 or ball.right >= screen_width:
        ball_speed_x *= -1
        if snd_wall:
            snd_wall.play()


    if ball.bottom > screen_height:
        if snd_out:
            snd_out.play()
        restart()

def player_movement():
    """
    Handles the movement of the player paddle, keeping it within the screen boundaries.
    """
    player.x += player_speed


    if player.left <= 0:
        player.left = 0
    if player.right >= screen_width:
        player.right = screen_width

def restart():
    """
    Resets the ball and player score to the initial state.
    """
    global ball_speed_x, ball_speed_y, score, start, hit_counter
    ball.center = (screen_width / 2, screen_height / 2)
    ball_speed_y, ball_speed_x = 0, 0
    score = 0
    hit_counter = 0
    start = False


pygame.mixer.pre_init(44100, -16, 2, 1024)
pygame.init()
clock = pygame.time.Clock()


screen_width = 500
screen_height = 500
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Pong')


bg_color = pygame.Color('grey12')
paddle_color = pygame.Color('cornflowerblue')
ball_color = pygame.Color('aquamarine')  # requested
text_color = paddle_color


ball = pygame.Rect(screen_width / 2 - 15, screen_height / 2 - 15, 30, 30)


player_height = 15
player_width = 200
player = pygame.Rect(screen_width/2 - player_width//2, screen_height - 20, player_width, player_height)


ball_speed_x = 0
ball_speed_y = 0
player_speed = 0
score = 0
hit_counter = 0
start = False


basic_font = pygame.font.Font('freesansbold.ttf', 32)


snd_hit = safe_load_sound(SND_HIT)
snd_wall = safe_load_sound(SND_WALL)
snd_out  = safe_load_sound(SND_OUT)


if ENABLE_MUSIC:
    start_music(MUS_BG, volume=0.5)


flash_timer = 0


trail_points = deque(maxlen=TRAIL_LENGTH)


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
                start = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                player_speed += 6
            if event.key == pygame.K_RIGHT:
                player_speed -= 6


    ball_movement()
    player_movement()


    if ENABLE_TRAIL:
        trail_points.appendleft((ball.centerx, ball.centery))


    screen.fill(bg_color)


    if ENABLE_TRAIL and len(trail_points) > 1:
        trail_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        for idx, (tx, ty) in enumerate(trail_points):

            alpha = TRAIL_FADE_START + (TRAIL_FADE_END - TRAIL_FADE_START) * (idx / (len(trail_points) - 1))
            alpha = max(0, min(255, int(alpha)))

            r = max(6, 14 - idx)
            trail_color = (ball_color.r, ball_color.g, ball_color.b, alpha)
            pygame.draw.ellipse(trail_surface, trail_color, pygame.Rect(tx - r, ty - r, 2*r, 2*r))
        screen.blit(trail_surface, (0, 0))


    pygame.draw.rect(screen, paddle_color, player)
    pygame.draw.ellipse(screen, ball_color, ball)


    score_text = basic_font.render(f'{score}', True, text_color)
    screen.blit(score_text, (screen_width/2 - 15, 10))


    if ENABLE_FLASH and flash_timer > 0:
        flash_surf = pygame.Surface((screen_width, screen_height))
        flash_surf.set_alpha(FLASH_ALPHA)
        flash_surf.fill((255, 255, 255))
        screen.blit(flash_surf, (0, 0))
        flash_timer -= 1


    pygame.display.flip()
    clock.tick(60)