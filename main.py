import asyncio
import flet as ft
import flet.canvas as cv

# Game Constants
WIDTH, HEIGHT = 1300, 750
FPS = 60
VEL = 5
BULLET_VEL = 7
MAX_BULLETS = 5
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40

class GalaxyFightersGame:
    def __init__(self, page: ft.Page):
        self.page = page
        self.keys_pressed = set()
        
        # Game State Variables
        self.number_of_times_run = 0
        self.red_score = 0
        self.yellow_score = 0
        self.game_running = False
        
        # Match/Round States
        self.reset_round()
        
        # Setup UI Components
        self.setup_audio()
        self.setup_canvas()

    def setup_audio(self):
        # Path references match your local Assets structure
        self.bullet_hit_sound = ft.Audio(src="Assets/Grenade+1.ogg")
        self.bullet_fire_sound = ft.Audio(src="Assets/Gun+Silencer.ogg")
        self.stage_sound = ft.Audio(src="Assets/bomberman_stage.mp3.ogg")
        self.final_song = ft.Audio(src="Assets/game_over.ogg")
        
        self.page.overlay.extend([
            self.bullet_hit_sound, self.bullet_fire_sound, 
            self.stage_sound, self.final_song
        ])

    def reset_round(self):
        # Spaceship initial rectangles (x, y, w, h)
        self.yellow = [100, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT]
        self.red = [1200, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT]
        
        self.yellow_bullets = [] # elements as [x, y, w, h]
        self.red_bullets = []
        
        self.yellow_health = 10
        self.red_health = 10
        self.announcement_text = ""
        self.announcement_color = ft.Colors.WHITE

    def setup_canvas(self):
        # Center separating border layout
        self.border_x = WIDTH // 2 - 5
        
        # Elements to render dynamically on our interactive game canvas
        self.canvas_elements = []
        self.game_canvas = cv.Canvas(
            elements=self.canvas_elements,
            width=WIDTH,
            height=HEIGHT,
        )

    def handle_keyboard(self, e: ft.KeyboardEvent):
        # Track holds and releases manually since Flet uses discrete event states
        if e.type == "keydown":
            self.keys_pressed.add(e.key.lower())
            # Fire bullet handlers
            if e.key.lower() == "left control" and len(self.yellow_bullets) < MAX_BULLETS:
                self.yellow_bullets.append([self.yellow[0] + self.yellow[2], self.yellow[1] + self.yellow[3]//2 - 2, 10, 5])
                self.bullet_fire_sound.play()
            if e.key.lower() == "right control" and len(self.red_bullets) < MAX_BULLETS:
                self.red_bullets.append([self.red[0], self.red[1] + self.red[3]//2 - 2, 10, 5])
                self.bullet_fire_sound.play()
        elif e.type == "keyup":
            self.keys_pressed.discard(e.key.lower())

    def update_movements(self):
        # Yellow controls (W, A, S, D)
        if "a" in self.keys_pressed and self.yellow[0] - VEL > 0:
            self.yellow[0] -= VEL
        if "d" in self.keys_pressed and self.yellow[0] + VEL + self.yellow[2] < self.border_x:
            self.yellow[0] += VEL
        if "w" in self.keys_pressed and self.yellow[1] - VEL > 0:
            self.yellow[1] -= VEL
        if "s" in self.keys_pressed and self.yellow[1] + VEL + self.yellow[3] + 15 < HEIGHT:
            self.yellow[1] += VEL

        # Red controls (Arrow Keys)
        if "arrow left" in self.keys_pressed and self.red[0] - VEL > self.border_x + 10:
            self.red[0] -= VEL
        if "arrow right" in self.keys_pressed and self.red[0] + VEL + self.red[2] < WIDTH:
            self.red[0] += VEL
        if "arrow up" in self.keys_pressed and self.red[1] - VEL > 0:
            self.red[1] -= VEL
        if "arrow down" in self.keys_pressed and self.red[1] + VEL + self.red[3] + 15 < HEIGHT:
            self.red[1] += VEL

    def check_collision(self, rect1, rect2):
        # Simple AABB bounding-box collision detection
        return (rect1[0] < rect2[0] + rect2[2] and
                rect1[0] + rect1[2] > rect2[0] and
                rect1[1] < rect2[1] + rect2[3] and
                rect1[1] + rect1[3] > rect2[1])

    def update_bullets(self):
        # Process yellow ammunition paths
        for bullet in self.yellow_bullets[:]:
            bullet[0] += BULLET_VEL
            if self.check_collision(bullet, self.red):
                self.red_health -= 1
                self.bullet_hit_sound.play()
                self.yellow_bullets.remove(bullet)
            elif bullet[0] > WIDTH:
                self.yellow_bullets.remove(bullet)

        # Process red ammunition paths
        for bullet in self.red_bullets[:]:
            bullet[0] -= BULLET_VEL
            if self.check_collision(bullet, self.yellow):
                self.yellow_health -= 1
                self.bullet_hit_sound.play()
                self.red_bullets.remove(bullet)
            elif bullet[0] + bullet[2] < 0:
                self.red_bullets.remove(bullet)

    def draw_frame(self):
        # Completely re-populate frame elements array mapping the internal state
        self.canvas_elements.clear()

        # 1. Background image canvas asset mapping
        self.canvas_elements.append(cv.Image(src="Assets/space.png", x=0, y=0, width=WIDTH, height=HEIGHT))

        # 2. Divide Screen Border Line
        self.canvas_elements.append(cv.Rect(x=self.border_x, y=0, width=10, height=HEIGHT, paint=ft.Paint(color=ft.Colors.BLACK)))

        # 3. GUI Text Scores and Health readouts
        self.canvas_elements.append(cv.Text(x=10, y=10, text=f"Health: {self.yellow_health}", style=ft.TextStyle(size=40, font_family="comicsans", color=ft.Colors.WHITE)))
        self.canvas_elements.append(cv.Text(x=WIDTH - 220, y=10, text=f"Health: {self.red_health}", style=ft.TextStyle(size=40, font_family="comicsans", color=ft.Colors.WHITE)))

        # 4. Spaceship Visual Rendering Elements
        self.canvas_elements.append(cv.Image(src="Assets/spaceship_yellow.png", x=self.yellow[0], y=self.yellow[1], width=self.yellow[2], height=self.yellow[3], rotate=1.5708)) # 90 deg rad
        self.canvas_elements.append(cv.Image(src="Assets/spaceship_red.png", x=self.red[0], y=self.red[1], width=self.red[2], height=self.red[3], rotate=4.71239)) # 270 deg rad

        # 5. Projectiles rendering loops
        for b in self.yellow_bullets:
            self.canvas_elements.append(cv.Rect(x=b[0], y=b[1], width=b[2], height=b[3], paint=ft.Paint(color=ft.Colors.YELLOW)))
        for b in self.red_bullets:
            self.canvas_elements.append(cv.Rect(x=b[0], y=b[1], width=b[2], height=b[3], paint=ft.Paint(color=ft.Colors.RED)))

        # 6. Global Banner Broadcast Overlays
        if self.announcement_text:
            self.canvas_elements.append(cv.Text(
                x=WIDTH//2 - 200, y=HEIGHT//2 - 50,
                text=self.announcement_text,
                style=ft.TextStyle(size=80, font_family="comicsans", color=self.announcement_color)
            ))

        self.game_canvas.update()

    async def start_game_loop(self):
        self.game_running = True
        
        while self.game_running:
            # Win Assessment Flags
            if self.red_score >= 2 or self.yellow_score >= 2:
                self.announcement_text = "WINNER OF ALL:"
                self.announcement_color = ft.Colors.WHITE
                self.draw_frame()
                self.final_song.play()
                await asyncio.sleep(7)
                self.page.window.close()
                break

            if self.number_of_times_run >= 4:
                self.page.window.close()
                break

            # Round Initial Stage Setup Sequence
            self.reset_round()
            self.number_of_times_run += 1
            self.announcement_text = f"Round {self.number_of_times_run}"
            self.draw_frame()
            self.stage_sound.play()
            await asyncio.sleep(3)
            self.announcement_text = ""

            # Core Active Round Tracking Step
            while self.game_running:
                self.update_movements()
                self.update_bullets()

                # Health state tracking validation checks
                if self.red_health <= 0:
                    self.yellow_score += 1
                    self.announcement_text = "Yellow Wins!"
                    self.announcement_color = ft.Colors.YELLOW
                    self.draw_frame()
                    await asyncio.sleep(4)
                    break

                if self.yellow_health <= 0:
                    self.red_score += 1
                    self.announcement_text = "Red Wins!"
                    self.announcement_color = ft.Colors.RED
                    self.draw_frame()
                    await asyncio.sleep(4)
                    break

                self.draw_frame()
                await asyncio.sleep(1 / FPS) # Fixed framing clock sync ticks

def main(page: ft.Page):
    page.title = "Galaxy Fighters (Flet Edition)"
    page.window.width = WIDTH
    page.window.height = HEIGHT
    page.window.resizable = False
    page.padding = 0
    
    game = GalaxyFightersGame(page)
    page.add(game.game_canvas)
    
    # Event hooks linking tracking listeners
    page.on_keyboard_event = game.handle_keyboard
    
    # Run the background async engine thread loop safely
    page.run_task(game.start_game_loop)

ft.app(target=main)



# # https://downloads.khinsider.com/game-soundtracks/album/bomberman-nes - BOMBERMAN MUSIC

# import pygame
# import os
# pygame.font.init()
# pygame.mixer.init()

# WIDTH, HEIGHT = 1300, 750
# WIN = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("Galaxy Fighters")

# BORDER = pygame.Rect(WIDTH//2 - 10//2, 0, 10, HEIGHT)

# BULLET_HIT_SOUND = pygame.mixer.Sound(os.path.join("Assets", "Grenade+1.ogg"))
# BULLET_FIRE_SOUND = pygame.mixer.Sound(os.path.join("Assets", "Gun+Silencer.ogg"))
# STAGE_SOUND = pygame.mixer.Sound(os.path.join("Assets", "bomberman_stage.mp3.ogg"))
# FINAL_SONG = pygame.mixer.Sound(os.path.join("Assets", "game_over.ogg"))

# HEALTH_FONT = pygame.font.SysFont("comicsans", 40)
# WINNER_FONT = pygame.font.SysFont("comicsans", 100)
# FINAL_WINNER_FONT = pygame.font.SysFont("comicsans", 100)

# FPS = 60
# VEL = 5
# BULLET_VEL = 7
# MAX_BULLETS = 5
# SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40
# 11/8
# 88/64

# YELLOW_HIT = pygame.USEREVENT + 1
# RED_HIT = pygame.USEREVENT + 2

# YELLOW_SPACESHIP_IMAGE = pygame.image.load(
#     os.path.join("Assets", "spaceship_yellow.png"))
# YELLOW_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(
#     YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)

# RED_SPACESHIP_IMAGE = pygame.image.load(
#     os.path.join("Assets", "spaceship_red.png"))
# RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(
#     RED_SPACESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 270)

# SPACE = pygame.transform.scale(pygame.image.load(
#     os.path.join("Assets", "space.png")), (WIDTH, HEIGHT))


# number_of_times_run = 0

# final_game_winner = "WINNER OF ALL:"

# red_score = 0
# yellow_score = 0

# def yellow_handle_movement(keys_pressed, yellow):
#     if keys_pressed[pygame.K_a] and yellow.x - VEL > 0: # left
#         yellow.x -= VEL
#     if keys_pressed[pygame.K_d] and yellow.x + VEL + yellow.width < BORDER.x: # Right
#         yellow.x += VEL
#     if keys_pressed[pygame.K_w] and yellow.y - VEL > 0:# Up
#         yellow.y -= VEL
#     if keys_pressed[pygame.K_s] and yellow.y + VEL + yellow.height + 15 < HEIGHT: # Down
#         yellow.y += VEL

# def red_handle_movement(keys_pressed, red):
#     if keys_pressed[pygame.K_LEFT] and red.x - VEL > BORDER.x + BORDER.width: # left
#         red.x -= VEL
#     if keys_pressed[pygame.K_RIGHT] and red.x + VEL  + red.width < WIDTH: # Right
#         red.x += VEL
#     if keys_pressed[pygame.K_UP] and red.y - VEL > 0: # Up
#         red.y -= VEL
#     if keys_pressed[pygame.K_DOWN] and red.y + VEL + red.height + 15 < HEIGHT: # Down
#         red.y += VEL

# def handle_bullets(yellow_bullets, red_bullets, yellow, red):
#     for bullet in yellow_bullets:
#         bullet.x += BULLET_VEL
#         if red.colliderect(bullet):
#             pygame.event.post(pygame.event.Event(RED_HIT))
#             yellow_bullets.remove(bullet)
#         elif bullet.x > WIDTH:
#             yellow_bullets.remove(bullet)

#     for bullet in red_bullets:
#         bullet.x -= BULLET_VEL
#         if yellow.colliderect(bullet):
#             pygame.event.post(pygame.event.Event(YELLOW_HIT))
#             red_bullets.remove(bullet)
#         elif bullet.x + bullet.width < 0:
#             red_bullets.remove(bullet)

# def draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health):
#     WIN.blit(SPACE, (0, 0))
#     pygame.draw.rect(WIN, "black", BORDER)

#     red_health_text = HEALTH_FONT.render("Health: " + str(red_health), 1, "white")
#     yellow_health_text = HEALTH_FONT.render("Health: " + str(yellow_health), 1, "white")
#     WIN.blit(red_health_text, (WIDTH - red_health_text.get_width() - 10, 10))
#     WIN.blit(yellow_health_text, (10, 10))

#     WIN.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))
#     WIN.blit(RED_SPACESHIP, (red.x, red.y))



#     for bullet in red_bullets:
#         pygame.draw.rect(WIN, "red", bullet)

#     for bullet in yellow_bullets:
#         pygame.draw.rect(WIN, "yellow", bullet)

#     pygame.display.update()

# def draw_winner(text):
#     draw_text = WINNER_FONT.render(text, 1, "white")
#     WIN.blit(draw_text, (WIDTH//2 - draw_text.get_width()//2, HEIGHT//2 - draw_text.get_height()//2))
#     pygame.display.update()
#     pygame.time.delay(4000)

# def draw_final_winner(text, colour):
#     WIN.blit(SPACE, (0, 0))
#     draw_text = FINAL_WINNER_FONT.render(text, 1, "white")
#     draw_colour = FINAL_WINNER_FONT.render(colour, 1, "white")
#     WIN.blit(draw_text, (WIDTH//2 - draw_text.get_width()//2, HEIGHT//2 - draw_text.get_height()//2))
#     WIN.blit(draw_colour, (WIDTH//2 - draw_colour.get_width()//2, HEIGHT//2 - draw_text.get_height()//2 + 200))
#     pygame.display.update()
#     FINAL_SONG.play() and pygame.time.delay(7010)

# def scores(colour, score):
#     colour+=score
#     return colour

# def draw_stage(number_of_times_run):
#     number_of_times_run += 1
#     if number_of_times_run>=4:
#         pygame.quit()
#     WIN.blit(SPACE, (0, 0))
#     draw_text = WINNER_FONT.render(f"Round {number_of_times_run}", 1, "white")
#     WIN.blit(draw_text, (WIDTH//2 - draw_text.get_width()//2, HEIGHT//2 - draw_text.get_height()//2))
#     pygame.display.update()
#     STAGE_SOUND.play() and pygame.time.delay(3010)
#     return number_of_times_run


# def main(number_of_times_run, red_score, yellow_score):
#     red = pygame.Rect(1200, 300, SPACESHIP_HEIGHT, SPACESHIP_HEIGHT)
#     yellow = pygame.Rect(100 , 300, SPACESHIP_HEIGHT, SPACESHIP_HEIGHT)

#     red_bullets = []
#     yellow_bullets = []

#     red_health = 10
#     yellow_health = 10

#     clock = pygame.time.Clock()
#     run = True

#     if red_score >= 2:
#         draw_final_winner(final_game_winner, "RED!!!")
#         pygame.quit()

#     if yellow_score >= 2:
#         draw_final_winner(final_game_winner,  "YELLOW!!!")
#         pygame.quit()

#     number_of_times_run = draw_stage(number_of_times_run)
#     while run:
#         clock.tick(FPS)


#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 run = False
#                 pygame.quit()

#             if event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_LCTRL and len(yellow_bullets) < MAX_BULLETS:
#                     bullet = pygame.Rect(
#                         yellow.x + yellow.width, yellow.y + yellow.height//2 - 2, 10, 5)
#                     yellow_bullets.append(bullet)
#                     BULLET_FIRE_SOUND.play()

#                 if event.key == pygame.K_RCTRL and len(red_bullets) < MAX_BULLETS:
#                     bullet = pygame.Rect(
#                         red.x, red.y + red.height//2 - 2, 10, 5)
#                     red_bullets.append(bullet)
#                     BULLET_FIRE_SOUND.play()

#             if event.type == RED_HIT:
#                 red_health -= 1
#                 BULLET_HIT_SOUND.play()

#             if event.type == YELLOW_HIT:
#                 yellow_health -= 1
#                 BULLET_HIT_SOUND.play()

#         winner_text = ""


#         if red_health <= 0:
#             winner_text = "Yellow Wins!"
#             yellow_score = scores(yellow_score, 1)


#         if yellow_health <= 0:
#             winner_text = "Red Wins!"
#             red_score = scores(red_score, 1)

#         draw_window(
#             red, yellow, red_bullets, yellow_bullets, red_health, yellow_health)


#         if winner_text != "":
#             draw_winner(winner_text)
#             break


#         keys_pressed = pygame.key.get_pressed()
#         yellow_handle_movement(keys_pressed, yellow)
#         red_handle_movement(keys_pressed, red)

#         handle_bullets(yellow_bullets, red_bullets, yellow, red)

#         draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health)

#     print(red_score, yellow_score)
#     main(number_of_times_run, red_score, yellow_score)


# main(number_of_times_run, red_score, yellow_score)
