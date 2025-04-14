import pygame
import random

DISPLAY_WIDTH, DISPLAY_HEIGHT = (1280, 720)

class GameObject():
    def __init__(self):
        self.image = pygame.Surface((10, 10))
        self.image.fill('White')

        self.pos_x, self.pos_y = (5, 5)
        
        self.draw_rect = pygame.Rect((0, 0), (10, 10))
        self.draw_rect.center = (self.pos_x, self.pos_y)

    def update(self):
        return
        
    def draw(self, screen):
        screen.blit(self.image, self.draw_rect)

class Projectile(GameObject):
    def __init__(self, path="images\\test_projectile.png", pos=(0, 0), hb=(8, 8), s=750, dir=0, dmg=1):
        super().__init__()
        self.pos_x, self.pos_y = pos
        
        self.image = pygame.image.load(path).convert_alpha()
        self.draw_rect = self.image.get_rect()
        self.draw_rect.center = (self.pos_x, self.pos_y)

        self.hitbox_rect = pygame.Rect((0, 0), hb)
        self.hitbox_rect.center = (self.pos_x, self.pos_y)

        self.speed = s
        self.direction = dir
        self.onscreen = True
        self.damage = dmg

    def _is_onscreen(self):
        game_window_rect = pygame.Rect((0,0), (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        return game_window_rect.colliderect(self.draw_rect)
    
    def update(self, dt=0):
        super().update()
        
        self.onscreen = self._is_onscreen()
        if self.onscreen:
            self.pos_x += (self.speed * self.direction) * dt
            self.draw_rect.center = (self.pos_x, self.pos_y)
            self.hitbox_rect.center = (self.pos_x, self.pos_y)
    
    def check_hit(self, rect):
        return self.hitbox_rect.colliderect(rect)

class Player(GameObject):
    def __init__(self, path="images\\test_player.png", pos=(100, 360), lim=(0, DISPLAY_HEIGHT), hb=(20, 20), hp=5, s=200, cdt=0.5):
        super().__init__()

        self.pos_x, self.pos_y = pos
        
        self.image = pygame.image.load(path).convert_alpha()
        self.draw_rect = self.image.get_rect()
        self.draw_rect.center = (self.pos_x, self.pos_y)

        self.min_y = lim[0] + (self.draw_rect.height / 2)
        self.max_y = lim[1] - (self.draw_rect.height / 2)

        self.hitbox_rect = pygame.Rect((0, 0), hb)
        self.hitbox_rect.center = (self.pos_x, self.pos_y)

        self.hitpoints = hp
        self.speed = s
        self.shoot_cooldown = 0
        self.cooldown_time = cdt

    def update(self, dt=0, direction=0):
        super().update()

        projected_y = self.pos_y + ((self.speed * direction) * dt)
        projected_draw_rect = self.draw_rect.copy()
        projected_draw_rect.center = (self.pos_x, projected_y)

        if not projected_draw_rect.top <= self.min_y and not projected_draw_rect.bottom >= self.max_y:
            self.pos_y = projected_y
            self.draw_rect.center = (self.pos_x, self.pos_y)
            self.hitbox_rect.center = (self.pos_x, self.pos_y)

        if self.shoot_cooldown <= self.cooldown_time:
            self.shoot_cooldown += dt

class GiantKillerSpaceRobot(GameObject):
    def __init__(self, path="images\\test_gksr.png", pos=(880, 120), hb=(300, 600), hp=100, s=200, cdt=2, init_ppw=5, mp=20, fr=(0, DISPLAY_HEIGHT)):
        super().__init__()

        self.pos_x, self.pos_y = pos
        
        self.image = pygame.image.load(path).convert_alpha()
        self.draw_rect = self.image.get_rect()
        self.draw_rect.topleft = (self.pos_x, self.pos_y)

        self.hitbox_rect = pygame.Rect((980, 120), hb)

        self.hitpoints = hp
        self.speed = s
        self.shoot_cooldown = 0
        self.cooldown_time = cdt
        self.projectiles_per_wave = init_ppw

        self.projectile_origin_positions = []
        firing_range = fr
        origin_amounts = 20
        for x in range(origin_amounts):
            self.projectile_origin_positions.append((900, firing_range[0] + (((firing_range[1] - firing_range[0]) / origin_amounts) * (x + 1))))
    
    def update(self, dt=0):
        super().update()
        
        if self.shoot_cooldown <= self.cooldown_time:
            self.shoot_cooldown += dt

def main():
    FRAMES_PER_SECOND = 24
    
    pygame.init()
    pygame.display.set_caption("Shooting Stars")

    info = pygame.display.Info()
    screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))

    clock = pygame.time.Clock()
    delta_time = 0

    player = Player(lim=(120, DISPLAY_HEIGHT))
    player_projectiles = []

    gksr = GiantKillerSpaceRobot(cdt=0.2, fr=(150, 700))
    gksr_projectiles = []

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_BACKSPACE] or keys[pygame.K_ESCAPE]:
            running = False
        
        if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
            player.update(delta_time, -1)
        elif keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
            player.update(delta_time, 1)
        else:
            player.update(delta_time, 0)
        
        if keys[pygame.K_SPACE] and player.shoot_cooldown >= player.cooldown_time:
            player_projectiles.append(Projectile(pos=player.hitbox_rect.center, dir=1))
            player.shoot_cooldown = 0
        
        gksr.update(delta_time)
        if gksr.shoot_cooldown >= gksr.cooldown_time:
            for x in range(gksr.projectiles_per_wave):
                gksr_projectiles.append(Projectile(pos=random.choice(gksr.projectile_origin_positions), dir=-1))
            gksr.shoot_cooldown = 0

        for index, projectile in enumerate(player_projectiles):
            if projectile.onscreen:
                if projectile.check_hit(gksr.hitbox_rect):
                    gksr.hitpoints -= projectile.damage
                    del player_projectiles[index]
                else:
                    projectile.update(delta_time)
            else:
                del player_projectiles[index]
        
        for index, projectile in enumerate(gksr_projectiles):
            if projectile.onscreen:
                if projectile.check_hit(player.hitbox_rect):
                    player.hitpoints -= projectile.damage
                    del gksr_projectiles[index]
                    print(player.hitpoints)
                else:
                    projectile.update(delta_time)
            else:
                del gksr_projectiles[index]

        screen.fill(pygame.Color(16, 0, 26))

        gksr.draw(screen)
        player.draw(screen)

        for projectile in player_projectiles:
            projectile.draw(screen)
        
        for projectile in gksr_projectiles:
            projectile.draw(screen)

        pygame.display.flip()
        delta_time = clock.tick(FRAMES_PER_SECOND) / 1000
    pygame.quit()

if __name__ == '__main__':
    main()