import pygame
import sys
import random

WIDTH, HEIGHT = 10, 20
BLOCK_SIZE = 30
SCREEN_WIDTH = WIDTH * BLOCK_SIZE + 200
SCREEN_HEIGHT = HEIGHT * BLOCK_SIZE
FIELD_COLOR = (30, 30, 40)
GRID_COLOR = (60, 60, 80)

COLORS = [
    (0, 255, 255),  # I
    (0, 0, 255),    # J
    (255, 165, 0),  # L
    (255, 255, 0),  # O
    (0, 255, 0),    # S
    (128, 0, 128),  # T
    (255, 0, 0),    # Z
]

FIGURES = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1], [1, 1]],        # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # Z
]

FONT_NAME = "arial"

def rotate(shape):
    return [ [ shape[y][x] for y in range(len(shape)) ] for x in range(len(shape[0])-1, -1, -1) ]

class Tetromino:
    def __init__(self, x, y, figure, color):
        self.x, self.y = x, y
        self.shape = figure
        self.color = color

    def image(self):
        return self.shape

    def rotate(self):
        self.shape = rotate(self.shape)

class Tetris:
    def __init__(self):
        self.field = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.score = 0
        self.state = "start"
        self.figure = None
        self.next_figure = self.new_figure()
        self.level = 1
        self.lines = 0

    def new_figure(self):
        idx = random.randint(0, len(FIGURES)-1)
        return Tetromino(WIDTH // 2 - len(FIGURES[idx][0]) // 2, 0, [row[:] for row in FIGURES[idx]], COLORS[idx])

    def spawn_figure(self):
        self.figure = self.next_figure
        self.next_figure = self.new_figure()
        if self.collision():
            self.state = "gameover"

    def collision(self):
        shape = self.figure.image()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    fx = self.figure.x + x
                    fy = self.figure.y + y
                    if fx < 0 or fx >= WIDTH or fy >= HEIGHT or (fy >= 0 and self.field[fy][fx]):
                        return True
        return False

    def freeze(self):
        shape = self.figure.image()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    fx = self.figure.x + x
                    fy = self.figure.y + y
                    if fy >= 0:
                        self.field[fy][fx] = self.figure.color
        self.clear_lines()
        self.spawn_figure()

    def clear_lines(self):
        lines = 0
        for y in range(HEIGHT-1, -1, -1):
            if 0 not in self.field[y]:
                del self.field[y]
                self.field.insert(0, [0 for _ in range(WIDTH)])
                lines += 1
        self.lines += lines
        if lines == 1:
            self.score += 100
        elif lines == 2:
            self.score += 300
        elif lines == 3:
            self.score += 500
        elif lines >= 4:
            self.score += 800
        self.level = 1 + self.lines // 10

    def reset(self):
        self.__init__()

def draw_grid(screen):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            pygame.draw.rect(
                screen,
                GRID_COLOR,
                (x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                1
            )

def draw_field(screen, game):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            color = game.field[y][x]
            if color:
                pygame.draw.rect(
                    screen,
                    color,
                    (x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                )

def draw_tetromino(screen, tetromino, offset=(0,0)):
    if tetromino is None:
        return
    shape = tetromino.image()
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                fx = tetromino.x + x + offset[0]
                fy = tetromino.y + y + offset[1]
                if fy >= 0:
                    pygame.draw.rect(
                        screen,
                        tetromino.color,
                        (fx*BLOCK_SIZE, fy*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                    )

def draw_next_figure(screen, next_figure):
    shape = next_figure.image()
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(
                    screen,
                    next_figure.color,
                    (WIDTH*BLOCK_SIZE + 60 + x*BLOCK_SIZE, 60 + y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                )

def draw_text(screen, text, size, x, y, color=(255,255,255)):
    font = pygame.font.SysFont(FONT_NAME, size, bold=True)
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()

    game = Tetris()
    fall_time = 0
    speed = 700
    paused = False

    game.spawn_figure()

    while True:
        dt = clock.tick(60)
        if not paused and game.state == "start":
            fall_time += dt
            speed = max(100, 700 - (game.level-1)*50)
            if fall_time > speed:
                if game.figure is not None:
                    game.figure.y += 1
                    if game.collision():
                        game.figure.y -= 1
                        game.freeze()
                fall_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if game.state == "start" and not paused:
                    if event.key == pygame.K_LEFT:
                        game.figure.x -= 1
                        if game.collision():
                            game.figure.x += 1
                    elif event.key == pygame.K_RIGHT:
                        game.figure.x += 1
                        if game.collision():
                            game.figure.x -= 1
                    elif event.key == pygame.K_DOWN:
                        game.figure.y += 1
                        if game.collision():
                            game.figure.y -= 1
                    elif event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                        old_shape = [row[:] for row in game.figure.shape]
                        game.figure.rotate()
                        if game.collision():
                            game.figure.shape = old_shape
                    elif event.key == pygame.K_p:
                        paused = not paused
                    elif event.key == pygame.K_r:
                        game.reset()
                        game.spawn_figure()
                        fall_time = 0
                        paused = False
                elif event.key == pygame.K_r:
                    game.reset()
                    game.spawn_figure()
                    fall_time = 0
                    paused = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_p:
                    paused = not paused

        screen.fill(FIELD_COLOR)
        draw_field(screen, game)
        if game.state == "start" and game.figure is not None:
            draw_tetromino(screen, game.figure)
        draw_grid(screen)

        pygame.draw.rect(screen, (24,24,24), (WIDTH*BLOCK_SIZE, 0, 200, SCREEN_HEIGHT))
        draw_text(screen, "Наступна:", 24, WIDTH*BLOCK_SIZE+60, 20)
        draw_next_figure(screen, game.next_figure)
        draw_text(screen, f"Рахунок: {game.score}", 24, WIDTH*BLOCK_SIZE+40, 180)
        draw_text(screen, f"Лінії: {game.lines}", 24, WIDTH*BLOCK_SIZE+40, 220)
        draw_text(screen, f"Рівень: {game.level}", 24, WIDTH*BLOCK_SIZE+40, 260)
        draw_text(screen, "P - пауза", 18, WIDTH*BLOCK_SIZE+40, 320)
        draw_text(screen, "R - рестарт", 18, WIDTH*BLOCK_SIZE+40, 350)
        draw_text(screen, "Q - вихід", 18, WIDTH*BLOCK_SIZE+40, 380)

        if paused and game.state == "start":
            draw_text(screen, "Пауза", 36, 90, SCREEN_HEIGHT//2-30, (255,255,0))
        if game.state == "gameover":
            draw_text(screen, "Game Over!", 36, 70, SCREEN_HEIGHT//2-30, (255,0,0))
            draw_text(screen, "R - рестарт, Q - вихід", 24, 30, SCREEN_HEIGHT//2+20, (255,255,255))

        pygame.display.flip()

if __name__ == "__main__":
    main()