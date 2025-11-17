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

class UnmovableProp(GameObject):
    def __init__(self, x, y, filenames=(None, None), color=(100,100,100), is_alive=False):
        super().__init__(x, y, filenames[0] if is_alive==False else filenames[1], color)
        self.is_alive = is_alive
        self.filenames = filenames
        # Solid tiles collide with the player
        if self.is_alive:
            self.is_solid = True
    def paint(self):
        self.is_alive = True
        self.is_solid = True
        self.filename = self.filenames[1]
        try:
            self.image = pygame.image.load(self.filename)
        except:
            print("Failed to load image:", self.filename)

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
                    self.grid[r][c] = UnmovableProp(x, y, filenames=("images/grass_dead.png", "images/grass.png"), is_alive=False)

    def solid_tiles(self):
        # Generator for tiles that block movement
        for row in self.grid:
            for t in row:
                if hasattr(t, 'is_solid') and t.is_solid:
                    yield t

    def move_axis(self, dx, dy):
        # Horizontal movement and collision resolution
        if dx != 0:
            self.p.x += dx
            pr = self.p.rect
            for tile in self.solid_tiles():
                if pr.colliderect(tile.rect):
                    if dx > 0:  # moving right
                        self.p.x = tile.x - self.p.width
                    else:       # moving left
                        self.p.x = tile.x + tile.width
                    pr = self.p.rect

        # Vertical movement and collision resolution
        self.p.grounded = False
        if dy != 0:
            self.p.y += dy
            pr = self.p.rect
            for tile in self.solid_tiles():
                if pr.colliderect(tile.rect):
                    if dy > 0:  # moving down
                        self.p.y = tile.y - self.p.height
                        self.p.vel_y = 0
                        self.p.grounded = True
                    else:       # moving up
                        self.p.y = tile.y + tile.height
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

    def draw_grid(self):
        for row in self.grid:
            for t in row:
                t.draw(self.screen)

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
                    if e.key == pygame.K_z and self.p.state == 2:
                        # Scan for nearby unmovable props to paint
                        if self.p.direction == 'right':
                            if self.grid[self.p.y // self.tile_size][self.p.x // self.tile_size].__class__ == UnmovableProp or self.grid[self.p.y // self.tile_size][self.p.x // self.tile_size + 1].__class__ == UnmovableProp:
                                if self.grid[self.p.y // self.tile_size][self.p.x // self.tile_size].__class__ == UnmovableProp:
                                    prop = self.grid[self.p.y // self.tile_size][self.p.x // self.tile_size]
                                else:
                                    prop = self.grid[self.p.y // self.tile_size][self.p.x // self.tile_size + 1]
                                prop.paint()
                        if self.p.direction == 'left':
                            if self.grid[self.p.y // self.tile_size][self.p.x // self.tile_size].__class__ == UnmovableProp or self.grid[self.p.y // self.tile_size][self.p.x // self.tile_size - 1].__class__ == UnmovableProp:
                                if self.grid[self.p.y // self.tile_size][self.p.x // self.tile_size].__class__ == UnmovableProp:
                                    prop = self.grid[self.p.y // self.tile_size][self.p.x // self.tile_size]
                                else:
                                    prop = self.grid[self.p.y // self.tile_size][self.p.x // self.tile_size - 1]
                                prop.paint()

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
                if keys[pygame.K_RIGHT]:
                    self.p.vel_x = self.p.speed
                if keys[pygame.K_UP]:
                    self.p.vel_y = -self.p.speed
                if keys[pygame.K_DOWN]:
                    self.p.vel_y = self.p.speed

            # Update physics and collisions
            self.update_player()

            # Draw frame
            self.screen.fill((255,255,255))
            self.draw_grid()
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
#..........##..........#
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
    player = Player(0,0)#filename="images/Character.png")
    game = Game(WIDTH, HEIGHT, player, level)
    game.run()
