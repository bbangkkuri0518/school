import pygame
import pygame_gui
import numpy as np
from sklearn.linear_model import LinearRegression

pygame.init()
WIDTH, HEIGHT = 1600, 900
GRID_SIZE = 800
GRID_ORIGIN = (400, 50)
CELL_COUNT = 21
CELL_SIZE = GRID_SIZE // (CELL_COUNT - 1)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("몰농도-굴절률 그래프")
manager = pygame_gui.UIManager((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# 한글 폰트 설정
font_path = "C:/Windows/Fonts/malgun.ttf"  # 맑은 고딕
font = pygame.font.Font(font_path, 20)

# UI 요소
input_lines = []
input_start_y = 30
add_button_y = input_start_y


def create_input_line(y):
    x_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((30, y), (100, 30)), manager=manager)
    y_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((140, y), (100, 30)), manager=manager)
    remove_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((250, y), (30, 30)), text='-', manager=manager)
    return {'x': x_entry, 'y': y_entry, 'remove': remove_button, 'y_pos': y}


def update_add_button():
    global add_button
    add_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((30, add_button_y), (50, 30)), text='+', manager=manager)


def draw_grid():
    for i in range(CELL_COUNT):
        x = GRID_ORIGIN[0] + i * CELL_SIZE
        y = GRID_ORIGIN[1] + i * CELL_SIZE
        pygame.draw.line(screen, (230, 230, 230), (x, GRID_ORIGIN[1]), (x, GRID_ORIGIN[1] + GRID_SIZE))
        pygame.draw.line(screen, (230, 230, 230), (GRID_ORIGIN[0], y), (GRID_ORIGIN[0] + GRID_SIZE, y))

    # x축 (화살표 - 가장 아래쪽 라인으로 이동)
    pygame.draw.line(screen, (0, 0, 0), (GRID_ORIGIN[0], GRID_ORIGIN[1] + GRID_SIZE), (GRID_ORIGIN[0] + GRID_SIZE + 20, GRID_ORIGIN[1] + GRID_SIZE), 2)
    pygame.draw.polygon(screen, (0, 0, 0), [
        (GRID_ORIGIN[0] + GRID_SIZE + 20, GRID_ORIGIN[1] + GRID_SIZE),
        (GRID_ORIGIN[0] + GRID_SIZE + 10, GRID_ORIGIN[1] + GRID_SIZE - 5),
        (GRID_ORIGIN[0] + GRID_SIZE + 10, GRID_ORIGIN[1] + GRID_SIZE + 5)
    ])

    # y축 (화살표)
    pygame.draw.line(screen, (0, 0, 0), (GRID_ORIGIN[0], GRID_ORIGIN[1] + GRID_SIZE), (GRID_ORIGIN[0], GRID_ORIGIN[1] - 20), 2)
    pygame.draw.polygon(screen, (0, 0, 0), [
        (GRID_ORIGIN[0], GRID_ORIGIN[1] - 20),
        (GRID_ORIGIN[0] - 5, GRID_ORIGIN[1] - 10),
        (GRID_ORIGIN[0] + 5, GRID_ORIGIN[1] - 10)
    ])

    # 축 이름 텍스트
    text_x_label = font.render("몰 농도(M, mol/L)", True, (0, 0, 0))
    screen.blit(text_x_label, (GRID_ORIGIN[0] + GRID_SIZE + 30, GRID_ORIGIN[1] + GRID_SIZE - 15))

    text_y_label = font.render("굴절률", True, (0, 0, 0))
    screen.blit(text_y_label, (GRID_ORIGIN[0] - 30, GRID_ORIGIN[1] - 40))

    for i in range(CELL_COUNT):
        x_value = i * 0.1
        y_value = 1.0 + i * 0.025
        x = GRID_ORIGIN[0] + i * CELL_SIZE
        y = GRID_ORIGIN[1] + GRID_SIZE - i * CELL_SIZE
        if x_value <= 2.0:
            text = font.render(f"{x_value:.1f}", True, (0, 0, 0))
            screen.blit(text, (x - 10, GRID_ORIGIN[1] + GRID_SIZE + 5))
        if y_value <= 1.5:
            text = font.render(f"{y_value:.3f}", True, (0, 0, 0))
            screen.blit(text, (GRID_ORIGIN[0] - 60, y - 5))


# 점과 상태 변수
points = []


def draw_points_and_line(points):
    if not points:
        return

    points_sorted = sorted(points, key=lambda p: p[0])
    xs = np.array([p[0] for p in points_sorted]).reshape(-1, 1)
    ys = np.array([p[1] for p in points_sorted])

    x_min, x_max = 0.0, 2.0
    y_min, y_max = 1.0, 1.5

    def to_screen(x, y):
        sx = GRID_ORIGIN[0] + ((x - x_min) / (x_max - x_min)) * GRID_SIZE
        sy = GRID_ORIGIN[1] + GRID_SIZE - ((y - y_min) / (y_max - y_min)) * GRID_SIZE
        return int(sx), int(sy)

    for x, y in zip(xs, ys):
        sx, sy = to_screen(x[0], y)
        pygame.draw.circle(screen, (0, 0, 255), (sx, sy), 5)

    model = LinearRegression()
    model.fit(xs, ys)
    slope = model.coef_[0]
    intercept = model.intercept_

    x_pred = np.linspace(x_min, x_max, 100).reshape(-1, 1)
    y_pred = model.predict(x_pred)

    for i in range(len(x_pred) - 1):
        x1, y1 = to_screen(x_pred[i][0], y_pred[i])
        x2, y2 = to_screen(x_pred[i + 1][0], y_pred[i + 1])
        pygame.draw.line(screen, (255, 0, 0), (x1, y1), (x2, y2), 2)

    slope_text = font.render(f"기울기: {slope:.4f}", True, (0, 0, 0))
    screen.blit(slope_text, (GRID_ORIGIN[0] + GRID_SIZE + 40, GRID_ORIGIN[1]))

    errors = np.abs((ys - model.predict(xs)) / ys) * 100
    mean_error = np.mean(errors)
    error_text = font.render(f"평균 오차율: {mean_error:.2f}%", True, (200, 0, 0))
    screen.blit(error_text, (GRID_ORIGIN[0] + GRID_SIZE + 40, GRID_ORIGIN[1] + 30))


# 초기 입력 줄 하나 생성
input_lines.append(create_input_line(add_button_y))
add_button_y += 40
update_add_button()

running = True
while running:
    time_delta = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == add_button:
                    input_lines.append(create_input_line(add_button_y))
                    add_button_y += 40
                    add_button.kill()
                    update_add_button()
                else:
                    for line in input_lines:
                        if event.ui_element == line['remove']:
                            line['x'].kill()
                            line['y'].kill()
                            line['remove'].kill()
                            input_lines.remove(line)
                            break

        manager.process_events(event)

    points.clear()
    for line in sorted(input_lines, key=lambda l: l['x'].get_text() if l['x'].get_text().replace('.', '', 1).isdigit() else '999'):
        try:
            x_val = float(line['x'].get_text())
            y_val = float(line['y'].get_text())
            points.append((x_val, y_val))
        except ValueError:
            continue

    manager.update(time_delta)
    screen.fill((255, 255, 255))
    draw_grid()
    draw_points_and_line(points)
    manager.draw_ui(screen)
    pygame.display.update()

pygame.quit()
