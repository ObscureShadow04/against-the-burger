import pygame
import random

DISPLAY_WIDTH, DISPLAY_HEIGHT = (1920, 1080)
UNIVERSAL_SPRITE_SCALE = 3.0

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
    def __init__(self, sprite_details=('images\\player\\character\\', 4, 12), pos=(0, 0), lim=(0, DISPLAY_HEIGHT), hb=(20, 20), hp=5, s=300, cdt=0.5):
        super().__init__(sprite_details, pos, lim, hb, hp, s, cdt)

        self.powerup_effect_duration = 0.0
        self.active_powerup = 0

        self.powerup_active_speed = self.speed * 2
        self.powerup_active_shoot_cooldown_time = self.shoot_cooldown_time * 0.5

        self.hitpoints_bar = MeterBar(pos=(45, 75), dims=(300, 30), sm=0, col='Blue', amt=self.hitpoints)
    
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
    def __init__(self, sprite_details=('images\\gksr\\phase1\\character\\', 4, 12), pos=(0, 0), lim=(0, DISPLAY_HEIGHT), hb=(20, 20), hp=100, s=0, cdt=2.0, ppw=5, po=10):
        super().__init__(sprite_details, pos, lim, hb, hp, s, cdt)
        self.attack_phase = 1
        self.projectiles_per_wave = ppw
        self.powerup_drop_chance = 10

        self.projectile_origin_positions = []
        firing_range = lim
        origin_amounts = po
        for x in range(origin_amounts):
            self.projectile_origin_positions.append((1350, firing_range[0] + (((firing_range[1] - firing_range[0]) / origin_amounts) * (x + 1))))
        
        self.hitpoints_bar = MeterBar(pos=(1845, 75), dims=(300, 30), sm=1, col='Red', amt=self.hitpoints)
    
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
            self.projectiles_per_wave = 5
            self.cooldown_time = 2.0
            self.powerup_drop_chance = 10
        elif self.attack_phase == 2:
            self.projectiles_per_wave = 6
            self.cooldown_time = 1.5
            self.powerup_drop_chance = 30
        if self.attack_phase == 3:
            self.projectiles_per_wave = 7
            self.cooldown_time = 1.0
            self.powerup_drop_chance = 50

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

class Blast():
    def __init__(self, sprite_details=('', 3, 12), pos=(0, 0), hb=(20, 20)):
        self.pos_x, self.pos_y = pos
        
        self.hitbox_rect = pygame.Rect((0, 0), hb)
        self.hitbox_rect.center = self.position_vector()
        
        self.sprite = AnimatedSprite(sprite_details[0], pos, sprite_details[1], sprite_details[2])

        self.lifetime = 0
        self.lifespan = self.sprite.image_replace_time * self.sprite.num_images

    def position_vector(self):
        return (self.pos_x, self.pos_y)
    
    def should_die(self):
        return self.lifetime >= self.lifespan
    
    def update(self, dt=0):
        self.lifetime += dt
        self.sprite.update(dt, self.position_vector())
    
    def draw(self, screen):
        self.sprite.draw(screen)

class MovingObject():
    def __init__(self, sprite_details=('', 3, 12), pos=(0, 0), hb=(20, 20), s=200, dir=0):
        self.pos_x, self.pos_y = pos

        self.hitbox_rect = pygame.Rect((0, 0), hb)
        self.hitbox_rect.center = self.position_vector()

        self.sprite = None
        if sprite_details[0] != '':
            self.sprite = AnimatedSprite(sprite_details[0], pos, sprite_details[1], sprite_details[2])
        else:
            self.sprite = Sprite(sprite_details[0], pos, sprite_details[1], sprite_details[2])

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
            self._adjust_position(dt)
            self.sprite.update(dt, self.position_vector())
    
    def check_hit(self, rect):
        return self.hitbox_rect.colliderect(rect)
    
    def draw(self, screen):
        self.sprite.draw(screen)

class Projectile(MovingObject):
    def __init__(self, sprite_details=('', 3, 12), pos=(0, 0), hb=(20, 20), s=200, dir=0, dmg=0, bd=(('', 3, 12), (0, 0), (20, 20))):
        super().__init__(sprite_details, pos, hb, s, dir)

        self.damage = dmg
        self.blast_details = bd

