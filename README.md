# Gesture Controlled Media Playback

Control videos with your hand through your webcam. It uses MediaPipe to track
your hand and sends keyboard presses to whatever video you have open (YouTube,
VLC, Netflix, anything that uses the arrow keys and space bar).

| Gesture | What it does | Key sent |
|---|---|---|
| Swipe your open hand right | fast forward | Right arrow |
| Swipe your open hand left | rewind | Left arrow |
| Make a fist | play / pause | Space |

## Setup

```
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

`mediapipe` is pinned to 0.10.14 because newer versions are moving away from
the `mp.solutions` API this uses. Upgrading pip first matters on Mac, otherwise
one of pyautogui's dependencies fails to build.

## Running it

```
python gesture_control.py
```

1. A camera window opens showing your hand with the tracking drawn on it
2. **Click on your video** so it's the focused window, otherwise the key presses
   go to the camera window instead
3. Swipe or make a fist. The action shows up on the camera window for a second

Quit with ctrl+c in the terminal (or q in the camera window).

**Mac:** the first time, macOS will ask for camera access for your terminal,
and you need to allow it under System Settings > Privacy & Security >
Accessibility too, or the key presses won't do anything.

## How it works

- `gesture_control.py` reads webcam frames with OpenCV, mirrors them, and runs
  MediaPipe's hand model on each one to get 21 points on the hand
- `gestures.py` has a `GestureDetector` class that gets the hand each frame and
  decides if something happened:
  - **Fist:** each finger counts as curled if its tip is below its middle
    knuckle (y goes down in images). Play/pause only fires when the fist first
    closes, so holding it doesn't keep toggling
  - MediaPipe loses track of a fist a lot more than an open hand, so the fist
    has to show up 3 frames in a row to count, and the hand has to be open or
    gone for 8 frames before another fist can count. Without this, holding a
    fist toggled play/pause over and over
  - **Swipe:** keeps the last few wrist positions in a `deque` and checks if the
    hand moved more than 15% of the frame width across them. There's a cooldown
    after each swipe
  - If the hand leaves the frame the history is cleared, so it doesn't count as
    a swipe when it comes back somewhere else

## Tests

The detector doesn't need a camera, so the tests just feed it fake hands:

```
pytest
```

## Things I noticed / might add

- Swiping back to the middle after a swipe can count as a swipe the other way
  if you're slow about it
- Could use MediaPipe's newer Tasks API instead of the old `solutions` one
- Volume control with a thumbs up/down would be a good next gesture
