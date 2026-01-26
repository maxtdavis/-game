# Added comments throughout explaining purpose and logic of each part.

import pygame
from levels import LEVELS
pygame.init()

WIDTH, HEIGHT = 768, 576

class Player:
    def __init__(self, x, y, color=(0,128,255), filename=None):
        # Player position
        self.x = x
        self.y = y
        self.direction = 'right'
        # Player size
        self.width = 32
        self.height = 48
        self.color = color
        self.filename = filename
        # Velocity components
        self.vel_x = 0
        self.vel_y = 0
        # Movement parameters
        self.speed = 5
        self.jump_strength = -20
        self.gravity = 1
        # State: 1 = platformer, 2 = top‑down
        self.state = 1
        self.grounded = False
        # Idle animation
        self.idle_right_frames = ["images/character/idle_right/1.png", "images/character/idle_right/2.png", "images/character/idle_right/3.png"]
        self.idle_left_frames = ["images/character/idle_left/1.png", "images/character/idle_left/2.png", "images/character/idle_left/3.png"]
        self.run_right_frames = ["images/character/run_right/1.png", "images/character/run_right/2.png", "images/character/run_right/3.png", "images/character/run_right/4.png"]
        self.run_left_frames = ["images/character/run_left/1.png", "images/character/run_left/2.png", "images/character/run_left/3.png", "images/character/run_left/4.png"]
        self.animation_frame = 0
        self.animation_counter = 0
        self.animation_speed = 5  # frames per sprite

    @property
    def rect(self):
        # Collision rectangle
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surf):
        # Check if player is idle (not moving)
        is_idle = self.vel_x == 0 and self.vel_y == 0
        
        # Draw idle animation if idle
        if is_idle and self.direction == 'right':
            self.animation_counter += 1
            if self.animation_counter >= self.animation_speed * 2:
                self.animation_counter = 0
                self.animation_frame = (self.animation_frame + 1) % len(self.idle_right_frames)
            
            try:
                image = pygame.image.load(self.idle_right_frames[self.animation_frame])
                surf.blit(image, (self.x, self.y))
                return
            except:
                pass
        elif is_idle and self.direction == 'left':
            self.animation_counter += 1
            if self.animation_counter >= self.animation_speed * 2:
                self.animation_counter = 0
                self.animation_frame = (self.animation_frame + 1) % len(self.idle_left_frames)
            
            try:
                image = pygame.image.load(self.idle_left_frames[self.animation_frame])
                surf.blit(image, (self.x, self.y))
                return
            except:
                pass
        elif not is_idle and self.grounded and self.direction == 'right':
            self.animation_counter += 1
            if self.animation_counter >= self.animation_speed:
                self.animation_counter = 0
                self.animation_frame = (self.animation_frame + 1) % len(self.run_right_frames)
            
            try:
                image = pygame.image.load(self.run_right_frames[self.animation_frame])
                surf.blit(image, (self.x, self.y))
                return
            except:
                pass
        elif not is_idle and self.grounded and self.direction == 'left':
            self.animation_counter += 1
            if self.animation_counter >= self.animation_speed:
                self.animation_counter = 0
                self.animation_frame = (self.animation_frame + 1) % len(self.run_left_frames)

            try:
                image = pygame.image.load(self.run_left_frames[self.animation_frame])
                surf.blit(image, (self.x, self.y))
                return
            except:
                pass
        else:
            # Reset animation when moving
            self.animation_counter = 0
            self.animation_frame = 0
        
        # Draw player with default sprite or color
        if self.filename:
            try:
                image = pygame.image.load(self.filename)
                surf.blit(image, (self.x, self.y))
                return
            except:
                pass
        pygame.draw.rect(surf, self.color, self.rect)

class GameObject:
    def __init__(self, x, y, filename=None, color=(0,0,0)):
        # Base class for background, terrain, props
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.color = color
        self.image = None
        
        # Load sprite image if given
        if filename:
            try:
                self.image = pygame.image.load(filename)
                self.width = self.image.get_width()
                self.height = self.image.get_height()
            except:
                print("Failed to load image:", filename)

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surf):
        if self.image:
            surf.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(surf, self.color, self.rect)

