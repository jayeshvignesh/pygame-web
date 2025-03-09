# https://downloads.khinsider.com/game-soundtracks/album/bomberman-nes - BOMBERMAN MUSIC

import pygame
import os
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1300, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Fighters")

BORDER = pygame.Rect(WIDTH//2 - 10//2, 0, 10, HEIGHT)

BULLET_HIT_SOUND = pygame.mixer.Sound(os.path.join("Assets", "Grenade+1.mp3"))
BULLET_FIRE_SOUND = pygame.mixer.Sound(os.path.join("Assets", "Gun+Silencer.mp3"))
STAGE_SOUND = pygame.mixer.Sound(os.path.join("Assets", "bomberman_stage.mp3.mp3"))
FINAL_SONG = pygame.mixer.Sound(os.path.join("Assets", "game_over.mp3"))

HEALTH_FONT = pygame.font.SysFont("comicsans", 40)
WINNER_FONT = pygame.font.SysFont("comicsans", 100)
FINAL_WINNER_FONT = pygame.font.SysFont("comicsans", 100)

FPS = 60
VEL = 5
BULLET_VEL = 7
MAX_BULLETS = 5
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40
11/8
88/64

YELLOW_HIT = pygame.USEREVENT + 1
RED_HIT = pygame.USEREVENT + 2

YELLOW_SPACESHIP_IMAGE = pygame.image.load(
    os.path.join("Assets", "spaceship_yellow.png"))
YELLOW_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(
    YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)

RED_SPACESHIP_IMAGE = pygame.image.load(
    os.path.join("Assets", "spaceship_red.png"))
RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(
    RED_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 270)

SPACE = pygame.transform.scale(pygame.image.load(
    os.path.join("Assets", "space.png")), (WIDTH, HEIGHT))


number_of_times_run = 0

final_game_winner = "WINNER OF ALL:"

red_score = 0
yellow_score = 0

def yellow_handle_movement(keys_pressed, yellow):
    if keys_pressed[pygame.K_a] and yellow.x - VEL > 0: # left
        yellow.x -= VEL
    if keys_pressed[pygame.K_d] and yellow.x + VEL + yellow.width < BORDER.x: # Right
        yellow.x += VEL
    if keys_pressed[pygame.K_w] and yellow.y - VEL > 0:# Up
        yellow.y -= VEL
    if keys_pressed[pygame.K_s] and yellow.y + VEL + yellow.height + 15 < HEIGHT: # Down
        yellow.y += VEL

def red_handle_movement(keys_pressed, red):
    if keys_pressed[pygame.K_LEFT] and red.x - VEL > BORDER.x + BORDER.width: # left
        red.x -= VEL
    if keys_pressed[pygame.K_RIGHT] and red.x + VEL  + red.width < WIDTH: # Right
        red.x += VEL
    if keys_pressed[pygame.K_UP] and red.y - VEL > 0: # Up
        red.y -= VEL
    if keys_pressed[pygame.K_DOWN] and red.y + VEL + red.height + 15 < HEIGHT: # Down
        red.y += VEL

def handle_bullets(yellow_bullets, red_bullets, yellow, red):
    for bullet in yellow_bullets:
        bullet.x += BULLET_VEL
        if red.colliderect(bullet):
            pygame.event.post(pygame.event.Event(RED_HIT))
            yellow_bullets.remove(bullet)
        elif bullet.x > WIDTH:
            yellow_bullets.remove(bullet)

    for bullet in red_bullets:
        bullet.x -= BULLET_VEL
        if yellow.colliderect(bullet):
            pygame.event.post(pygame.event.Event(YELLOW_HIT))
            red_bullets.remove(bullet)
        elif bullet.x + bullet.width < 0:
            red_bullets.remove(bullet)

def draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health):
    WIN.blit(SPACE, (0, 0))
    pygame.draw.rect(WIN, "black", BORDER)

    red_health_text = HEALTH_FONT.render("Health: " + str(red_health), 1, "white")
    yellow_health_text = HEALTH_FONT.render("Health: " + str(yellow_health), 1, "white")
    WIN.blit(red_health_text, (WIDTH - red_health_text.get_width() - 10, 10))
    WIN.blit(yellow_health_text, (10, 10))

    WIN.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))
    WIN.blit(RED_SPACESHIP, (red.x, red.y))



    for bullet in red_bullets:
        pygame.draw.rect(WIN, "red", bullet)

    for bullet in yellow_bullets:
        pygame.draw.rect(WIN, "yellow", bullet)

    pygame.display.update()

