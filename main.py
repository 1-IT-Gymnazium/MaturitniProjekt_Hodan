import subprocess
import pygame
import sys
import random
from settings import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.music_manager = MusicManager()
        self.jumpscare_manager = JumpscareManager(self.screen)
        self.player = Player(self.screen)
        self.door = Door(self.screen)
        self.coins = [self.generate_coin_position() for _ in range(10)]
        self.running = True
        self.main_loop()

    def generate_coin_position(self):
        return (random.randint(0, screen_width - coin_size), random.randint(0, screen_height - coin_size))

    def check_coin_collision(self):
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.size, self.player.size)
        for coin in self.coins[:]:  # Iterujeme přes kopii seznamu mincí, abychom mohli bezpečně odstraňovat
            coin_rect = pygame.Rect(coin[0], coin[1], coin_size, coin_size)
            if player_rect.colliderect(coin_rect):
                self.coins.remove(coin)  # Odstranění mince po kolizi
                self.music_manager.pickup_sound.play()  # Přehrání zvuku sběru

    def main_loop(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            pygame.time.Clock().tick(60)
        self.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.player.handle_event(event)

    def update(self):
        player_moving_before_update = self.player.is_moving()
        player_moving_after_update = self.player.is_moving()
        player_moving = player_moving_before_update or player_moving_after_update
        current_time = pygame.time.get_ticks()
        player_moving = self.player.is_moving()
        music_playing = pygame.mixer.music.get_busy()

        self.player.update()
        self.music_manager.update()
        self.jumpscare_manager.update(music_playing, player_moving, current_time)
        self.check_coin_collision()

    def render(self):
        self.screen.fill(background)
        self.player.draw()
        self.door.draw()
        for coin in self.coins:
            pygame.draw.rect(self.screen, (255, 215, 0), (coin[0], coin[1], coin_size, coin_size))
        pygame.display.flip()

    def quit(self):
        pygame.quit()
        sys.exit()

class MusicManager:
    def __init__(self):
        pygame.mixer.music.load(r'assets/music/music.mp3')
        pygame.mixer.music.play(-1)
        self.stop_sound = pygame.mixer.Sound(r'assets/music/music-stop.mp3')
        self.footstep_sound = pygame.mixer.Sound(r'assets/sounds/footstep.mp3')
        self.pickup_sound = pygame.mixer.Sound(r'assets/sounds/pickup.mp3')
        self.last_stop_time = pygame.time.get_ticks()
        self.stop_interval = random.randint(10000, 20000)
        self.music_playing = True

    def update(self):
        current_time = pygame.time.get_ticks()
        if self.music_playing and current_time - self.last_stop_time > self.stop_interval:
            pygame.mixer.music.stop()
            self.stop_sound.play()
            self.music_playing = False
            self.last_stop_time = current_time
            self.stop_interval = random.randint(3000, 7000)  # Kratší čas pro restart hudby
        elif not self.music_playing and current_time - self.last_stop_time > self.stop_interval:
            pygame.mixer.music.play(-1)
            self.music_playing = True
            self.last_stop_time = current_time
            self.stop_interval = random.randint(10000, 20000)

class JumpscareManager:
    def __init__(self, screen):
        self.screen = screen
        self.jumpscare_sound = pygame.mixer.Sound(r'assets/sounds/jumpscare.mp3')
        self.jumpscare_image = pygame.image.load(r'assets/images/jumpscare.png').convert_alpha()
        self.jumpscare_image = pygame.transform.scale(self.jumpscare_image, (screen_width, screen_height))
        self.jumpscare_triggered = False
        self.music_stopped_time = None

    def update(self, music_playing, player_moving, current_time):
        # Zaznamená čas, kdy hudba skončila
        if not music_playing and self.music_stopped_time is None:
            self.music_stopped_time = current_time
        elif music_playing:
            self.music_stopped_time = None  # Reset, pokud hudba znovu začne hrát

        # Spustí jumpscare, pokud hudba skončila, hráč se pohybuje a uplynula více než 1 sekunda
        if self.music_stopped_time and player_moving and current_time - self.music_stopped_time > 1000 and not self.jumpscare_triggered:
            self.trigger_jumpscare()

    def trigger_jumpscare(self):
        self.jumpscare_sound.play()
        self.screen.blit(self.jumpscare_image, (0, 0))
        pygame.display.flip()
        pygame.time.wait(2000)  # Jumpscare je zobrazen 2 sekundy
        self.jumpscare_triggered = False
        self.music_stopped_time = None

class Player:
    def __init__(self, screen):
        self.screen = screen
        self.x = screen_width // 2
        self.y = screen_height // 2
        self.speed = player_speed
        self.size = player_size
        # Přidáme směrové proměnné pro sledování pohybu
        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False

    def handle_event(self, event):
        # Aktivace pohybu při stisku klávesy
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.move_left = True
            if event.key == pygame.K_RIGHT:
                self.move_right = True
            if event.key == pygame.K_UP:
                self.move_up = True
            if event.key == pygame.K_DOWN:
                self.move_down = True

        # Deaktivace pohybu při uvolnění klávesy
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                self.move_left = False
            if event.key == pygame.K_RIGHT:
                self.move_right = False
            if event.key == pygame.K_UP:
                self.move_up = False
            if event.key == pygame.K_DOWN:
                self.move_down = False

    def is_moving(self):
        return self.move_left or self.move_right or self.move_up or self.move_down

    def update(self):
        # Aktualizace pozice na základě směrových proměnných
        if self.move_left:
            self.x -= self.speed
        if self.move_right:
            self.x += self.speed
        if self.move_up:
            self.y -= self.speed
        if self.move_down:
            self.y += self.speed

        # Omezení pohybu hráče na herní plochu
        self.x = max(0, min(self.x, screen_width - self.size))
        self.y = max(0, min(self.y, screen_height - self.size))

    def draw(self):
        pygame.draw.rect(self.screen, white, (self.x, self.y, self.size, self.size))

class Door:
    def __init__(self, screen):
        self.screen = screen
        self.x, self.y = self.generate_random_door_position()

    def generate_random_door_position(self):
        edge = random.choice(["top", "bottom", "left", "right"])
        if edge == "top":
            return random.randint(0, screen_width - door_width), 0
        elif edge == "bottom":
            return random.randint(0, screen_width - door_width), screen_height - door_height
        elif edge == "left":
            return 0, random.randint(0, screen_height - door_height)
        else:  # edge == "right"
            return screen_width - door_width, random.randint(0, screen_height - door_height)

    def draw(self):
        if len(coins) == 0:  # Předpokládáme, že existuje reference na instanci hry
            pygame.draw.rect(self.screen, door_color, (self.x, self.y, door_width, door_height))

if __name__ == "__main__":
    Game()