class Background(GameObject):
    def __init__(self, x, y, filename=None, color=(200,200,200)):
        super().__init__(x, y, filename, color)
        self.is_solid = False
    def draw(self, surf):
        pass

class Terrain(GameObject):
    def __init__(self, x, y, row=None, col=None, color=(139,69,19)):
        super().__init__(x, y, None, color)
        # Solid tiles collide with the player
        self.is_solid = True
        self.row = row
        self.col = col
        self.placement = "0000"
    
    def calculate_placement(self, grid):
        """Calculate placement based on neighboring terrain blocks.
        Placement is a 4-digit binary string: above, right, below, left
        """
        if self.row is None or self.col is None:
            self.placement = "0000"
            return
        
        # Get grid dimensions for bounds checking
        grid_height = len(grid)
        grid_width = len(grid[0]) if grid_height > 0 else 0
        
        # Check each direction with bounds checking
        # Check above (row - 1)
        above = "1" if (self.row > 0 and isinstance(grid[self.row-1][self.col], Terrain)) else "0"
        # Check right (col + 1)
        right = "1" if (self.col < grid_width - 1 and isinstance(grid[self.row][self.col+1], Terrain)) else "0"
        # Check below (row + 1)
        below = "1" if (self.row < grid_height - 1 and isinstance(grid[self.row+1][self.col], Terrain)) else "0"
        # Check left (col - 1)
        left = "1" if (self.col > 0 and isinstance(grid[self.row][self.col-1], Terrain)) else "0"
        
        self.placement = above + right + below + left
    
    def load_image(self):
        """Load image based on placement, fallback to brown square if not found"""
        filename = f"images/themes/standard/{self.placement}.png"
        try:
            self.image = pygame.image.load(filename)
            self.width = self.image.get_width()
            self.height = self.image.get_height()
        except:
            # Fallback: will draw brown square in draw method
            self.image = None
    
    def draw(self, surf):
        if self.image:
            surf.blit(self.image, (self.x, self.y))
        else:
            # Draw brown fallback square
            pygame.draw.rect(surf, (139, 69, 19), self.rect)

class ImmovableProp(GameObject):
    def __init__(self, x, y, filenames=(None, None), color=(200,200,100), is_alive=False):
        super().__init__(x, y, filenames[0] if is_alive==False else filenames[1], color)
        self.is_alive = is_alive
        self.filenames = filenames
        self.is_solid = False
        # Solid tiles collide with the player
        if self.is_alive:
            self.is_solid = True
    
    def paint(self):
        self.is_alive = True
        self.is_solid = True
        try:
            self.image = pygame.image.load(self.filenames[1])
            self.width = self.image.get_width()
            self.height = self.image.get_height()
        except:
            print("Failed to load image:", self.filenames[1])

    def draw(self, surf):
        if self.image:
            surf.blit(self.image, (self.x, self.y))

class Paint(GameObject):
    def __init__(self, x, y, direction, filename=None):
        super().__init__(x, y, filename, color=(0, 0, 255))
        self.width = 8
        self.height = 8
        self.direction = direction
        self.vel_x = 10 if direction == 'right' else -10
        self.speed = 10
        self.distance_traveled = 0
        self.max_distance = 160  # 5 blocks
        # Animation properties
        self.current_frame = 1
        self.frame_counter = 0
        self.frames_per_image = 1  # Change image every frame
    
    def update(self):
        # Move projectile (no friction)
        self.x += self.vel_x
        self.distance_traveled += abs(self.vel_x)
        # Update animation frame
        self.frame_counter += 1
        if self.frame_counter >= self.frames_per_image:
            self.frame_counter = 0
            self.current_frame += 1
            if self.current_frame > 18:
                self.current_frame = 1
    
    def draw(self, surf):
        filename = f"images/paintball/{self.current_frame}.png"
        try:
            surf.blit(pygame.image.load(filename), (self.x, self.y))
        except FileNotFoundError:
            # Fallback to drawing a circle if image not found
            pygame.draw.rect(surf, self.color, self.rect)

