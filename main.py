import pygame

pygame.init()

WIDTH, HEIGHT = 768, 512

class Player:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, 32, 32))

class GameObject:
    def __init__(self, x, y, filename=None, color=(200, 200, 200)):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.color = color
        self.image = None
        
        if filename:
            try:
                self.image = pygame.image.load(filename)
                self.width = self.image.get_width()
                self.height = self.image.get_height()
            except:
                pass

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(surface, (100, 100, 100), (self.x, self.y, self.width, self.height), 1)

class Game:
    def __init__(self, width, height, player, caption="Game", FPS=60):
        self.width = width
        self.height = height
        self.p = player
        self.FPS = FPS
        self.caption = caption
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.grid = self.create_grid()

    def create_grid(self):
        """Create a grid of 32x32 GameObject squares"""
        grid = []
        tile_size = 32
        cols = self.width // tile_size
        rows = self.height // tile_size
        
        for row in range(rows):
            grid_row = []
            for col in range(cols):
                x = col * tile_size
                y = row * tile_size
                grid_row.append(GameObject(x, y))
            grid.append(grid_row)
        
        return grid

    def run(self):
        pygame.display.set_caption(self.caption)

        self.running = True
        while self.running:
            self.clock.tick(self.FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    if event.key == pygame.K_LEFT:
                        self.p.x -= 8
                    if event.key == pygame.K_RIGHT:
                        self.p.x += 8
            
            self.screen.fill((255, 255, 255))
            
            # Draw grid
            for row in self.grid:
                for tile in row:
                    tile.draw(self.screen)
            
            self.p.draw(self.screen)
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    player = Player(64, 64, (0, 128, 255))
    game = Game(WIDTH, HEIGHT, player)
    game.run()