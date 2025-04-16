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

class StaticImage():
    def __init__(self, path="images\\test_UI_bar.png", pos=(0, 0)):
        self.image = pygame.image.load(path).convert_alpha()
        self.draw_rect = self.image.get_rect()
        self.draw_rect.topleft = pos
    
    def draw(self, screen):
        screen.blit(self.image, self.draw_rect)

class MeterBar():
    def __init__(self, pos=(0, 0), dims=(250, 50), sm=0, col='White', amt=100):
        self.position = pos

        self.max_width = dims[0]
        self.height = dims[1]

        self.draw_rect = pygame.Rect(pos, dims)
        self.shrink_mode = sm
        self.color = col

        self.max_amount = amt
        self.amount = self.max_amount

    def update(self, new_amount):
        self.amount = new_amount
        new_width = (self.max_width * (self.amount / self.max_amount))
        self.draw_rect.update((0, 0), (new_width, self.height))

        if self.shrink_mode == 0:
            self.draw_rect.topleft = self.position
        elif self.shrink_mode == 1:
            self.draw_rect.topright = self.position
        else:
            self.draw_rect.midtop = self.position

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.draw_rect)

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

        self.hitpoints_bar = MeterBar(pos=(30, 50), dims=(200, 20), sm=0, col='Blue', amt=self.hitpoints)

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

        self.hitpoints_bar.update(self.hitpoints)

    def draw(self, screen):
        super().draw(screen)
        self.hitpoints_bar.draw(screen)

class GiantKillerSpaceRobot(GameObject):
    def __init__(self, path="images\\test_gksr_phase1.png", pos=(880, 170), hb=(300, 600), hp=100, s=200, cdt=2, init_ppw=6, mp=10, y_range=(0, DISPLAY_HEIGHT)):
        super().__init__()

        self.pos_x, self.pos_y = pos
        
        self.image = pygame.image.load(path).convert_alpha()
        self.draw_rect = self.image.get_rect()
        self.draw_rect.topleft = (self.pos_x, self.pos_y)

        self.hitbox_rect = pygame.Rect((980, 120), hb)

        self.hitpoints = hp
        self.max_hitpoints = hp
        self.attack_phase = 1
        self.speed = s
        self.shoot_cooldown = 0
        self.cooldown_time = cdt
        self.projectiles_per_wave = init_ppw

        self.projectile_origin_positions = []
        firing_range = y_range
        origin_amounts = mp
        for x in range(origin_amounts):
            self.projectile_origin_positions.append((900, firing_range[0] + (((firing_range[1] - firing_range[0]) / origin_amounts) * (x + 1))))
        
        self.hitpoints_bar = MeterBar(pos=(1230, 50), dims=(200, 20), sm=1, col='Red', amt=self.hitpoints)
    
    def update(self, dt=0):
        super().update()
        
        if self.shoot_cooldown <= self.cooldown_time:
            self.shoot_cooldown += dt
        
        health_percent = self.hitpoints / self.max_hitpoints
        if health_percent < 0.66 and self.attack_phase == 1:
            self.attack_phase = 2
        elif health_percent < 0.33 and self.attack_phase == 2:
            self.attack_phase = 3

        if self.attack_phase == 1:
            self.image = pygame.image.load('images\\test_gksr_phase1.png').convert_alpha()
            self.projectiles_per_wave = 6
            self.cooldown_time = 2.0
        elif self.attack_phase == 2:
            self.image = pygame.image.load('images\\test_gksr_phase2.png').convert_alpha()
            self.projectiles_per_wave = 5
            self.cooldown_time = 1.5
        if self.attack_phase == 3:
            self.image = pygame.image.load('images\\test_gksr_phase3.png').convert_alpha()
            self.projectiles_per_wave = 6
            self.cooldown_time = 1.0

        self.hitpoints_bar.update(self.hitpoints)
        
    def draw(self, screen):
        super().draw(screen)
        self.hitpoints_bar.draw(screen)

def choose_gksr_projectiles_origins(gksr):
    positions = []
    while len(positions) < gksr.projectiles_per_wave:
        pos = random.choice(gksr.projectile_origin_positions)
        if not pos in positions:
            positions.append(pos)
    return positions

