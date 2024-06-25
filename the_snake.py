import pygame as pg
from random import choice, randint

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position=None, body_color=None):
        """Инициализация GameObject."""
        self.position = position
        self.body_color = body_color

    def draw_cell(self, screen):
        """Отрисовка одной ячейки объекта на экране."""
        rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self, screen):
        """Отрисовка объекта на экране."""
        raise NotImplementedError


class Apple(GameObject):
    """Класс, представляющий яблоко в игре."""

    def __init__(self):
        """Инициализация яблока."""
        super().__init__()
        self.reset_position()

    def reset_position(self):
        """Сброс яблока и случайная генерация его позиции."""
        self.randomize_position()
        self.body_color = APPLE_COLOR

    def draw(self, screen):
        """Отрисовка яблока на экране."""
        rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self):
        """Случайная генерация позиции яблока."""
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )


class Snake(GameObject):
    """Класс, представляющий змейку в игре."""

    def __init__(self):
        """Инициализация змейки."""
        self.eat_food = False
        super().__init__()
        self.reset_snake()

    def reset_snake(self):
        """Сброс змейки с начальной позицией и направлением."""
        self.positions = [
            (GRID_WIDTH // 2 * GRID_SIZE, GRID_HEIGHT // 2 * GRID_SIZE)
        ]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.body_color = SNAKE_COLOR
        self.last = None

    def draw(self, screen):
        """Отрисовка змейки на экране."""
        for position in self.positions:
            rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, self.body_color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def move(self):
        """Движение змейки в текущем направлении."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

        x, y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (y + dy * GRID_SIZE) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head)
        if self.eat_food:
            self.eat_food = False
        else:
            self.positions.pop()
        self.last = self.positions[-1]

    def eat(self, apple):
        """Увеличение длины змейки при поедании яблока."""
        self.positions.append(self.last)

    def update_direction(self, new_direction):
        """Обновление направления движения змейки."""
        if new_direction in [UP, DOWN, LEFT, RIGHT]:
            self.next_direction = new_direction

    def get_head_position(self):
        """Получение текущей позиции головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сброс змейки в начальное состояние."""
        self.positions = [
            (GRID_WIDTH // 2 * GRID_SIZE, GRID_HEIGHT // 2 * GRID_SIZE)
        ]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None


class Game:
    """Класс, представляющий игровую логику и состояние."""

    def __init__(self):
        """Инициализация игры со змейкой и яблоком."""
        self.apple = Apple()
        self.snake = Snake()

    def draw(self, screen):
        """Отрисовка всех игровых объектов на экране."""
        screen.fill(BOARD_BACKGROUND_COLOR)
        self.snake.draw(screen)
        self.apple.draw(screen)

    def update(self):
        """Обновление состояния игры."""
        self.snake.move()
        self.check_collision()

    def check_collision(self):
        """Проверка на столкновения змейки со стенами и яблоком."""
        head_x, head_y = self.snake.get_head_position()
        if (
            head_x < 0
            or head_x >= SCREEN_WIDTH
            or head_y < 0
            or head_y >= SCREEN_HEIGHT
        ):
            self.snake.reset()

        if self.snake.positions[0] in self.snake.positions[1:]:
            self.snake.reset()

        if self.snake.get_head_position() == self.apple.position:
            self.snake.eat(self.apple)
            self.apple.randomize_position()


def handle_keys(snake):
    """Обработка ввода с клавиатуры для управления направлением змейки."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            key_direction_map = {
                pg.K_UP: UP,
                pg.K_DOWN: DOWN,
                pg.K_LEFT: LEFT,
                pg.K_RIGHT: RIGHT
            }
            if event.key in key_direction_map:
                direction = key_direction_map[event.key]
                if (direction == UP and snake.direction != DOWN) or \
                    (direction == DOWN and snake.direction != UP) or \
                    (direction == LEFT and snake.direction != RIGHT) or \
                        (direction == RIGHT and snake.direction != LEFT):
                    snake.update_direction(direction)


def main():
    """Основная функция для запуска игры."""
    game = Game()

    while True:
        clock.tick(SPEED)
        handle_keys(game.snake)
        game.update()
        game.draw(screen)
        pg.display.update()


if __name__ == '__main__':
    main()