class MovableObject(GameObject):
    def __init__(self, x, y, filename=None, color=(160,82,45)):
        super().__init__(x, y, filename, color)
        # Movable objects are solid and can be pushed
        self.is_solid = True
        self.is_movable = True
        # Physics
        self.vel_x = 0
        self.vel_y = 0
        self.gravity = 1
        self.grounded = False
        self.speed = 5
    
    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surf):
        if self.image:
            surf.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(surf, self.color, self.rect)

class PaintBar(GameObject):
    def __init__(self, x, y, state=10):
        self.x = x
        self.y = y
        self.state = state  # Amount of paint available
        self.width = 48
        self.height = 16
    def draw(self, surf):
        filename = "images/paintbar/" + str(self.state) + ".png"
        surf.blit(pygame.image.load(filename), (self.x, self.y))

class Goal(GameObject):
    def __init__(self, x, y, filename=None, color=(0,255,0)):
        super().__init__(x, y, filename, color)
        self.is_solid = False
        self.height = 64  # Two blocks tall

class Barrier(GameObject):
    def __init__(self, x, y, filenames=(None, None), state1_color=(255,200,200), state2_color=(255,0,0)):
        # filenames[0]: off animation (passable in platformer mode)
        # filenames[1]: on animation (solid in top-down mode)
        # state1_color: light red (passable in platformer mode)
        # state2_color: solid red (solid in top-down mode)
        super().__init__(x, y, filenames[0], state2_color)
        self.filenames = filenames
        self.state1_color = state1_color
        self.state2_color = state2_color
        self.is_solid = True
        self.player = None  # Will be set by Game after creation
    
    def set_player(self, player):
        self.player = player
    
    def draw(self, surf):
        # Update image and color based on current player state
        if self.player:
            if self.player.state == 1:
                # Platformer mode: off animation (passable)
                self.color = self.state1_color
                if self.filenames[0]:
                    try:
                        self.image = pygame.image.load(self.filenames[0])
                    except:
                        self.image = None
            else:
                # Top-down mode: on animation (solid)
                self.color = self.state2_color
                if self.filenames[1]:
                    try:
                        self.image = pygame.image.load(self.filenames[1])
                    except:
                        self.image = None
        
        # Draw background color first, then image on top
        if self.image:
            surf.blit(self.image, (self.x, self.y))

class Level:
    def __init__(self, index, map_string, theme="basic"):
        self.index = index
        self.map = map_string
        self.theme = theme