class Star(MovingObject):
    def __init__(self, sprite_details=('', (4, 4), pygame.Color('White')), pos=(0, 0), hb=(20, 20), s=200, dir=0, x_lim=DISPLAY_WIDTH+50):
        super().__init__(sprite_details, pos, hb, s, dir)

        self.x_limit = x_lim
    
    def _is_onscreen(self):
        return self.pos_x < self.x_limit

    def update(self, dt=0):
        self.onscreen = self._is_onscreen()
        if self.onscreen:
            self._adjust_position(dt)
            self.sprite.set_position(self.position_vector())

class PowerUp(MovingObject):
    def __init__(self, sprite_details=('', 3, 12), pos=(0, 0), hb=(20, 20), s=200, dir=-1, c=1, dur=5):
        super().__init__(sprite_details, pos, hb, s, dir)

        self.code = c
        self.duration = dur

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

def update_player_from_keys(player, keys, dt=0):
    direction = None
    if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
        direction = -1
    elif keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
        direction = 1
    else:
        direction = 0
    
    player.update(dt, direction)
    return direction

def player_shoot(player, player_projectiles):
    blast_details = ((f'images\\player\\blast\\', 6, 12), (0, 0), (1, 1))
    player_projectiles.append(Projectile(('images\\player\\projectile\\', 3, 12), player.position_vector(), s=900, dir=1, dmg=1, bd=blast_details))
    player.time_since_last_shoot = 0

def choose_random_gksr_projectiles_origins(gksr):
    positions = []
    while len(positions) < gksr.projectiles_per_wave:
        pos = random.choice(gksr.projectile_origin_positions)
        if not pos in positions:
            positions.append(pos)
    return positions

def gksr_fire_projectile_wave(gksr, powerups_group, gksr_projectile_group):
    positions = choose_random_gksr_projectiles_origins(gksr)

    chance = gksr.powerup_drop_chance
    random_num = random.randint(1, 100)
    powerup_will_spawn = False
    if random_num < chance:
        powerup_will_spawn = True
                
    random_position_index = random.randint(0, len(positions)-1)

    for index, position in enumerate(positions):
        if index == random_position_index and powerup_will_spawn:
            powerups_group.append(spawn_powerup(position))
        else:
            blast_details = ((f'images\\gksr\\phase{gksr.attack_phase}\\blast\\', 8, 12), (0, 0), (1, 1))
            gksr_projectile_group.append(Projectile((f'images\\gksr\\phase{gksr.attack_phase}\\projectile\\', 3, 12), position, hb=(48, 48), s=750, dir=-1, dmg=1, bd=blast_details))
    gksr.time_since_last_shoot = 0
    return (powerups_group, gksr_projectile_group)

def update_projectiles(projectiles, target, blasts, dt=0):
    new_projectiles = []
    for projectile in projectiles:
        if projectile.onscreen:
            projectile.update(dt)                    
            if projectile.check_hit(target.hitbox_rect):
                target.hitpoints -= projectile.damage
                blast_details = projectile.blast_details
                blasts.append(Blast(blast_details[0], projectile.position_vector(), blast_details[2]))
            else:
                new_projectiles.append(projectile)
    return (new_projectiles, blasts)

def update_powerups(powerups, target, dt=0):
    new_powerups = []
    for powerup in powerups:
        if powerup.onscreen:
            powerup.update(dt)                    
            if powerup.check_hit(target.hitbox_rect) and target.active_powerup == 0:
                target.active_powerup = powerup.code
                target.powerup_effect_duration = powerup.duration
            else:
                new_powerups.append(powerup)
    return new_powerups

def spawn_powerup(position):
    base_path = 'images\\powerups\\'
    random_num = random.randint(1,3)
    return PowerUp((f'{base_path}{random_num}\\', 3, 12), position, s=300, c=random_num)

def update_blasts(blasts, dt=0):
    new_blasts = []
    for blast in blasts:
        blast.update(dt)
        if not blast.should_die():
            new_blasts.append(blast)
    return new_blasts

def generate_star(x_range=(0, DISPLAY_WIDTH), y_range=(0, DISPLAY_HEIGHT), x_limit=DISPLAY_WIDTH+50):
    position = (random.randint(x_range[0], x_range[1]), random.randint(y_range[0], y_range[1]))
    color = pygame.Color('White') #pygame.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    random_num = random.randint(1, 3)

    STAR_SIZE_CONSTANT = 3
    size = STAR_SIZE_CONSTANT #* random_num

    STAR_SPEED_CONSTANT = 100
    speed = STAR_SPEED_CONSTANT * random_num

    sprite_details = ('', (size, size), color)

    return Star(sprite_details, position, s=speed, dir=1, x_lim=x_limit)

