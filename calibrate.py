import pygame
import numpy as np
from evdev import InputDevice, list_devices, ecodes

# -----------------------------
# DEVICE SELECTION MENU (TERMINAL)
# -----------------------------

devices = [InputDevice(p) for p in list_devices()]

print("\nAvailable input devices:\n")
for i, d in enumerate(devices):
    print(f"[{i}] {d.path} | {d.name}")

idx = int(input("\nSelect touch device index: "))
dev = devices[idx]

print("\nUsing:", dev.path, dev.name)

# -----------------------------
# PYGAME INIT
# -----------------------------

pygame.init()

W, H = 800, 480
screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

# -----------------------------
# CALIBRATION TARGETS
# -----------------------------

targets = [
    (80, 80),
    (720, 80),
    (80, 400),
    (720, 400)
]

raw_points = []
index = 0

# -----------------------------
# TOUCH INPUT (ROBUST read_one)
# -----------------------------

def read_touch():
    x = None
    y = None

    while True:
        event = dev.read_one()
        if event is None:
            break

        if event.type == ecodes.EV_ABS:
            if event.code == ecodes.ABS_X:
                x = event.value
            elif event.code == ecodes.ABS_Y:
                y = event.value

    if x is not None and y is not None:
        return x, y

    return None

# -----------------------------
# AFFINE SOLVER
# -----------------------------

def solve_affine(raw, screen_pts):
    A = []
    B = []

    for (rx, ry), (sx, sy) in zip(raw, screen_pts):
        A.append([rx, ry, 1, 0, 0, 0])
        A.append([0, 0, 0, rx, ry, 1])
        B.append(sx)
        B.append(sy)

    A = np.array(A)
    B = np.array(B)

    X, *_ = np.linalg.lstsq(A, B, rcond=None)
    return X  # a b c d e f


def to_xinput_matrix(m):
    a, b, c, d, e, f = m

    return [
        a, c, e / W,
        b, d, f / H,
        0, 0, 1
    ]

# -----------------------------
# DEBOUNCE
# -----------------------------

last_tap = 0
DEBOUNCE_MS = 400

# -----------------------------
# MAIN LOOP
# -----------------------------

running = True

while running:
    screen.fill((25, 25, 25))

    # draw targets
    for i, (x, y) in enumerate(targets):
        color = (0, 255, 0) if i == index else (120, 120, 120)
        pygame.draw.circle(screen, color, (x, y), 18)

    msg = font.render(f"Tap target {index+1}/4", True, (255, 255, 255))
    screen.blit(msg, (20, 20))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # -----------------------------
    # TOUCH READ
    # -----------------------------

    touch = read_touch()
    now = pygame.time.get_ticks()

    if touch and index < len(targets):
        if now - last_tap > DEBOUNCE_MS:
            rx, ry = touch
            print("Captured:", rx, ry)

            raw_points.append((rx, ry))
            index += 1
            last_tap = now

    clock.tick(60)

pygame.quit()

# -----------------------------
# SOLVE RESULT
# -----------------------------

if len(raw_points) == 4:
    m = solve_affine(raw_points, targets)
    xinput = to_xinput_matrix(m)

    print("\n=== CALIBRATION COMPLETE ===")
    print("Affine:", m)

    print("\nXInput matrix:")
    print(" ".join(map(str, xinput)))

    print("\nApply with:")
    print(
        "xinput set-prop <device-id> "
        "'Coordinate Transformation Matrix' " +
        " ".join(map(str, xinput))
    )