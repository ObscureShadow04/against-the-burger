import pygame
import random

DISPLAY_WIDTH, DISPLAY_HEIGHT = (1280, 720)
UNIVERSAL_SPRITE_SCALE = 2.0

class Sprite():
    def __init__(self, path='', pos=(0, 0), dims=(10, 10), col=pygame.Color('White')):
        self.image = None
        self.draw_rect = pygame.Rect((0, 0), dims)

        if path != '':
            self.image = self._get_scaled_image_from_path(path)
            self.draw_rect = self.image.get_rect()        

        self.draw_rect.center = pos
        self.color = col
    
    def _get_scaled_image_from_path(self, path):
        img = pygame.image.load(path).convert_alpha()
        img_w = img.get_width()
        img_h = img.get_height()
        img = pygame.transform.scale_by(img, (UNIVERSAL_SPRITE_SCALE, UNIVERSAL_SPRITE_SCALE))
        return img

    def get_draw_rect(self):
        return self.draw_rect
    
    def set_position(self, pos=(0, 0)):
        self.draw_rect.center = pos

    def draw(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.draw_rect)
        else:
            pygame.draw.rect(screen, self.color, self.draw_rect)

class AnimatedSprite(Sprite):
    def __init__(self, path='', pos=(0, 0), fc=3, fps=12):
        super().__init__()

        self.num_images = fc
        self.images = []
        self._get_images_from_path(path)

        self.image_index = 0
        self.image = self.images[self.image_index]

        self.image_replace_time = 1.0 / fps
        self.time_since_last_replace = 0

        self.draw_rect = self.images[0].get_rect()
        self.draw_rect.center = pos

    def _get_images_from_path(self, new_path=''):
        for num in range(0, self.num_images, 1):
            self.images.append(self._get_scaled_image_from_path(f'{new_path}{num}.png'))
    
    def set_framerate(self, fps=12):
        self.image_replace_time = 1.0 / fps
    
    def update(self, dt=0, pos=(0, 0)):
        self.time_since_last_replace += dt

        if self.time_since_last_replace >= self.image_replace_time:
            self.image_index += 1
            self.time_since_last_replace = 0
        
        if self.image_index == len(self.images):
            self.image_index = 0
        
        self.image = self.images[self.image_index]

        self.draw_rect.center = pos

class Character():
    def __init__(self, sprite_details=('', 3, 12), pos=(0, 0), lim=(0, DISPLAY_HEIGHT), hb=(20, 20), hp=5, s=200, cdt=1.0):
        self.pos_x, self.pos_y = pos
        self.y_range = lim

        self.hitbox_rect = pygame.Rect((0, 0), hb)
        self.hitbox_rect.center = self.position_vector()

        self.sprite = AnimatedSprite(sprite_details[0], pos, sprite_details[1], sprite_details[2])

        self.hitpoints = hp
        self.max_hitpoints = hp

        self.speed = s

        self.time_since_last_shoot = 0
        self.shoot_cooldown_time = cdt
    
    def position_vector(self):
        return (self.pos_x, self.pos_y)

    def _update_hitbox_rect_position(self, new_rect):
        self.pos_y = new_rect.center[1]
        self.hitbox_rect.center = self.position_vector()

    def _manage_excessive_hitpoints(self):
        if self.hitpoints > self.max_hitpoints:
            self.hitpoints = self.max_hitpoints

    def _manage_shoot_cooldown(self, dt=0, cooldown_time=0):
        if self.time_since_last_shoot <= cooldown_time:
            self.time_since_last_shoot += dt
    
    def _calculate_projected_position(self, dt=0, direction=0, speed=0):
        projected_y = self.pos_y + ((speed * direction) * dt)
        projected_hitbox_rect = self.hitbox_rect.copy()
        projected_hitbox_rect.center = (self.pos_x, projected_y)
        return projected_hitbox_rect
    
    def can_shoot(self):
        if self.time_since_last_shoot >= self.shoot_cooldown_time:
            return True
        else:
            return False

    def update(self, dt=0, direction=0):
        self._manage_excessive_hitpoints
        self._manage_shoot_cooldown(dt, self.shoot_cooldown_time)
        
        projected_hitbox_rect = self._calculate_projected_position(dt, direction, self.speed)
        if not projected_hitbox_rect.top <= self.y_range[0] and not projected_hitbox_rect.bottom >= self.y_range[1]:
            self.pos_y = projected_hitbox_rect.center[1]
            self._update_hitbox_rect_position(projected_hitbox_rect)
        
        self.sprite.update(dt, self.position_vector())
    
    def draw(self, screen):
        self.sprite.draw(screen)   