def update_projectile_group(projectiles, delta_time, target):
    new_projectiles = []
    for projectile in projectiles:
        if projectile.onscreen:
            projectile.update(delta_time)                    
            if projectile.check_hit(target.hitbox_rect):
                target.hitpoints -= projectile.damage
            else:
                new_projectiles.append(projectile)
    return new_projectiles

def main():
    FRAMES_PER_SECOND = 24
    
    pygame.init()
    pygame.display.set_caption("Impending Doom")

    screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))

    clock = pygame.time.Clock()
    delta_time = 0

    player = Player(lim=(280, 580))
    player_projectiles = []

    gksr = GiantKillerSpaceRobot(y_range=(280, 550))
    gksr_projectiles = []

    time_left = 60.0
    time_bar = MeterBar(pos=(640, 20), dims=(500, 20), sm=2, col='Purple', amt=time_left)

    game_phase = 1
    game_end_scenario = 0

    title_card = StaticImage(path="images\\title_card.png")
    game_over_card = StaticImage(path="images\\game_over_card.png")
    victory_card = StaticImage(path="images\\victory_card.png")
    ui_background_bar = StaticImage()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_BACKSPACE] or keys[pygame.K_ESCAPE]:
            running = False
        
        if game_phase == 1:
            # display the title card
            # proceed to next game phase when player presses the space bar
            # increase gamephase to 2
            title_card.draw(screen)
            if keys[pygame.K_SPACE]:
                game_phase += 1
        elif game_phase == 2:
            # initialize player and player projectiles
            # initialize GKSR and gksr projectiles
            # increase gamephase to 3
            player = Player(lim=(280, 580), hp=10)
            player_projectiles = []

            gksr = GiantKillerSpaceRobot(y_range=(280, 550))
            gksr_projectiles = []

            game_end_scenario = 0
            
            time_left = 60.0
            time_bar = MeterBar(pos=(640, 20), dims=(500, 20), sm=2, col='Purple', amt=time_left)

            game_phase +=1
        elif game_phase == 3:
            # run the game:
            # update and draw the player and player projectiles
            # update and draw the gksr and gksr projectiles
            # ^^^ do this until:
            # 1. the player's health is depleted
            # 2. the gksr's health is depleted
            # 3. the timer runs out
            # ^^^ when this happens:
            # change the value of game_end_scenario to 1, 2, or 3 depending on which of the above happened
            # increase the gamephase to 4
            time_bar.update(time_left)

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
                positions = choose_gksr_projectiles_origins(gksr)
                for position in positions:
                    gksr_projectiles.append(Projectile(path='images\\test_gskr_projectile.png', pos=position, hb=(20,32), s=500, dir=-1))
                gksr.shoot_cooldown = 0

            player_projectiles = update_projectile_group(player_projectiles, delta_time, gksr)
            gksr_projectiles = update_projectile_group(gksr_projectiles, delta_time, player)
    
            screen.fill(pygame.Color(16, 0, 26))
            ui_background_bar.draw(screen)

            time_bar.draw(screen)
            
            gksr.draw(screen)
            player.draw(screen)

            for projectile in player_projectiles:
                projectile.draw(screen)
        
            for projectile in gksr_projectiles:
                projectile.draw(screen)
            
            time_left -= delta_time
            
            if gksr.hitpoints <= 0:
                game_end_scenario = 1
            elif player.hitpoints <= 0:
                game_end_scenario = 2
            elif time_left <= 0:
                game_end_scenario = 3
            
            if game_end_scenario != 0:
                game_phase += 1
        else:
            # display a win or lose screen depending on the value of game_end_scenario
            # prompt the user to either:
            # press space to try again
            # press escape to quit
            # ^^^ depending on which of these happen:
            # set gamephase to 2 if the user presses space
            # do nothing if the player presses escape, since that's already taken care of farther above.
            if game_end_scenario == 1:
                victory_card.draw(screen)
            elif game_end_scenario == 2 or game_end_scenario == 3:
                game_over_card.draw(screen)

            if keys[pygame.K_LSHIFT]:
                game_phase = 2

        pygame.display.flip()
        delta_time = clock.tick(FRAMES_PER_SECOND) / 1000
    pygame.quit()

if __name__ == '__main__':
    main()