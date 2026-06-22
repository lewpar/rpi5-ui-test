import pygame
import numpy as np
from evdev import InputDevice, ecodes, list_devices

# -----------------------------
# FIND TOUCH DEVICE
# -----------------------------

def find_touch():
    for path in list_devices():
        dev = InputDevice(path)
        caps = dev.capabilities()

        if ecodes.EV_ABS in caps:
            abs_caps = caps[ecodes.EV_ABS]

            if ecodes.ABS_X in abs_caps and ecodes.ABS_Y in abs_caps:
                print("Using:", dev.path, dev.name)
                return dev

    return None


dev = find_touch()
if not dev:
    raise RuntimeError("No touchscreen device found")

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
    (80, 80),      # top-left
    (720, 80),     # top-right
    (80, 400),     # bottom-left
    (720, 400)     # bottom-right
]

raw_points = []
index = 0

# -----------------------------
# READ TOUCH (FIXED: read_one ONLY)
# -----------------------------

def read_touch():
    x = None
    y = None

    # drain available events
    while True:
        event = dev.read_one()   # ✅ safest API
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
DEBOUNCE = 400  # ms

# -----------------------------
# MAIN LOOP
# -----------------------------

running = True

while running:
    screen.fill((20, 20, 20))

    # draw targets
    for i, (x, y) in enumerate(targets):
        color = (0, 255, 0) if i == index else (120, 120, 120)
        pygame.draw.circle(screen, color, (x, y), 18)

    txt = font.render(f"Tap target {index+1}/4", True, (255, 255, 255))
    screen.blit(txt, (20, 20))

    pygame.display.flip()

    # pygame events (exit support)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # -----------------------------
    # TOUCH INPUT
    # -----------------------------

    touch = read_touch()
    now = pygame.time.get_ticks()

    if touch and index < len(targets):
        if now - last_tap > DEBOUNCE:
            rx, ry = touch
            print("Captured:", rx, ry)

            raw_points.append((rx, ry))
            index += 1
            last_tap = now

    clock.tick(60)

pygame.quit()

# -----------------------------
# SOLVE + OUTPUT
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