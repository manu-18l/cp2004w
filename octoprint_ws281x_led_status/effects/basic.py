from __future__ import absolute_import, unicode_literals, division

import time
import random
import math

from octoprint_ws281x_led_status.util import milli_sleep, wheel

DIRECTIONS = ['forward', 'backward']  # Used for effects that go 'out and back' kind of thing


def solid_color(strip, queue, color, delay=None, max_brightness=255, set_brightness=True, wait=True):
    # Set pixels to a solid color
    if set_brightness:
        strip.setBrightness(max_brightness)
    for p in range(strip.numPixels()):
        strip.setPixelColorRGB(p, *color)
    strip.show()
    if wait:
        time.sleep(0.1)


def color_wipe(strip, queue, color, delay, max_brightness=255):
    strip.setBrightness(max_brightness)
    for i in range(strip.numPixels()):
        strip.setPixelColorRGB(i, *color)
        strip.show()
        if not queue.empty():
            return
        milli_sleep(delay)
    for i in range(strip.numPixels()):
        strip.setPixelColorRGB(i, 0, 0, 0)
        strip.show()
        if not queue.empty():
            return
        milli_sleep(delay)


def color_wipe_2(strip, queue, color, delay, max_brightness=255):
    strip.setBrightness(max_brightness)
    for direction in DIRECTIONS:
        for i in range(strip.numPixels()) if direction == 'forward' else reversed(range(strip.numPixels())):
            if direction == 'backward':
                color = (0, 0, 0)
            strip.setPixelColorRGB(i, *color)
            strip.show()
            if not queue.empty():
                return
            milli_sleep(delay)


def simple_pulse(strip, queue, color, delay, max_brightness=255):
    strip.setBrightness(1)
    solid_color(strip, queue, color, delay, max_brightness, set_brightness=False, wait=False)
    for direction in DIRECTIONS:
        for b in range(max_brightness) if direction == 'forward' else reversed(range(max_brightness)):
            strip.setBrightness(b)
            strip.show()
            if not queue.empty():
                return
            milli_sleep(delay)


def rainbow(strip, queue, color, delay, max_brightness=255):
    strip.setBrightness(max_brightness)
    for i in range(256):
        solid_color(strip, queue, wheel(i), delay, max_brightness, set_brightness=False, wait=False)
        if not queue.empty():
            return
        milli_sleep(delay)


def rainbow_cycle(strip, queue, color, delay, max_brightness=255):
    strip.setBrightness(max_brightness)
    for j in range(256):
        for i in range(strip.numPixels()):
            strip.setPixelColorRGB(i, *wheel(
                (int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        if not queue.empty():
            return
        milli_sleep(delay)


def solo_bounce(strip, queue, color, delay, max_brightness=255):
    strip.setBrightness(max_brightness)
    for direction in DIRECTIONS:
        for i in range(strip.numPixels()) if direction == 'forward' else reversed(range(strip.numPixels())):
            strip.setPixelColorRGB(i, *color)
            for blank in range(strip.numPixels()):
                if blank != i:
                    strip.setPixelColorRGB(blank, 0, 0, 0)
            strip.show()
            if not queue.empty():
                return
            milli_sleep(delay)


def bounce(strip, queue, color, delay, max_brightness=255):
    red, green, blue = color
    size = 3
    for direction in DIRECTIONS:
        for i in range(0, (strip.numPixels() - size - 2)) if direction == 'forward' else range((strip.numPixels() - size - 2), 0, -1):
            solid_color(strip, queue, (0, 0, 0), max_brightness=max_brightness, wait=False)
            strip.setPixelColorRGB(i, *(int(math.floor(red / 10)), int(math.floor(green / 10)), int(math.floor(blue / 10))))
            for j in range(1, (size + 1)):
                strip.setPixelColorRGB(i + j, *(red, green, blue))
            strip.setPixelColorRGB(i + size + 1, *(int(math.floor(red / 10)), int(math.floor(green / 10)), int(math.floor(blue / 10))))
            if not queue.empty():
                return
            strip.show()
            milli_sleep(delay)


def random_single(strip, queue, color, delay, max_brightness=255):
    strip.setBrightness(max_brightness)
    for p in range(strip.numPixels()):
        strip.setPixelColorRGB(p, *wheel(random.randint(0, 255)))
    strip.show()
    while True:
        strip.setPixelColorRGB(random.randint(0, strip.numPixels()), *wheel(random.randint(0, 255)))
        strip.show()
        if not queue.empty():
            return
        milli_sleep(delay)


def blink(strip, queue, color, delay, max_brightness=255):
    solid_color(strip, queue, color, delay, max_brightness, wait=False)
    for direction in DIRECTIONS:
        strip.setBrightness(max_brightness if direction == 'forward' else 0)
        strip.show()
        for ms in range(int(delay / 2)):  # We do it this way so we can check the q more often
            if not queue.empty():         # Otherwise the effect may end up blocking the server, when settings
                return                    # Are saved, or it shuts down.
            milli_sleep(2)


def crossover(strip, queue, color, delay, max_brightness=255):
    strip.setBrightness(max_brightness)
    solid_color(strip, queue, (0, 0, 0), wait=False)
    num_pixels = strip.numPixels()
    if num_pixels % 2 != 1:
        num_pixels -= 1

    for i in range(num_pixels):
        for p in range(num_pixels):
            strip.setPixelColorRGB(p, 0, 0, 0)
        strip.setPixelColorRGB(i, *color)
        strip.setPixelColorRGB(num_pixels - 1 - i, *color)
        strip.show()
        if not queue.empty():
            return
        milli_sleep(delay)


# Credit to https://www.tweaking4all.com/hardware/arduino/adruino-led-strip-effects/#LEDStripEffectBouncingBalls
# Translated from c++ to Python by me
def bouncy_balls(strip, queue, color, delay, max_brightness=255):
    ball_count = 2
    gravity = -9.81
    start_height = 1

    height = []
    impact_velocity_start = math.sqrt(- 2 * gravity * start_height)
    impact_velocity = []
    time_since_last_bounce = []
    position = []
    clock_time_since_last_bounce = []
    dampening = []

    for i in range(ball_count):
        clock_time_since_last_bounce.append(time.time() * 1000)
        time_since_last_bounce.append(0)
        height.append(start_height)
        position.append(0)
        impact_velocity.append(impact_velocity_start)
        dampening.append(0.9 - (i / math.pow(ball_count, 2)))

    while True:
        for i in range(ball_count):
            time_since_last_bounce[i] = time.time() * 1000 - clock_time_since_last_bounce[i]
            height[i] = 0.5 * gravity * math.pow(time_since_last_bounce[i] / 1000, 2) + impact_velocity[i] * time_since_last_bounce[i] / 1000

            if height[i] < 0:
                height[i] = 0
                impact_velocity[i] = dampening[i] * impact_velocity[i]
                clock_time_since_last_bounce[i] = time.time() * 1000

                if impact_velocity[i] < 0.01:
                    impact_velocity[i] = impact_velocity_start

            position[i] = round(height[i] * (strip.numPixels() - 1) / start_height)

        for p in range(strip.numPixels()):
            # Set to blank
            strip.setPixelColorRGB(p, 0, 0, 0)

        for i in range(ball_count):
            # Light pixels that should be lit
            strip.setPixelColorRGB(position[i], *color)

        strip.show()
        if not queue.empty():
            return
        milli_sleep(delay)
