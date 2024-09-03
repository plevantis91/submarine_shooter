import pygame 
import os 
import random

pygame.font.init()

WIDTH, HEIGHT = 750,750
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Submarine Shooter")


#Load Images
SHARK = pygame.image.load(os.path.join("assets","Shark.png"))
OCTOPUS = pygame.image.load(os.path.join("assets","Octopus.png"))
FISH = pygame.image.load(os.path.join("assets","Fish.png"))

# Player submarine
YELLOW_SUB = pygame.image.load(os.path.join("assets","yellow_sub.png"))

# Weapons
BUBBLES = pygame.image.load(os.path.join("assets","Bubble.png"))
TORPEDO = pygame.image.load(os.path.join("assets","Torpedo.png"))

# Backgroud
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets","ocean_background.png")), (WIDTH,HEIGHT))

class Weapon:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
        
    def draw(self, window):
            window.blit(self.img, (self.x, self.y))
            
    def move(self, vel):
            self.x += vel
            
    def off_screen(self, width):
            return not(self.x <= width and self.x >= 0)
        
    def collision(self, obj):
            return collide(self, obj)

class Ship:
    COOLDOWN = 30
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health 
        self.ship_img = None
        self.weapon_img = None
        self.weapons = []
        self.cool_down_counter = 0
        
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for weapon in self.weapons:
            weapon.draw(window)
            
    def move_weapon(self, vel, obj):
        self.cooldown()
        for weapon in self.weapons:
            weapon.move(vel)
            if weapon.off_screen(WIDTH):
                self.weapons.remove(weapon)
            elif weapon.collision(obj):
                obj.health -= 10
                self.weapons.remove(weapon)
        
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
        
    def shoot(self):
        if self.cool_down_counter == 0:
            weapon = Weapon(self.x+40, self.y+50, self.weapon_img)
            self.weapons.append(weapon)
            self.cool_down_counter = 1
        
    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()
    
        
class Player(Ship):
    def __init__(self,x ,y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SUB
        self.weapon_img = TORPEDO
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        
    def move_weapons(self, vel, objs):
        self.cooldown()
        for weapon in self.weapons:
            weapon.move(vel)
            if weapon.off_screen(WIDTH):
                self.weapons.remove(weapon)
            else:
                for obj in objs:
                    if weapon.collision(obj):
                        objs.remove(obj)
                        if weapon in self.weapons:
                            self.weapons.remove(weapon)
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))
    
        

        
class Enemy(Ship):
    ENEMIES_MAP = {
                "shark" : (SHARK, BUBBLES),
                "octopus": (OCTOPUS,BUBBLES),
                "fish": (FISH, BUBBLES)
    }
    def __init__(self, x, y, marine, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.weapon_img = self.ENEMIES_MAP[marine]
        self.mask = pygame.mask.from_surface(self.ship_img)
        
    def move(self, vel):
        self.x -= vel
        
    def shoot(self):
        if self.cool_down_counter == 0:
            weapon = Weapon(self.x, self.y, self.weapon_img)
            self.weapons.append(weapon)
            self.cool_down_counter = 1
        
    
def collide(obj1, obj2):
        offset_x = obj2.x - obj1.x 
        offset_y = obj2.y - obj1.y 
        return obj1.mask.overlap(obj2.mask, (offset_x,offset_y)) != None
       
def main():
    run = True
    FPS = 60
    level = 0
    lives = 3
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comcisans", 60)
    
    enemies = []
    wave_length = 5
    
    enemy_vel = 1
    weapon_vel = 4
    player_vel = 5
    
    player = Player(300, 650)
    
    lost = False
    lost_count = 0
    
    def redraw_window():
        WIN.blit(BG,(0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        
        WIN.blit(lives_label, (10,10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
                
        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)
        
        if lost:
            lost_label = lost_font.render("YOU LOST!!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
            
        pygame.display.update()
    
    while run:
        clock.tick(FPS)
        redraw_window()   
        
        if player.health <= 0:
            lives -= 1
            player.health = player.max_health
        if lives <= 0:
            lost = True
            lost_count += 1
            
        if lost:
            if lost_count > FPS * 3:
                run = False
            else: 
                continue
        
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                 # Random x position from 0 to WIDTH - 100
                 x_position = random.randrange(WIDTH + 50, WIDTH + 1500)
                 # Random y position offscreen (negative value)
                 y_position = random.randrange(0, HEIGHT - 100)
                 enemy = Enemy(x_position, y_position, random.choice(["shark", "octopus", "fish"]))
                 enemies.append(enemy)
                               
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
                
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:# left
            player.x -= player_vel 
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel 
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
            
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_weapon(-weapon_vel, player)
            
            if random.randrange(0, 2*60) == 1:
                enemy.shoot()
            
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
      
        player.move_weapons(weapon_vel, enemies)
            
def main_menu():
    title_font = pygame.font.SysFont("comicsans", 50)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 150))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()
        
                    
main_menu()
            
