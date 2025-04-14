import pygame

DISPLAY_WIDTH, DISPLAY_HEIGHT = (1280, 720)

class GameObject():
    def __init__(self):
        self.image = pygame.Surface((10, 10))
        self.image.fill('White')

        self.pos_x, self.pos_y = (5, 5)
        
        self.rect = pygame.Rect((0, 0), (10, 10))
        self.rect.center = (self.pos_x, self.pos_y)

    def update(self):
        return
        
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Projectile(GameObject):
    def __init__(self, path="images\\test_projectile.png", pos=(0, 0), hb=(8, 8), s=750, dir=0):
        super().__init__()
        self.image = pygame.image.load(path).convert_alpha()

        self.pos_x, self.pos_y = pos
        
        self.rect = pygame.Rect((0, 0), hb)
        self.rect.center = (self.pos_x, self.pos_y)

        self.speed = s
        self.direction = dir
        self.onscreen = True

    def _is_onscreen(self):
        game_window_rect = pygame.Rect((0,0), (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        return game_window_rect.contains(self.rect)
    
    def update(self, dt=0):
        super().update()
        
        self.onscreen = self._is_onscreen()
        if self.onscreen:
            self.pos_x += (self.speed * self.direction) * dt
            self.rect.center = (self.pos_x, self.pos_y)
    
    def check_hit(self, rect):
        return self.rect.colliderect(rect)

class Player(GameObject):
    def __init__(self, path="images\\test_player.png", pos=(100, 360), hb=(10, 10), hp=5, s=200, cdt=0.5):
        super().__init__()

        self.image = pygame.image.load(path).convert_alpha()

        self.pos_x, self.pos_y = pos
        
        self.rect = pygame.Rect((0, 0), hb)
        self.rect.center = (self.pos_x, self.pos_y)

        self.hitpoints = hp
        self.speed = s
        self.shoot_cooldown = 0
        self.cooldown_time = cdt

    def update(self, dt=0, direction=0):
        super().update()

        self.pos_y += (self.speed * direction) * dt
        self.rect.center = (self.pos_x, self.pos_y)

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

    player = Player()
    player_projectiles = []

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
            player_projectiles.append(Projectile(pos=player.rect.center, dir=1))
            player.shoot_cooldown = 0
            print(len(player_projectiles))
        
        for index, projectile in enumerate(player_projectiles):
            if projectile.onscreen:
                projectile.update(delta_time)
            else:
                del player_projectiles[index]

        screen.fill(pygame.Color(16, 0, 26))

        player.draw(screen)
        for projectile in player_projectiles:
            projectile.draw(screen)

        pygame.display.flip()
        delta_time = clock.tick(FRAMES_PER_SECOND) / 1000
    pygame.quit()

if __name__ == '__main__':
    main()