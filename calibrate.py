import pygame
import numpy as np
from evdev import InputDevice, list_devices, ecodes

# -----------------------------
# DEVICE SELECTION
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
# TARGETS
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
# TOUCH SAMPLING (FIXED + STABLE)
# -----------------------------

def read_stable_touch(samples=6):
    points = []

    x = None
    y = None

    while len(points) < samples:
        event = dev.read_one()
        if event is None:
            continue

        if event.type == ecodes.EV_ABS:
            if event.code in (ecodes.ABS_X, ecodes.ABS_MT_POSITION_X):
                x = event.value

            elif event.code in (ecodes.ABS_Y, ecodes.ABS_MT_POSITION_Y):
                y = event.value

        elif event.type == ecodes.SYN_REPORT:
            if x is not None and y is not None:
                points.append((x, y))

            x = None
            y = None

    if len(points) == 0:
        return None

    arr = np.array(points)
    return (int(np.median(arr[:, 0])), int(np.median(arr[:, 1])))


# -----------------------------
# AFFINE SOLVER (SAFE)
# -----------------------------

def solve_affine(raw, screen_pts):
    A = []
    B = []

    for (rx, ry), (sx, sy) in zip(raw, screen_pts):
        A.append([rx, ry, 1, 0, 0, 0])
        A.append([0, 0, 0, rx, ry, 1])
        B.append(sx)
        B.append(sy)

    A = np.array(A, dtype=float)
    B = np.array(B, dtype=float)

    X, *_ = np.linalg.lstsq(A, B, rcond=None)

    # sanity check (prevents shear explosions)
    if np.any(np.abs(X) > 10):
        print("⚠️ WARNING: unstable calibration detected")
        print(X)

    return X


def to_xinput_matrix(m):
    a, b, c, d, e, f = m

    return [
        a, c, e / W,
        b, d, f / H,
        0, 0, 1
    ]

# -----------------------------
# STATE
# -----------------------------

running = True
done = False

# -----------------------------
# MAIN LOOP
# -----------------------------

while running:
    screen.fill((25, 25, 25))

    # draw targets
    for i, (x, y) in enumerate(targets):
        color = (0, 255, 0) if i == index else (120, 120, 120)
        pygame.draw.circle(screen, color, (x, y), 18)

    if not done:
        msg = font.render(f"Tap target {index+1}/4", True, (255, 255, 255))
    else:
        msg = font.render("Calibration complete", True, (0, 255, 0))

    screen.blit(msg, (20, 20))
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # -----------------------------
    # TOUCH CAPTURE
    # -----------------------------

    if not done and index < len(targets):
        touch = read_stable_touch(samples=6)

        if touch:
            rx, ry = touch
            print("Captured stable:", rx, ry)

            raw_points.append((rx, ry))
            index += 1

            if index >= len(targets):
                done = True
                running = False

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