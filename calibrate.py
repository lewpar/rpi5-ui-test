#!/usr/bin/env python3
import pygame
import sys
import time

# -----------------------------
# Config
# -----------------------------
HOLD_SECONDS = 3
SAMPLE_RATE = 0.02  # seconds between samples

# -----------------------------
# Helpers
# -----------------------------
def draw_screen(screen, text, pos, font, color=(255, 255, 255)):
    screen.fill((0, 0, 0))
    label = font.render(text, True, color)
    rect = label.get_rect(center=pos)
    screen.blit(label, rect)
    pygame.display.flip()

def collect_touch(screen, prompt, width, height, font):
    """
    Collect averaged touch position while finger is held down.
    Works with SDL touch + mouse fallback.
    """

    print(f"\n==> {prompt}")

    screen.fill((0, 0, 0))
    label = font.render(prompt, True, (255, 255, 255))
    rect = label.get_rect(center=(width // 2, height // 2))
    screen.blit(label, rect)
    pygame.display.flip()

    touching = False
    start_time = None

    sum_x = 0
    sum_y = 0
    count = 0

    last_sample = 0

    running = True
    while running:
        now = time.time()

        for event in pygame.event.get():
            # Touch events (SDL2)
            if event.type == pygame.FINGERDOWN:
                touching = True
                start_time = time.time()

            elif event.type == pygame.FINGERUP:
                touching = False
                running = False

            elif event.type == pygame.FINGERMOTION:
                touching = True

            # Mouse fallback (useful for desktop testing)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                touching = True
                start_time = time.time()

            elif event.type == pygame.MOUSEBUTTONUP:
                touching = False
                running = False

        if touching and (now - last_sample) >= SAMPLE_RATE:
            last_sample = now

            x, y = pygame.mouse.get_pos()

            sum_x += x
            sum_y += y
            count += 1

        # Stop automatically after hold time
        if start_time and (now - start_time) >= HOLD_SECONDS:
            running = False

    if count == 0:
        print("No touch detected")
        sys.exit(1)

    avg_x = sum_x // count
    avg_y = sum_y // count

    print(f"    x: {avg_x}")
    print(f"    y: {avg_y}")

    return avg_x, avg_y


# -----------------------------
# Main
# -----------------------------
def main():
    pygame.init()

    info = pygame.display.Info()
    width, height = info.current_w, info.current_h

    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
    pygame.display.set_caption("Touch Calibration")

    font = pygame.font.SysFont(None, 48)

    print("Touchscreen calibration starting...")

    # -----------------------------
    # Top-left
    # -----------------------------
    draw_screen(screen, "Touch TOP LEFT corner", (width * 0.2, height * 0.2), font)
    time.sleep(1)
    tl_x, tl_y = collect_touch(screen, "Touch TOP LEFT and hold", width, height, font)

    time.sleep(1)

    # -----------------------------
    # Bottom-right
    # -----------------------------
    draw_screen(screen, "Touch BOTTOM RIGHT corner", (width * 0.8, height * 0.8), font)
    time.sleep(1)
    br_x, br_y = collect_touch(screen, "Touch BOTTOM RIGHT and hold", width, height, font)

    # -----------------------------
    # Results
    # -----------------------------
    screen.fill((0, 0, 0))
    pygame.display.flip()

    print("\n==============================")
    print(" Calibration Results")
    print("==============================\n")

    device = "/dev/input/eventX (SDL touch - replace if needed)"

    print("Kivy config line:")
    print(
        f"hidinput,{device},invert_y=0,"
        f"min_abs_x={tl_x},max_abs_x={br_x},"
        f"min_abs_y={tl_y},max_abs_y={br_y}"
    )

    print("\nIndividual values:")
    print(f"min_abs_x = {tl_x}")
    print(f"max_abs_x = {br_x}")
    print(f"min_abs_y = {tl_y}")
    print(f"max_abs_y = {br_y}")

    print("\nPress any key to exit...")

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                waiting = False

    pygame.quit()


if __name__ == "__main__":
    main()