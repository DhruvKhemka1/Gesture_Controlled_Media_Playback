from collections import deque

# mediapipe gives 21 points per hand, these are the ones used here
WRIST = 0
FINGER_TIPS = [8, 12, 16, 20]   # index, middle, ring, pinky
FINGER_PIPS = [6, 10, 14, 18]   # middle knuckle of each of those fingers


def is_fist(hand):
    # y goes DOWN in image coordinates, so a curled finger has its tip
    # lower on the screen (bigger y) than its middle knuckle.
    # skipping the thumb since it bends sideways and is hard to read
    pts = hand.landmark
    return all(pts[tip].y > pts[pip].y for tip, pip in zip(FINGER_TIPS, FINGER_PIPS))


class GestureDetector:
    # all the gesture logic lives here instead of in the camera loop,
    # so it can be tested with fake hands and no webcam

    def __init__(self, swipe_distance=0.15, window=6, swipe_cooldown=0.6,
                 fist_cooldown=1.5, fist_frames_needed=3, release_frames_needed=8):
        self.swipe_distance = swipe_distance    # fraction of the frame width
        self.swipe_cooldown = swipe_cooldown    # seconds
        self.fist_cooldown = fist_cooldown      # seconds
        self.xs = deque(maxlen=window)          # recent wrist x positions
        self.last_swipe = 0
        self.last_fist = 0

        # tracking flickers a lot on a fist, so it has to be seen a few frames
        # in a row to count, and the hand has to be open (or gone) for a few
        # frames before another fist can count
        self.fist_frames_needed = fist_frames_needed
        self.release_frames_needed = release_frames_needed
        self.fist_count = 0
        self.open_count = 0
        self.fist_down = False

    def update(self, hand, now):
        # call once per frame. returns "left", "right", "space" or None
        fist = hand is not None and is_fist(hand)
        if fist:
            self.fist_count += 1
            self.open_count = 0
        else:
            self.open_count += 1
            self.fist_count = 0
            if self.open_count >= self.release_frames_needed:
                self.fist_down = False

        if hand is None:
            # hand left the frame, forget where it was so it doesn't
            # count as a swipe when it comes back somewhere else
            self.xs.clear()
            return None

        if fist or self.fist_down:
            self.xs.clear()
            if self.fist_count == self.fist_frames_needed and not self.fist_down:
                self.fist_down = True
                if now - self.last_fist > self.fist_cooldown:
                    self.last_fist = now
                    return "space"
            return None

        self.xs.append(hand.landmark[WRIST].x)
        if len(self.xs) < 2 or now - self.last_swipe < self.swipe_cooldown:
            return None

        dx = self.xs[-1] - self.xs[0]
        if abs(dx) > self.swipe_distance:
            self.last_swipe = now
            self.xs.clear()
            return "right" if dx > 0 else "left"
        return None