def draw_winner(text):
    draw_text = WINNER_FONT.render(text, 1, "white")
    WIN.blit(draw_text, (WIDTH//2 - draw_text.get_width()//2, HEIGHT//2 - draw_text.get_height()//2))
    pygame.display.update()
    pygame.time.delay(4000)

def draw_final_winner(text, colour):
    WIN.blit(SPACE, (0, 0))
    draw_text = FINAL_WINNER_FONT.render(text, 1, "white")
    draw_colour = FINAL_WINNER_FONT.render(colour, 1, "white")
    WIN.blit(draw_text, (WIDTH//2 - draw_text.get_width()//2, HEIGHT//2 - draw_text.get_height()//2))
    WIN.blit(draw_colour, (WIDTH//2 - draw_colour.get_width()//2, HEIGHT//2 - draw_text.get_height()//2 + 200))
    pygame.display.update()
    FINAL_SONG.play() and pygame.time.delay(7010)

def scores(colour, score):
    colour+=score
    return colour

def draw_stage(number_of_times_run):
    number_of_times_run += 1
    if number_of_times_run>=4:
        pygame.quit()
    WIN.blit(SPACE, (0, 0))
    draw_text = WINNER_FONT.render(f"Round {number_of_times_run}", 1, "white")
    WIN.blit(draw_text, (WIDTH//2 - draw_text.get_width()//2, HEIGHT//2 - draw_text.get_height()//2))
    pygame.display.update()
    STAGE_SOUND.play() and pygame.time.delay(3010)
    return number_of_times_run


def main(number_of_times_run, red_score, yellow_score):
    red = pygame.Rect(1200, 300, SPACESHIP_HEIGHT, SPACESHIP_HEIGHT)
    yellow = pygame.Rect(100 , 300, SPACESHIP_HEIGHT, SPACESHIP_HEIGHT)

    red_bullets = []
    yellow_bullets = []

    red_health = 10
    yellow_health = 10

    clock = pygame.time.Clock()
    run = True

    if red_score >= 2:
        draw_final_winner(final_game_winner, "RED!!!")
        pygame.quit()

    if yellow_score >= 2:
        draw_final_winner(final_game_winner,  "YELLOW!!!")
        pygame.quit()

    number_of_times_run = draw_stage(number_of_times_run)
    while run:
        clock.tick(FPS)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL and len(yellow_bullets) < MAX_BULLETS:
                    bullet = pygame.Rect(
                        yellow.x + yellow.width, yellow.y + yellow.height//2 - 2, 10, 5)
                    yellow_bullets.append(bullet)
                    BULLET_FIRE_SOUND.play()

                if event.key == pygame.K_RCTRL and len(red_bullets) < MAX_BULLETS:
                    bullet = pygame.Rect(
                        red.x, red.y + red.height//2 - 2, 10, 5)
                    red_bullets.append(bullet)
                    BULLET_FIRE_SOUND.play()

            if event.type == RED_HIT:
                red_health -= 1
                BULLET_HIT_SOUND.play()

            if event.type == YELLOW_HIT:
                yellow_health -= 1
                BULLET_HIT_SOUND.play()

        winner_text = ""


        if red_health <= 0:
            winner_text = "Yellow Wins!"
            yellow_score = scores(yellow_score, 1)


        if yellow_health <= 0:
            winner_text = "Red Wins!"
            red_score = scores(red_score, 1)

        draw_window(
            red, yellow, red_bullets, yellow_bullets, red_health, yellow_health)


        if winner_text != "":
            draw_winner(winner_text)
            break


        keys_pressed = pygame.key.get_pressed()
        yellow_handle_movement(keys_pressed, yellow)
        red_handle_movement(keys_pressed, red)

        handle_bullets(yellow_bullets, red_bullets, yellow, red)

        draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health)

    print(red_score, yellow_score)
    main(number_of_times_run, red_score, yellow_score)


main(number_of_times_run, red_score, yellow_score)