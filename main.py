# Added comments throughout explaining purpose and logic of each part.

import pygame
pygame.init()

WIDTH, HEIGHT = 768, 512

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

    @property
    def rect(self):
        # Collision rectangle
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surf):
        # Draw player
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
                pass

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

class Terrain(GameObject):
    def __init__(self, x, y, filename=None, color=(139,69,19)):
        super().__init__(x, y, filename, color)
        # Solid tiles collide with the player
        self.is_solid = True

class ImmovableProp(GameObject):
    def __init__(self, x, y, filenames=(None, None), color=(100,100,100), is_alive=False):
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
        # Head riding mechanic
        self.on_player_head = False
    
    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surf):
        if self.image:
            surf.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(surf, self.color, self.rect)

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

        # Grid of tiles (background by default)
        self.grid = self.create_grid()
        # List to store movable objects
        self.movable_objects = []
        # Track which movable object is on player's head
        self.object_on_player_head = None
        # Replace tiles based on level map
        self.load_level()

    def create_grid(self):
        # Basic grid filled with background tiles
        cols = self.width // self.tile_size
        rows = self.height // self.tile_size
        return [[Background(c*self.tile_size, r*self.tile_size) for c in range(cols)] for r in range(rows)]

    def load_level(self):
        # Parse level map string and place tiles accordingly
        lines = self.level.map.strip().split("\n")
        for r, line in enumerate(lines):
            for c, ch in enumerate(line):
                x = c * self.tile_size
                y = r * self.tile_size

                if ch == '.':   # Air / sky
                    self.grid[r][c] = Background(x, y, color=(135,206,235))
                elif ch == '#': # Solid terrain
                    self.grid[r][c] = Terrain(x, y, filename="images/grass.png")
                elif ch == 'P': # Player spawn
                    self.p.x = x
                    self.p.y = y
                    self.grid[r][c] = Background(x, y, color=(135,206,235))
                elif ch == 'i': # Interactive prop
                    self.grid[r][c] = ImmovableProp(x, y, filenames=("images/flower_dead.png", "images/flower_alive.png"), is_alive=False)
                elif ch == 'M': # Movable object
                    self.grid[r][c] = Background(x, y, color=(135,206,235))
                    self.movable_objects.append(MovableObject(x, y, filename="images/crate.png"))

    def solid_tiles(self):
        # Generator for tiles that block movement
        for row in self.grid:
            for t in row:
                if hasattr(t, 'is_solid') and t.is_solid:
                    yield t
    
    def all_solid_objects(self):
        # Generator for all solid objects (tiles + movable objects)
        for obj in self.solid_tiles():
            yield obj
        for obj in self.movable_objects:
            yield obj

    def move_axis(self, dx, dy):
        # Horizontal movement and collision resolution
        if dx != 0:
            self.p.x += dx
            pr = self.p.rect
            for obj in self.all_solid_objects():
                # Skip object on player's head
                if obj is self.object_on_player_head:
                    continue
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
                            obj.vel_x = push_dx
                            obj.x += push_dx
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
                # Skip object on player's head
                if obj is self.object_on_player_head:
                    continue
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
                                obj.vel_y = push_dy
                                obj.y += push_dy
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
            # Check if object is on player's head
            if self.p.state == 1 and obj.on_player_head:
                # Object moves with player horizontally
                obj.x = self.p.x + (self.p.width - obj.width) // 2
                # Object stays on top of player
                obj.y = self.p.y - obj.height
                obj.vel_x = 0
                obj.vel_y = 0
                obj.grounded = True
                continue
            
            # Reset head flag if not on head
            obj.on_player_head = False
            
            # Apply gravity in platformer mode
            if self.p.state == 1:
                obj.vel_y += obj.gravity
            else:
                obj.vel_y = 0  # No gravity in top-down mode
            
            # Apply velocity
            dx = obj.vel_x
            dy = obj.vel_y
            
            # Horizontal collision
            if dx != 0:
                obj.x += dx
                or_rect = obj.rect
                for other_obj in self.all_solid_objects():
                    if other_obj is not obj and or_rect.colliderect(other_obj.rect):
                        if dx > 0:
                            obj.x = other_obj.x - obj.width
                        else:
                            obj.x = other_obj.x + other_obj.width
                        obj.vel_x = 0
                        break
            
            # Vertical collision
            obj.grounded = False
            if dy != 0:
                obj.y += dy
                or_rect = obj.rect
                for other_obj in self.all_solid_objects():
                    if other_obj is not obj and or_rect.colliderect(other_obj.rect):
                        if dy > 0:  # falling
                            obj.y = other_obj.y - obj.height
                            obj.vel_y = 0
                            obj.grounded = True
                            # Check if landing on player's head (object directly above player)
                            if self.p.state == 1 and other_obj is self.p:
                                obj.on_player_head = True
                                self.object_on_player_head = obj
                        else:  # moving up
                            obj.y = other_obj.y + other_obj.height
                            obj.vel_y = 0
                        break
            
            # Friction
            if obj.grounded:
                obj.vel_x *= 0.9

    def draw_grid(self):
        for row in self.grid:
            for t in row:
                t.draw(self.screen)
    
    def draw_movable_objects(self):
        for obj in self.movable_objects:
            obj.draw(self.screen)

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
                    # Toggle between platformer and top‑down
                    if e.key == pygame.K_SPACE:
                        self.p.state = 2 if self.p.state == 1 else 1
                        self.p.vel_x = 0
                        self.p.vel_y = 0
                        # Reset velocities of all movable objects
                        for obj in self.movable_objects:
                            obj.vel_x = 0
                            obj.vel_y = 0
                    if e.key == pygame.K_z and self.p.state == 1:
                        # Calculate player's center position in grid coordinates
                        player_grid_x = (self.p.x + self.p.width // 2) // self.tile_size
                        player_grid_y = (self.p.y + self.p.height // 2) // self.tile_size
                        
                        # Scan for nearby unmovable props to paint
                        prop = None
                        if self.p.direction == 'right':
                            # Check tile to the right
                            check_x = player_grid_x + 1
                            if 0 <= check_x < len(self.grid[0]) and 0 <= player_grid_y < len(self.grid):
                                if isinstance(self.grid[player_grid_y][check_x],ImmovableProp):
                                    prop = self.grid[player_grid_y][check_x]
                        elif self.p.direction == 'left':
                            # Check tile to the left
                            check_x = player_grid_x - 1
                            if 0 <= check_x < len(self.grid[0]) and 0 <= player_grid_y < len(self.grid):
                                if isinstance(self.grid[player_grid_y][check_x], ImmovableProp):
                                    prop = self.grid[player_grid_y][check_x]
                        
                        if prop:
                            prop.paint()

            # Handle continuous input
            keys = pygame.key.get_pressed()

            if self.p.state == 1:
                # Left/right input
                if keys[pygame.K_UP] and self.p.grounded:
                    # If object is on player's head, eject it instead of jumping
                    if self.object_on_player_head:
                        self.object_on_player_head.on_player_head = False
                        self.object_on_player_head.vel_y = -10
                        self.object_on_player_head = None
                    else:
                        # Jump only in platformer mode when not carrying
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

            # Draw frame
            self.screen.fill((255,255,255))
            self.draw_grid()
            self.draw_movable_objects()
            self.p.draw(self.screen)
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    LEVEL_1_MAP = """
########################
#......................#
#......................#
#......P...............#
#......................#
#.......#..............#
#..........##...M......#
#.............###......#
####...................#
##.....................#
##.....................#
##.....................#
##.....................#
##.............i.......#
########################
######################## 
"""

    level = Level(1, LEVEL_1_MAP)
    player = Player(0,0, filename="images/Character_Idle_1.png")
    game = Game(WIDTH, HEIGHT, player, level)
    game.run()