class Player(Character):
    def __init__(self, sprite_details=('images\\player\\character\\', 4, 12), pos=(0, 0), lim=(0, DISPLAY_HEIGHT), hb=(20, 20), hp=5, s=200, cdt=0.5):
        super().__init__(sprite_details, pos, lim, hb, hp, s, cdt)

        self.powerup_effect_duration = 0.0
        self.active_powerup = 0

        self.powerup_active_speed = self.speed * 2
        self.powerup_active_shoot_cooldown_time = self.shoot_cooldown_time * 0.5

        self.hitpoints_bar = MeterBar(pos=(30, 50), dims=(200, 20), sm=0, col='Blue', amt=self.hitpoints)
    
    def _configure_self_from_powerups(self):
        current_speed = self.speed
        current_shoot_cooldown_time = self.shoot_cooldown_time

        if self.powerup_effect_duration > 0:
            if self.active_powerup == 1:
                self.hitpoints += 1
                self.powerup_effect_duration = 0
                self.active_powerup = 0
            elif self.active_powerup == 2:
                current_speed = self.powerup_active_speed
            elif self.active_powerup == 3:
                current_shoot_cooldown_time = self.powerup_active_shoot_cooldown_time                
        else:
            self.active_powerup = 0
        
        return (current_speed, current_shoot_cooldown_time)
    
    def can_shoot(self):
        current_speed, current_shoot_cooldown_time = self._configure_self_from_powerups()
        if self.time_since_last_shoot >= current_shoot_cooldown_time:
            return True
        else:
            return False

    def update(self, dt=0, direction=0):
        if self.active_powerup != 0:
            self.powerup_effect_duration -= dt
        
        current_speed, current_shoot_cooldown_time = self._configure_self_from_powerups()
        
        self._manage_shoot_cooldown(dt, current_shoot_cooldown_time)
        self._manage_excessive_hitpoints()
        
        projected_hitbox_rect = self._calculate_projected_position(dt, direction, current_speed)
        if not projected_hitbox_rect.top <= self.y_range[0] and not projected_hitbox_rect.bottom >= self.y_range[1]:
            self._update_hitbox_rect_position(projected_hitbox_rect)
        
        self.sprite.update(dt, self.position_vector())
        self.hitpoints_bar.update(self.hitpoints)
    
    def draw(self, screen):
        super().draw(screen)
        self.hitpoints_bar.draw(screen)

class GiantKillerSpaceRobot(Character):
    def __init__(self, sprite_details=('images\\gksr\\phase1\\character\\', 4, 12), pos=(0, 0), lim=(0, DISPLAY_HEIGHT), hb=(20, 20), hp=100, s=0, cdt=2.0, ppw=4, po=10):
        super().__init__(sprite_details, pos, lim, hb, hp, s, cdt)
        self.attack_phase = 1
        self.projectiles_per_wave = ppw

        self.projectile_origin_positions = []
        firing_range = lim
        origin_amounts = po
        for x in range(origin_amounts):
            self.projectile_origin_positions.append((900, firing_range[0] + (((firing_range[1] - firing_range[0]) / origin_amounts) * (x + 1))))
        
        self.hitpoints_bar = MeterBar(pos=(1230, 50), dims=(200, 20), sm=1, col='Red', amt=self.hitpoints)
    
    def _manage_attack_phase(self):
        health_percent = self.hitpoints / self.max_hitpoints
        phase_changed = False
        if health_percent < 0.66 and self.attack_phase == 1:
            self.attack_phase = 2
            phase_changed = True
        elif health_percent < 0.33 and self.attack_phase == 2:
            self.attack_phase = 3
            phase_changed = True
        
        if phase_changed == True:
            self.sprite = AnimatedSprite(f'images\\gksr\\phase{self.attack_phase}\\character\\', (self.pos_x, self.pos_y), 4, 12)
    
    def _manage_self_from_attack_phase(self):
        if self.attack_phase == 1:
            self.projectiles_per_wave = 4
            self.cooldown_time = 2.0
        elif self.attack_phase == 2:
            self.projectiles_per_wave = 5
            self.cooldown_time = 1.5
        if self.attack_phase == 3:
            self.projectiles_per_wave = 6
            self.cooldown_time = 1.0

    def update(self, dt=0):
        super().update(dt, 0)

        self._manage_attack_phase()
        self._manage_self_from_attack_phase()

        self.sprite.update(dt, self.position_vector())
        self.hitpoints_bar.update(self.hitpoints)
        return
    
    def draw(self, screen):
        super().draw(screen)
        self.hitpoints_bar.draw(screen)