class Game:
    def __init__(self, width, height, player, level, FPS=60, tile_size=32):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.FPS = FPS
        self.p = player
        self.level = level
        self.tile_size = tile_size
        self.UI_HEIGHT = 64  # Reserved space at top for UI
        self.paintbar = PaintBar(0,0)
        self.font_large = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
        self.background = "images/background.jpg"

        # Grid of tiles (background by default)
        self.grid = self.create_grid()
        # List to store movable objects
        self.movable_objects = []
        # List to store paint projectiles
        self.paint_projectiles = []
        # Goal object
        self.goal = None
        # Replace tiles based on level map
        self.load_level()

    def create_grid(self):
        # Basic grid - will be sized based on level map
        return []

    def load_level(self):
        # Parse level map string and place tiles accordingly
        lines = self.level.map.strip().split("\n")
        # Create grid based on actual level dimensions, offset by UI_HEIGHT
        self.grid = [[Background(c*self.tile_size, r*self.tile_size + self.UI_HEIGHT) for c in range(len(line))] for r, line in enumerate(lines)]
        for r, line in enumerate(lines):
            for c, ch in enumerate(line):
                x = c * self.tile_size
                y = r * self.tile_size + self.UI_HEIGHT

                if ch == '.':   # Air / sky
                    self.grid[r][c] = Background(x, y, color=(135,206,235))
                elif ch == '#': # Solid terrain
                    self.grid[r][c] = Terrain(x, y, row=r, col=c)
                elif ch == 'P': # Player spawn
                    self.p.x = x
                    self.p.y = y
                    self.grid[r][c] = Background(x, y, color=(135,206,235))
                elif ch == 'i': # Interactive prop
                    self.grid[r][c] = ImmovableProp(x, y, color=(135,206,235), filenames=("images/flower_dead.png", "images/flower_alive.png"), is_alive=False)
                elif ch == 'M': # Movable object
                    self.grid[r][c] = Background(x, y, color=(135,206,235))
                    self.movable_objects.append(MovableObject(x, y, filename="images/barrel.png"))
                elif ch == 'g': # Goal
                    self.goal = Goal(x, y, color=(0,255,0))
                    self.grid[r][c] = Background(x, y, color=(135,206,235))
                elif ch == '^': # Barrier (solid in top-down, passable in platformer)
                    barrier = Barrier(x, y, filenames=('images/barrier_off.png', 'images/barrier_on.png'), state1_color=(135,206,235), state2_color=(255,0,0))
                    barrier.set_player(self.p)
                    self.grid[r][c] = barrier
        
        # After grid is fully built, calculate placement and load images for all terrain blocks
        for row in self.grid:
            for tile in row:
                if isinstance(tile, Terrain):
                    tile.calculate_placement(self.grid)
                    tile.load_image()

    def solid_tiles(self):
        # Generator for tiles that block movement
        for row in self.grid:
            for t in row:
                if hasattr(t, 'is_solid') and t.is_solid:
                    yield t
    
    def all_solid_objects(self):
        # Generator for all solid objects (tiles + movable objects)
        for obj in self.solid_tiles():
            # Skip Barriers in platformer mode (state 1)
            if isinstance(obj, Barrier) and self.p.state == 1:
                continue
            yield obj
        for obj in self.movable_objects:
            yield obj
        # Include goal when in top-down mode (state 2)
        if self.goal and self.p.state == 2:
            yield self.goal


    def move_axis(self, dx, dy):
        # Horizontal movement and collision resolution
        if dx != 0:
            self.p.x += dx
            pr = self.p.rect
            for obj in self.all_solid_objects():
                if pr.colliderect(obj.rect):
                    # Check if it's a movable object
                    if hasattr(obj, 'is_movable') and obj.is_movable:
                        # Try to push the object horizontally in both modes
                        push_dx = self.p.speed if dx > 0 else -self.p.speed
                        # Check if the push destination is valid (no collision)
                        test_rect = pygame.Rect(obj.x + push_dx, obj.y, obj.width, obj.height)
                        can_push = True
                        for other_obj in self.all_solid_objects():
                            if other_obj is not obj and test_rect.colliderect(other_obj.rect):
                                can_push = False
                                break
                        
                        if can_push:
                            # Move the object only the amount pushed, no velocity
                            obj.x += push_dx
                            obj.vel_x = 0
                        else:
                            # Can't push, stop player movement
                            if dx > 0:
                                self.p.x = obj.x - self.p.width
                            else:
                                self.p.x = obj.x + obj.width
                    else:
                        # Normal collision
                        if dx > 0:  # moving right
                            self.p.x = obj.x - self.p.width
                        else:       # moving left
                            self.p.x = obj.x + obj.width
                    pr = self.p.rect

        # Vertical movement and collision resolution
        self.p.grounded = False
        if dy != 0:
            self.p.y += dy
            pr = self.p.rect
            for obj in self.all_solid_objects():
                if pr.colliderect(obj.rect):
                    # Check if it's a movable object
                    if hasattr(obj, 'is_movable') and obj.is_movable:
                        if self.p.state == 2:
                            # Try to push the object vertically in top-down mode
                            push_dy = self.p.speed if dy > 0 else -self.p.speed
                            # Check if the push destination is valid (no collision)
                            test_rect = pygame.Rect(obj.x, obj.y + push_dy, obj.width, obj.height)
                            can_push = True
                            for other_obj in self.all_solid_objects():
                                if other_obj is not obj and test_rect.colliderect(other_obj.rect):
                                    can_push = False
                                    break
                            
                            if can_push:
                                # Move the object only the amount pushed, no velocity
                                obj.y += push_dy
                                obj.vel_y = 0
                            else:
                                # Can't push, stop player movement
                                if dy > 0:
                                    self.p.y = obj.y - self.p.height
                                else:
                                    self.p.y = obj.y + obj.height
                        else:
                            # Normal collision in platformer mode
                            if dy > 0:  # moving down
                                self.p.y = obj.y - self.p.height
                                self.p.vel_y = 0
                                self.p.grounded = True
                            else:       # moving up
                                self.p.y = obj.y + obj.height
                                self.p.vel_y = 0
                    else:
                        # Normal collision
                        if dy > 0:  # moving down
                            self.p.y = obj.y - self.p.height
                            self.p.vel_y = 0
                            if self.p.state == 1:
                                self.p.grounded = True
                        else:       # moving up
                            self.p.y = obj.y + obj.height
                            self.p.vel_y = 0
                    pr = self.p.rect

    def update_player(self):
        # Apply gravity when in platformer mode
        if self.p.state == 1:
            self.p.vel_y += self.p.gravity
            dx = self.p.vel_x
            dy = self.p.vel_y
            self.move_axis(dx, dy)

        else:  # Top‑down movement (no gravity)
            dx = self.p.vel_x
            dy = self.p.vel_y
            self.move_axis(dx, dy)
    
    def update_movable_objects(self):
        # Update physics for all movable objects
        for obj in self.movable_objects:
            # Apply gravity in platformer mode
            if self.p.state == 1:
                obj.vel_y += obj.gravity
            else:
                obj.vel_y = 0
            
            # Move and collide horizontally
            if obj.vel_x != 0:
                obj.x += obj.vel_x
                for other_obj in self.all_solid_objects():
                    if other_obj is not obj and obj.rect.colliderect(other_obj.rect):
                        obj.x = other_obj.x - obj.width if obj.vel_x > 0 else other_obj.x + other_obj.width
                        obj.vel_x = 0
                        break
            
            # Move and collide vertically
            obj.grounded = False
            if obj.vel_y != 0:
                obj.y += obj.vel_y
                for other_obj in self.all_solid_objects():
                    if other_obj is not obj and obj.rect.colliderect(other_obj.rect):
                        if obj.vel_y > 0:  # falling
                            obj.y = other_obj.y - obj.height
                            obj.vel_y = 0
                            obj.grounded = True
                        else:  # moving up
                            obj.y = other_obj.y + other_obj.height
                            obj.vel_y = 0
                        break
            
            # Friction
            if obj.grounded:
                obj.vel_x *= 0.9

    def update_paint_projectiles(self):
        # Update all paint projectiles
        projectiles_to_remove = []
        for paint in self.paint_projectiles:
            # Update paint position
            paint.update()
            
            # Check if projectile has traveled too far
            if paint.distance_traveled >= paint.max_distance:
                projectiles_to_remove.append(paint)
                continue
            
            # Check collision with all solid objects and dead flowers in grid
            collision_found = False
            
            # First check all objects in grid for dead flowers
            for row in self.grid:
                for obj in row:
                    if paint.rect.colliderect(obj.rect):
                        if isinstance(obj, ImmovableProp) and not obj.is_alive:
                            obj.paint()
                        if hasattr(obj, 'is_solid') and obj.is_solid:
                            collision_found = True
                        break
                if collision_found:
                    break
            
            # Then check movable objects and other solid objects
            if not collision_found:
                for obj in self.all_solid_objects():
                    if paint.rect.colliderect(obj.rect):
                        collision_found = True
                        break
            
            if collision_found:
                projectiles_to_remove.append(paint)
        
        # Remove collided or expired projectiles
        for paint in projectiles_to_remove:
            self.paint_projectiles.remove(paint)

    def draw_grid(self):
        self.screen.blit(pygame.image.load(self.background), (0,0))
        for row in self.grid:
            for t in row:
                t.draw(self.screen)
    
    def draw_movable_objects(self):
        for obj in self.movable_objects:
            obj.draw(self.screen)
    
    def draw_paint_projectiles(self):
        for paint in self.paint_projectiles:
            paint.draw(self.screen)
    
    def draw_goal(self):
        if self.goal:
            self.goal.draw(self.screen)
    
    def draw_ui(self):
        # Draw gradient-like UI background
        pygame.draw.rect(self.screen, (45, 45, 55), (0, 0, self.width, self.UI_HEIGHT))
        
        # Draw bottom border line
        pygame.draw.line(self.screen, (20, 20, 30), (0, self.UI_HEIGHT - 1), (self.width, self.UI_HEIGHT - 1), 3)
        
        # Draw paint bar
        self.paintbar.x = 10
        self.paintbar.y = 18
        self.paintbar.draw(self.screen)
        
        # Draw level number
        level_text = self.font_large.render(f"Level {self.level.index}", True, (255, 200, 100))
        level_rect = level_text.get_rect(center=(self.width // 2, 32))
        self.screen.blit(level_text, level_rect)
    
    def reset_level(self):
        # Reset player position and state
        self.p.x = 0
        self.p.y = self.UI_HEIGHT
        self.p.vel_x = 0
        self.p.vel_y = 0
        self.p.state = 1
        self.p.grounded = False
        self.p.direction = 'right'
        self.paintbar.state = 10
        
        # Reload the level
        self.movable_objects = []
        self.paint_projectiles = []
        self.goal = None
        self.grid = self.create_grid()
        self.load_level()

    def next_level(self):
        # Move to next level
        if self.level.index < len(LEVELS):
            self.level = Level(self.level.index + 1, LEVELS[self.level.index])
            self.reset_level()
        else:
            print("You've completed all levels!")

    def previous_level(self):
        # Move to previous level
        if self.level.index > 1:
            self.level = Level(self.level.index - 1, LEVELS[self.level.index - 2])
            self.reset_level()
        else:
            print("You're already on the first level!")

    def run(self):
        running = True
        while running:
            self.clock.tick(self.FPS)

            # Handle events
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        running = False
                    # Reset level
                    if e.key == pygame.K_r:
                        self.reset_level()
                    # Next level
                    if e.key == pygame.K_p:
                        self.next_level()
                    # Previous level
                    if e.key == pygame.K_o:
                        self.previous_level()
                    # Toggle between platformer and top‑down
                    if e.key == pygame.K_SPACE and self.paintbar.state > 2:
                        self.p.state = 2 if self.p.state == 1 else 1
                        self.p.vel_x = 0
                        self.p.vel_y = 0
                        self.paintbar.state = max(1, self.paintbar.state - 2)
                        # Reset velocities of all movable objects
                        for obj in self.movable_objects:
                            obj.vel_x = 0
                            obj.vel_y = 0
                    if e.key == pygame.K_z and self.p.state == 1 and self.paintbar.state > 1 and len(self.paint_projectiles) == 0:
                        # Create paint projectile
                        paint = Paint(self.p.x + self.p.width // 2, self.p.y + self.p.height // 2, self.p.direction)
                        self.paint_projectiles.append(paint)
                        self.paintbar.state = max(1, self.paintbar.state - 1)

            # Handle continuous input
            keys = pygame.key.get_pressed()

            if self.p.state == 1:
                # Left/right input
                if keys[pygame.K_UP] and self.p.grounded:
                    # Jump only in platformer mode
                    self.p.vel_y = self.p.jump_strength
                elif keys[pygame.K_RIGHT]:
                    self.p.vel_x = self.p.speed
                    self.p.direction = 'right'
                elif keys[pygame.K_LEFT]:
                    self.p.vel_x = -self.p.speed
                    self.p.direction = 'left'
                else:
                    self.p.vel_x = 0
            else:
                # Top‑down directional movement
                self.p.vel_x = 0
                self.p.vel_y = 0
                if keys[pygame.K_LEFT]:
                    self.p.vel_x = -self.p.speed
                    self.p.direction = 'left'
                if keys[pygame.K_RIGHT]:
                    self.p.vel_x = self.p.speed
                    self.p.direction = 'right'
                if keys[pygame.K_UP]:
                    self.p.vel_y = -self.p.speed
                if keys[pygame.K_DOWN]:
                    self.p.vel_y = self.p.speed

            # Update physics and collisions
            self.update_player()
            self.update_movable_objects()
            self.update_paint_projectiles()
            
            # Check if player reached goal
            if self.goal and self.p.state == 1 and self.p.rect.colliderect(self.goal.rect):
                self.next_level()

            # Draw frame
            self.screen.fill((255,255,255))
            self.draw_grid()
            self.draw_movable_objects()
            self.draw_paint_projectiles()
            self.draw_goal()
            self.p.draw(self.screen)
            self.draw_ui()
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    player = Player(0,0)
    game = Game(WIDTH, HEIGHT, player, Level(1, LEVELS[0]))
    game.run()