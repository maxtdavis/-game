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
    def __init__(self, x, y, filename):
        self.x = x
        self.y = y
        self.image = pygame.image.load(filename)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

class Game:
    def __init__(self, width, height, player, caption="Game", FPS=60):
        self.width = width
        self.height = height
        self.p = player
        self.FPS = FPS
        self.caption = caption
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.width, self.height))

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
                        self.p.x -= 10
                    if event.key == pygame.K_RIGHT:
                        self.p.x += 10
            
            self.screen.fill((255, 255, 255))
            self.p.draw(self.screen)
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    player = Player(100, 100, (0, 128, 255))
    game = Game(WIDTH, HEIGHT, player)
    game.run()