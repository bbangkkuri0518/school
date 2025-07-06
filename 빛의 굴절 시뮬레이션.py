import pygame
import pygame_gui
import math

pygame.init()
WIDTH, HEIGHT = 1600, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("굴절 시뮬레이션")
clock = pygame.time.Clock()
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

font = pygame.font.Font(pygame.font.match_font('malgungothic'), 30)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NAVY = (0, 0, 128)
RED = (255, 0, 0)
LIGHT_GRAY = (220, 220, 220)
SKY_BLUE = (173, 216, 230)
GREEN = (0, 200, 0)
PURPLE_FADE = (200, 160, 255)

center_x, center_y = WIDTH // 2, HEIGHT // 2
R = 250
laser_radius = R * 1.2

n1 = 1.0003
molar_concentration = 1.0

def interpolate_n(concentration):
    return 0.0444 * concentration + 1.3310

concentration_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((50, 50), (300, 30)),
    start_value=molar_concentration,
    value_range=(0.0, 2.0),
    manager=manager
)

concentration_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((360, 50), (80, 30)),
    manager=manager
)
concentration_input.set_text(f"{molar_concentration:.2f}")

angle_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((50, 90), (80, 30)),
    manager=manager
)
angle_input.set_text("0.0")

afterimage_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((50, 700), (150, 40)),
    text='잔상 남기기',
    manager=manager
)

clear_afterimage_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((210, 700), (150, 40)),
    text='잔상 지우기',
    manager=manager
)

def draw_text(text, pos):
    screen.blit(font.render(text, True, BLACK), pos)

def get_refracted_angle_signed(incidence_deg, n1, n2):
    incidence_rad = math.radians(abs(incidence_deg))
    try:
        sin_b = (n1 / n2) * math.sin(incidence_rad)
        if abs(sin_b) > 1:
            return None
        refraction_rad = math.asin(sin_b)
        refraction_deg = math.degrees(refraction_rad)
        return refraction_deg if incidence_deg >= 0 else -refraction_deg
    except:
        return None

def draw_protractor_top():
    radius = R + 50
    for angle in range(-90, 91):
        rad = math.radians(angle)
        x1 = center_x + radius * math.sin(rad)
        y1 = center_y - radius * math.cos(rad)
        inner_radius = radius - (10 if angle % 10 == 0 else 5)
        x2 = center_x + inner_radius * math.sin(rad)
        y2 = center_y - inner_radius * math.cos(rad)
        pygame.draw.line(screen, BLACK, (x1, y1), (x2, y2), 1)
        if angle % 10 == 0:
            tx = center_x + (radius + 15) * math.sin(rad)
            ty = center_y - (radius + 15) * math.cos(rad)
            label = font.render(f"{abs(angle)}", True, BLACK)
            screen.blit(label, label.get_rect(center=(tx, ty)))

def draw_protractor_bottom():
    radius = R + 50
    for angle in range(-90, 91):
        rad = math.radians(angle)
        x1 = center_x + radius * math.sin(rad)
        y1 = center_y + radius * math.cos(rad)
        inner_radius = radius - (10 if angle % 10 == 0 else 5)
        x2 = center_x + inner_radius * math.sin(rad)
        y2 = center_y + inner_radius * math.cos(rad)
        pygame.draw.line(screen, BLACK, (x1, y1), (x2, y2), 1)
        if angle % 10 == 0:
            tx = center_x + (radius + 15) * math.sin(rad)
            ty = center_y + (radius + 15) * math.cos(rad)
            label = font.render(f"{abs(angle)}", True, BLACK)
            screen.blit(label, label.get_rect(center=(tx, ty)))

laser_angle_deg = 0
laser_body_size = (30, 60)
afterimages = []

def update_laser_position(angle_deg):
    global laser_body_rect
    x = center_x - laser_radius * math.sin(math.radians(angle_deg))
    y = center_y - laser_radius * math.cos(math.radians(angle_deg))
    laser_body_rect.center = (x, y)

