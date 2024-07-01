import pygame as pg
from random import randint

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость:
SPEED = 20

# Инициализация pygame:
pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption('Змейка')
clock = pg.time.Clock()

# Начальная позиция змейки:
INITIAL_SNAKE_POSITION = (
    (GRID_WIDTH // 2) * GRID_SIZE,
    (GRID_HEIGHT // 2) * GRID_SIZE
)

# Словарь для определения возможных поворотов:
TURNS = {
    (pg.K_UP, LEFT): UP,
    (pg.K_UP, RIGHT): UP,
    (pg.K_DOWN, LEFT): DOWN,
    (pg.K_DOWN, RIGHT): DOWN,
    (pg.K_LEFT, UP): LEFT,
    (pg.K_LEFT, DOWN): LEFT,
    (pg.K_RIGHT, UP): RIGHT,
    (pg.K_RIGHT, DOWN): RIGHT
}

TURN_KEYS = set(event_key for event_key, _ in TURNS)

# Начальное направление:
INITIAL_DIRECTION = RIGHT


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position=None, body_color=None):
        """Инициализация GameObject."""
        self.position = position
        self.body_color = body_color

    def draw_cell(self, screen, position, color):
        """Отрисовка одной ячейки объекта на экране."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)

    def draw(self, screen):
        """Отрисовка объекта на экране."""
        raise NotImplementedError


class Apple(GameObject):
    """Класс, представляющий яблоко в игре."""

    def __init__(self, snake=None):
        """Инициализация яблока."""
        super().__init__()
        self.snake = snake if snake else Snake()
        self.reset_position()

    def reset_position(self):
        """Сброс яблока и случайная генерация его позиции."""
        self.randomize_position()
        self.body_color = APPLE_COLOR

    def draw(self, screen):
        """Отрисовка яблока на экране."""
        self.draw_cell(screen, self.position, self.body_color)

    def randomize_position(self):
        """Случайная генерация позиции яблока."""
        while True:
            x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            self.position = (x, y)
            # Проверка, что позиция не занята змеей
            if self.position not in self.snake.positions:
                break


class Snake(GameObject):
    """Класс, представляющий змейку в игре."""

    def __init__(self):
        """Инициализация змейки."""
        super().__init__()
        self.reset()

    def reset(self):
        """Сброс змейки в начальное состояние."""
        self.positions = [INITIAL_SNAKE_POSITION]
        self.direction = RIGHT
        self.body_color = SNAKE_COLOR
        self.length = 1
        self.last_tail_position = None  # Последняя позиция хвоста
        self.self_collision = False  # Флаг для обнаружения самоукуса

    def draw(self, screen):
        """Отрисовка змейки на экране."""
        # Отрисовываем тело змеи
        for position in self.positions:
            self.draw_cell(screen, position, self.body_color)

        # Если есть последняя позиция хвоста, затираем её
        if self.last_tail_position:
            self.draw_cell(
                screen,
                self.last_tail_position,
                BOARD_BACKGROUND_COLOR
            )

    def move(self):
        """Движение змейки в текущем направлении."""
        # Получаем текущую позицию головы змеи
        x, y = self.get_head_position()
        dx, dy = self.direction

        # Вычисляем новую позицию головы змеи
        new_head = (
            (x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (y + dy * GRID_SIZE) % SCREEN_HEIGHT
        )
        # Проверяем, не столкнулась ли голова змеи с её телом
        if new_head in self.positions:
            self.self_collision = True

        # Добавляем новую позицию головы в начало списка позиций
        self.positions.insert(0, new_head)

        # Удаляем последний элемент списка позиций, если длина превышает
        if len(self.positions) > self.length:
            self.last_tail_position = self.positions.pop()
        else:
            self.last_tail_position = None

    def update_direction(self, new_direction):
        """Обновление направления движения змейки."""
        if new_direction in {UP, DOWN, LEFT, RIGHT}:
            self.direction = new_direction

    def get_head_position(self):
        """Получение текущей позиции головы змеи."""
        return self.positions[0]


class Game:
    """Класс, представляющий игровую логику и состояние."""

    def __init__(self):
        """Инициализация игры со змейкой и яблоком."""
        self.snake = Snake()
        self.apple = Apple(self.snake)

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

        if self.snake.self_collision:
            self.snake.reset()
            self.snake.self_collision = False

        if self.snake.get_head_position() == self.apple.position:
            self.snake.length += 1
            self.apple.reset_position()


def handle_keys(snake):
    """Обработка ввода с клавиатуры для управления направлением змейки."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type == pg.KEYDOWN:
            if event.key in TURN_KEYS:
                key_direction = (event.key, snake.direction)
                new_direction = TURNS.get(key_direction, snake.direction)
                snake.update_direction(new_direction)


def main():
    """Основная функция для запуска игры."""
    game = Game()
    while True:
        handle_keys(game.snake)
        game.update()
        game.draw(screen)
        pg.display.flip()
        clock.tick(SPEED)


if __name__ == "__main__":
    main()
