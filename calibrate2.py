#!/usr/bin/env python3
import pygame
import time
import sys

HOLD_SECONDS = 3
SAMPLE_RATE = 0.02

def collect_touch(screen, prompt, width, height, font):
    screen.fill((0, 0, 0))
    label = font.render(prompt, True, (255, 255, 255))
    rect = label.get_rect(center=(width // 2, height // 2))
    screen.blit(label, rect)
    pygame.display.flip()

    touching = False
    start_time = None

    sx = sy = 0
    count = 0
    last = 0

    while True:
        now = time.time()

        for event in pygame.event.get():
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                touching = True
                start_time = time.time()

            if event.type in (pygame.MOUSEBUTTONUP, pygame.FINGERUP):
                touching = False
                return sx // count, sy // count

        if touching and now - last > SAMPLE_RATE:
            last = now
            x, y = pygame.mouse.get_pos()
            sx += x
            sy += y
            count += 1

        if start_time and now - start_time > HOLD_SECONDS:
            return sx // count, sy // count


def main():
    pygame.init()
    width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
    font = pygame.font.SysFont(None, 48)

    print("Touch TOP LEFT")
    tl_x, tl_y = collect_touch(screen, "Touch TOP LEFT", width, height, font)

    time.sleep(1)

    print("Touch BOTTOM RIGHT")
    br_x, br_y = collect_touch(screen, "Touch BOTTOM RIGHT", width, height, font)

    # -----------------------------
    # CALIBRATION MATH
    # -----------------------------
    raw_range_x = br_x - tl_x
    raw_range_y = br_y - tl_y

    screen_w, screen_h = width, height

    scale_x = 4096 / raw_range_x
    scale_y = 4096 / raw_range_y

    print("\n==============================")
    print(" CALIBRATION RESULT")
    print("==============================\n")

    print("Raw points:")
    print(f"TL = ({tl_x}, {tl_y})")
    print(f"BR = ({br_x}, {br_y})\n")

    print("Offsets:")
    print(f"X offset (min) = {tl_x}")
    print(f"Y offset (min) = {tl_y}\n")

    print("Ranges:")
    print(f"X range = {raw_range_x}")
    print(f"Y range = {raw_range_y}\n")

    print("Scale (raw → 0–4096 normalized):")
    print(f"X scale = {scale_x}")
    print(f"Y scale = {scale_y}\n")

    print("Final mapping formula:")
    print("screen_x = (raw_x - Xoffset) * (screen_width / raw_range_x)")
    print("screen_y = (raw_y - Yoffset) * (screen_height / raw_range_y)\n")

    print("Kivy-style config equivalent:")
    print(
        f"hidinput,/dev/input/eventX,"
        f"min_abs_x={tl_x},max_abs_x={br_x},"
        f"min_abs_y={tl_y},max_abs_y={br_y}"
    )

    pygame.quit()


if __name__ == "__main__":
    main()