laser_body_rect = pygame.Rect(0, 0, *laser_body_size)
update_laser_position(laser_angle_deg)

dragging = False
running = True

while running:
    time_delta = clock.tick(60) / 1000.0
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and laser_body_rect.collidepoint(event.pos):
            dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False
        elif event.type == pygame.MOUSEMOTION and dragging:
            dx, dy = event.pos[0] - center_x, event.pos[1] - center_y
            angle_from_up = math.degrees(math.atan2(-dx, -dy))
            angle_from_up = max(-90, min(90, angle_from_up))
            laser_angle_deg = angle_from_up
            angle_input.set_text(f"{laser_angle_deg:.1f}")
            update_laser_position(laser_angle_deg)
        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == angle_input:
                try:
                    laser_angle_deg = max(-90, min(90, float(event.text)))
                    update_laser_position(laser_angle_deg)
                except ValueError:
                    pass
            elif event.ui_element == concentration_input:
                try:
                    molar_concentration = max(0.0, min(4.5, float(event.text)))
                    concentration_slider.set_current_value(molar_concentration)
                except ValueError:
                    pass
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == afterimage_button and refraction_angle is not None:
                afterimages.append({
                    'incidence': (laser_tip, (center_x, center_y)),
                    'refraction': ((center_x, center_y),
                                   (center_x + 300 * math.sin(math.radians(refraction_angle)),
                                    center_y + 300 * math.cos(math.radians(refraction_angle))))
                })
            elif event.ui_element == clear_afterimage_button:
                afterimages.clear()

        manager.process_events(event)

    molar_concentration = concentration_slider.get_current_value()
    concentration_input.set_text(f"{molar_concentration:.2f}")
    n2 = interpolate_n(molar_concentration)

    pygame.draw.circle(screen, BLACK, (center_x, center_y), R, 2)
    pygame.draw.polygon(screen, SKY_BLUE, [
        (center_x + R * math.cos(math.radians(a)), center_y + R * math.sin(math.radians(a)))
        for a in range(0, 181, 2)
    ] + [(center_x - R, center_y), (center_x + R, center_y)])

    draw_protractor_top()
    draw_protractor_bottom()

    pygame.draw.line(screen, NAVY, (center_x - R, center_y), (center_x + R, center_y), 2)

    laser_surface = pygame.Surface(laser_body_size, pygame.SRCALPHA)
    laser_surface.fill(BLACK)
    rotated_laser = pygame.transform.rotate(laser_surface, laser_angle_deg)
    laser_rect = rotated_laser.get_rect(center=laser_body_rect.center)
    screen.blit(rotated_laser, laser_rect.topleft)

    laser_tip = (
        laser_body_rect.centerx + 30 * -math.sin(math.radians(laser_angle_deg)),
        laser_body_rect.centery + 30 * -math.cos(math.radians(laser_angle_deg))
    )

    refraction_angle = get_refracted_angle_signed(laser_angle_deg, n1, n2)

    # 잔상 먼저 그리기
    for path in afterimages:
        pygame.draw.line(screen, PURPLE_FADE, *path['incidence'], 2)
        pygame.draw.line(screen, PURPLE_FADE, *path['refraction'], 2)

    pygame.draw.line(screen, RED, laser_tip, (center_x, center_y), 2)
    if refraction_angle is not None:
        end_x = center_x + 300 * math.sin(math.radians(refraction_angle))
        end_y = center_y + 300 * math.cos(math.radians(refraction_angle))
        pygame.draw.line(screen, GREEN, (center_x, center_y), (end_x, end_y), 2)
    else:
        draw_text("전반사 발생", (50, 200))

    draw_text(f"입사각: {laser_angle_deg:.1f}°", (150, 90))
    if refraction_angle is not None:
        draw_text(f"굴절각: {refraction_angle:.2f}°", (50, 130))
    draw_text(f"굴절률: {n2:.4f}", (50, 160))
    draw_text(f"몰농도:", (450, 50))

    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.flip()

pygame.quit()