def update_stars(stars, dt=0):
    stars_removed = 0

    new_stars = []
    for star in stars:
        if star.onscreen:
            star.update(dt)                    
            new_stars.append(star)
        else:
            stars_removed += 1
    
    for number in range(0, stars_removed, 1):
        new_stars.append(generate_star(x_range=(-64, -16)))

    return new_stars

def main():
    FRAMES_PER_SECOND = 60
    
    pygame.init()
    pygame.display.set_caption('Impending Doom')

    screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))

    clock = pygame.time.Clock()
    delta_time = 0

    player = Player(pos=(150, 630), lim=(345, 960), hp=5)
    player_projectiles = []

    gksr = GiantKillerSpaceRobot(pos=(1575, 630), lim=(270, 1020), hb=(300, 750))
    gksr_projectiles = []

    powerup_pickups = []
    blasts = []

    star_count = 300
    stars = []

    time_left = 60.0
    time_bar = MeterBar(pos=(960, 30), dims=(750, 30), sm=2, col='Purple', amt=time_left)

    powerup_pickups = []

    game_phase = 1
    game_end_scenario = 0

    center_vector = (DISPLAY_WIDTH/2, DISPLAY_HEIGHT/2)

    title_screen = Sprite(path='images\\title.png', pos=center_vector)
    end_screen = Sprite(path='')    

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_BACKSPACE] or keys[pygame.K_ESCAPE]:
            running = False
        
        if game_phase == 1:
            title_screen.draw(screen)

            if keys[pygame.K_SPACE]:
                game_phase += 1
        elif game_phase == 2:
            player = Player(pos=(150, 630), lim=(345, 960), hb=(60, 60), hp=5)
            player_projectiles = []

            gksr = GiantKillerSpaceRobot(pos=(1575, 630), lim=(270, 910), hb=(300, 750), po=8)
            gksr_projectiles = []

            powerups = []
            blasts = []

            stars = []
            for num in range(0, star_count, 1):
                stars.append(generate_star())

            game_end_scenario = 0
            
            time_left = 60.0
            time_bar = MeterBar(pos=(960, 30), dims=(750, 30), sm=2, col='Purple', amt=time_left)

            end_screen = Sprite(path='') 
            game_phase +=1
        elif game_phase == 3:
            time_bar.update(time_left)

            direction = update_player_from_keys(player, keys, delta_time)
            if keys[pygame.K_SPACE] and player.can_shoot() and direction == 0:
                player_shoot(player, player_projectiles)
        
            gksr.update(delta_time)
            if gksr.can_shoot():
                powerups, gksr_projectiles = gksr_fire_projectile_wave(gksr, powerups, gksr_projectiles)

            player_projectiles, blasts = update_projectiles(player_projectiles, gksr, blasts, delta_time)
            gksr_projectiles, blasts = update_projectiles(gksr_projectiles, player, blasts, delta_time)

            powerups = update_powerups(powerups, player, delta_time)
            blasts = update_blasts(blasts, delta_time)

            stars = update_stars(stars, delta_time)

            screen.fill(pygame.Color(32, 0, 54))

            for star in stars:
                star.draw(screen)
            
            pygame.draw.rect(screen, "Grey", pygame.Rect((0, 0), (DISPLAY_WIDTH, 180)))

            time_bar.draw(screen)
            
            gksr.draw(screen)
            player.draw(screen)

            for projectile in player_projectiles:
                projectile.draw(screen)
        
            for projectile in gksr_projectiles:
                projectile.draw(screen)
            
            for powerup in powerups:
                powerup.draw(screen)

            for blast in blasts:
                blast.draw(screen)

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
            end_screen = Sprite(path=f'images\\endings\\game_end_{game_end_scenario}.png', pos=center_vector)
            end_screen.draw(screen)

            if keys[pygame.K_RSHIFT]:
                game_phase = 2

        pygame.display.flip()
        delta_time = clock.tick(FRAMES_PER_SECOND) / 1000
    pygame.quit()

if __name__ == '__main__':
    main()