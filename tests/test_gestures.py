import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from gestures import GestureDetector, is_fist


# fake mediapipe hand: 21 points, only the ones the code looks at matter
def make_hand(fist=False, wrist_x=0.5):
    pts = [SimpleNamespace(x=wrist_x, y=0.5) for _ in range(21)]
    pts[0].y = 0.8                        # wrist at the bottom
    for pip in [6, 10, 14, 18]:
        pts[pip].y = 0.4
    for tip in [8, 12, 16, 20]:
        pts[tip].y = 0.45 if fist else 0.2
    return SimpleNamespace(landmark=pts)


def test_is_fist():
    assert is_fist(make_hand(fist=True))
    assert not is_fist(make_hand(fist=False))


def run(d, frames, start=2.0, fps=30):
    # feed a list of hands to the detector like a camera would
    return [d.update(h, start + i / fps) for i, h in enumerate(frames)]


def test_holding_fist_only_toggles_once():
    d = GestureDetector()
    actions = run(d, [make_hand(fist=True)] * 150)   # 5 seconds
    assert actions.count("space") == 1


def test_flickering_fist_only_toggles_once():
    # tracking drops out or misreads the fist for a frame every so often
    d = GestureDetector()
    frames = []
    for i in range(150):
        if i % 10 == 5:
            frames.append(None)
        elif i % 10 == 8:
            frames.append(make_hand(fist=False))
        else:
            frames.append(make_hand(fist=True))
    assert run(d, frames).count("space") == 1


def test_one_bad_frame_isnt_a_fist():
    d = GestureDetector()
    frames = [make_hand()] * 10 + [make_hand(fist=True)] + [make_hand()] * 10
    assert "space" not in run(d, frames)


def test_fist_again_toggles_again():
    d = GestureDetector()
    frames = ([make_hand(fist=True)] * 10 + [make_hand()] * 60
              + [make_hand(fist=True)] * 10)
    assert run(d, frames).count("space") == 2


def test_swipe_right_and_left():
    d = GestureDetector()
    d.update(make_hand(wrist_x=0.3), 1.0)
    assert d.update(make_hand(wrist_x=0.6), 1.1) == "right"

    d.update(make_hand(wrist_x=0.6), 2.0)
    assert d.update(make_hand(wrist_x=0.3), 2.1) == "left"


def test_small_movement_ignored():
    d = GestureDetector()
    actions = [d.update(make_hand(wrist_x=0.5 + (i % 2) * 0.02), 1 + i * 0.1)
               for i in range(20)]
    assert all(a is None for a in actions)


def test_hand_reappearing_somewhere_else_isnt_a_swipe():
    d = GestureDetector()
    d.update(make_hand(wrist_x=0.2), 1.0)
    d.update(None, 1.1)
    assert d.update(make_hand(wrist_x=0.8), 1.2) is None