class MovingObject():
    def __init__(self, sprite_details=('', 3, 12), pos=(0, 0), hb=(20, 20), s=200, dir=0):
        self.pos_x, self.pos_y = pos

        self.hitbox_rect = pygame.Rect((0, 0), hb)
        self.hitbox_rect.center = self.position_vector()

        self.sprite = AnimatedSprite(sprite_details[0], pos, sprite_details[1], sprite_details[2])

        self.speed = s
        self.direction = dir
        self.onscreen = True
    
    def position_vector(self):
        return (self.pos_x, self.pos_y)
    
    def _is_onscreen(self):
        game_window_rect = pygame.Rect((0,0), (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        return game_window_rect.colliderect(self.sprite.draw_rect)
    
    def _adjust_position(self, dt=0):
        self.pos_x += (self.speed * self.direction) * dt
        self.hitbox_rect.center = self.position_vector()

    def update(self, dt=0):        
        self.onscreen = self._is_onscreen()
        if self.onscreen:
            self._adjust_position
        self.sprite.update(dt, self.position_vector())
    
    def check_hit(self, rect):
        return self.hitbox_rect.colliderect(rect)



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
    def __init__(self, path='test_images\\test_UI_bar.png', pos=(0, 0)):
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

        self.shrink_mode = sm
        self.color = col

        self.max_amount = amt
        self.amount = self.max_amount

        self.draw_rect = pygame.Rect(pos, dims)
        if self.shrink_mode == 0:
            self.draw_rect.topleft = self.position
        elif self.shrink_mode == 1:
            self.draw_rect.topright = self.position
        else:
            self.draw_rect.midtop = self.position
        
        self.outline_rect = pygame.Rect(pos, (dims[0] + 10, dims[1] + 10))
        self.outline_rect.center = self.draw_rect.center

        self.background_rect = pygame.Rect(pos, dims)
        self.background_rect.center = self.draw_rect.center

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
        pygame.draw.rect(screen, 'Black', self.outline_rect)
        pygame.draw.rect(screen, pygame.Color(self.color).lerp('Black', 0.5), self.background_rect)
        pygame.draw.rect(screen, self.color, self.draw_rect)

class OldProjectile(GameObject):
    def __init__(self, path='test_images\\test_projectile.png', pos=(0, 0), hb=(8, 8), s=750, dir=0, dmg=1):
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

class OldPowerUp(GameObject):
    def __init__(self, path='test_images\\test_powerup.png', pos=(900, 360), hb=(20, 20), code=1):
        super().__init__()
        self.pos_x, self.pos_y = pos
        
        self.image = pygame.image.load(path).convert_alpha()
        self.draw_rect = self.image.get_rect()
        self.draw_rect.center = (self.pos_x, self.pos_y)

        self.hitbox_rect = pygame.Rect((0, 0), hb)
        self.hitbox_rect.center = (self.pos_x, self.pos_y)

        self.powerup_code = code
        self.powerup_duration = 5.0
        self.direction = -1
        self.speed = 350
        self.onscreen = True
    
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

class OldPlayer(GameObject):
    def __init__(self, path='test_images\\test_player.png', pos=(100, 360), lim=(0, DISPLAY_HEIGHT), hb=(20, 20), hp=5, s=200, cdt=0.5):
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
        self.max_hitpoints = hp

        self.speed = s

        self.shoot_cooldown = 0
        self.cooldown_time = cdt
        self.current_cooldown_time = cdt

        self.powerup_effect_duration = 0.0
        self.active_powerup = 0

        self.speed_when_powerup = self.speed * 2
        self.cooldown_time_when_powerup = self.cooldown_time * 0.5

        self.hitpoints_bar = MeterBar(pos=(30, 50), dims=(200, 20), sm=0, col='Blue', amt=self.hitpoints)

    def update(self, dt=0, direction=0):
        super().update()

        if self.active_powerup != 0:
            self.powerup_effect_duration -= dt
        
        current_speed = self.speed
        self.current_cooldown_time = self.cooldown_time

        if self.powerup_effect_duration > 0:
            if self.active_powerup == 1:
                self.hitpoints += 1
                self.powerup_effect_duration = 0
                self.active_powerup = 0
            elif self.active_powerup == 2:
                current_speed = self.speed_when_powerup
            elif self.active_powerup == 3:
                self.current_cooldown_time = self.cooldown_time_when_powerup                
        else:
            self.active_powerup = 0

        if self.hitpoints > self.max_hitpoints:
            self.hitpoints = self.max_hitpoints
        
        projected_y = self.pos_y + ((current_speed * direction) * dt)
        projected_draw_rect = self.draw_rect.copy()
        projected_draw_rect.center = (self.pos_x, projected_y)

        if not projected_draw_rect.top <= self.min_y and not projected_draw_rect.bottom >= self.max_y:
            self.pos_y = projected_y
            self.draw_rect.center = (self.pos_x, self.pos_y)
            self.hitbox_rect.center = (self.pos_x, self.pos_y)

        if self.shoot_cooldown <= self.current_cooldown_time:
            self.shoot_cooldown += dt
        
        self.hitpoints_bar.update(self.hitpoints)

    def draw(self, screen):
        super().draw(screen)
        self.hitpoints_bar.draw(screen)

class OldGiantKillerSpaceRobot(GameObject):
    def __init__(self, path='test_images\\test_gksr_phase1.png', pos=(880, 170), hb=(300, 600), hp=100, s=200, cdt=2, init_ppw=6, mp=10, y_range=(0, DISPLAY_HEIGHT)):
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
            self.image = pygame.image.load('test_images\\test_gksr_phase1.png').convert_alpha()
            self.projectiles_per_wave = 4
            self.cooldown_time = 2.0
        elif self.attack_phase == 2:
            self.image = pygame.image.load('test_images\\test_gksr_phase2.png').convert_alpha()
            self.projectiles_per_wave = 5
            self.cooldown_time = 1.5
        if self.attack_phase == 3:
            self.image = pygame.image.load('test_images\\test_gksr_phase3.png').convert_alpha()
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

def spawn_powerup():
    powerup_sprites = ['test_images\\powerup_healthpack.png', 'test_images\\powerup_speed.png', 'test_images\\powerup_firerate.png']
    random_num = random.randint(1,3)
    return OldPowerUp(path=powerup_sprites[random_num - 1],code=random_num)

def main():
    FRAMES_PER_SECOND = 60
    
    pygame.init()
    pygame.display.set_caption('Impending Doom')

    screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))

    clock = pygame.time.Clock()
    delta_time = 0

    player = OldPlayer(lim=(280, 580))
    player_projectiles = []

    gksr = OldGiantKillerSpaceRobot(y_range=(280, 550))
    gksr_projectiles = []

    time_left = 60.0
    time_bar = MeterBar(pos=(640, 20), dims=(500, 20), sm=2, col='Purple', amt=time_left)

    powerup_pickups = []

    game_phase = 1
    game_end_scenario = 0

    title_card = StaticImage(path='test_images\\title_card.png')
    game_over_card = StaticImage(path='test_images\\game_over_card.png')
    victory_card = StaticImage(path='test_images\\victory_card.png')
    ui_background_bar = StaticImage()

    #test_player = GiantKillerSpaceRobot(pos=(300, 400))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_BACKSPACE] or keys[pygame.K_ESCAPE]:
            running = False
        
        if game_phase == 1:
            #test_player.update(delta_time)

            title_card.draw(screen)
            #test_player.draw(screen)

            if keys[pygame.K_SPACE]:
                game_phase += 1
        elif game_phase == 2:
            player = Player(pos=(100, 420), lim=(230, 640), hp=5)
            player_projectiles = []

            gksr = GiantKillerSpaceRobot(pos=(1050, 420), lim=(180, 680), hb=(200, 500))
            gksr_projectiles = []

            powerup_pickups = []

            game_end_scenario = 0
            
            time_left = 60.0
            time_bar = MeterBar(pos=(640, 20), dims=(500, 20), sm=2, col='Purple', amt=time_left)

            game_phase +=1
        elif game_phase == 3:
            time_bar.update(time_left)

            if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
                player.update(delta_time, -1)
            elif keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
                player.update(delta_time, 1)
            else:
                player.update(delta_time, 0)
            
            if keys[pygame.K_SPACE] and player.can_shoot():
                player_projectiles.append(OldProjectile(pos=player.hitbox_rect.center, dir=1))
                player.time_since_last_shoot = 0
        
            gksr.update(delta_time)
            if gksr.can_shoot():
                positions = choose_gksr_projectiles_origins(gksr)
                for position in positions:
                    gksr_projectiles.append(OldProjectile(path='test_images\\test_gskr_projectile.png', pos=position, hb=(20,32), s=500, dir=-1))
                
                chance = 20
                random_num = random.randint(1, 100)
                if random_num < chance:
                    powerup_pickups.append(spawn_powerup())

                gksr.time_since_last_shoot = 0

            player_projectiles = update_projectile_group(player_projectiles, delta_time, gksr)
            gksr_projectiles = update_projectile_group(gksr_projectiles, delta_time, player)

            new_powerup_pickups = []
            for powerup in powerup_pickups:
                if powerup.onscreen:
                    powerup.update(delta_time)                    
                    if powerup.check_hit(player.hitbox_rect) and player.active_powerup == 0:
                        player.active_powerup = powerup.powerup_code
                        player.powerup_effect_duration = powerup.powerup_duration
                    else:
                        new_powerup_pickups.append(powerup)
            powerup_pickups = new_powerup_pickups
    
            screen.fill(pygame.Color(16, 0, 26))
            ui_background_bar.draw(screen)

            time_bar.draw(screen)
            
            gksr.draw(screen)
            player.draw(screen)

            for projectile in player_projectiles:
                projectile.draw(screen)
        
            for projectile in gksr_projectiles:
                projectile.draw(screen)
            
            for powerup in powerup_pickups:
                powerup.draw(screen)

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