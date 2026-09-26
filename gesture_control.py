import time

import cv2
import mediapipe as mp
import pyautogui

from gestures import GestureDetector

LABELS = {"left": "<< rewind", "right": "fast forward >>", "space": "play / pause"}


def check_mac_permission():
    # on mac, key presses from pyautogui get silently thrown away unless the
    # app running this (Terminal, VS Code, etc) has Accessibility permission
    try:
        import Quartz
    except ImportError:
        return    # not a mac
    if not Quartz.CGPreflightPostEventAccess():
        print("WARNING: no Accessibility permission, key presses won't reach the video.")
        print("Turn on your terminal app in System Settings > Privacy & Security >")
        print("Accessibility, then quit and reopen it and run this again.")


def main():
    check_mac_permission()

    mp_hands = mp.solutions.hands
    drawer = mp.solutions.drawing_utils
    # only track one hand, two hands made the position jump around
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7,
                           min_tracking_confidence=0.7)
    detector = GestureDetector()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("couldn't open the webcam")
        return

    print("click on your video so it's the focused window before using gestures")
    print("ctrl+c here or q in the camera window to quit")

    label = ""
    label_time = 0

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            # mirror it so moving your hand right looks like moving right
            frame = cv2.flip(frame, 1)
            result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            hand = None
            if result.multi_hand_landmarks:
                hand = result.multi_hand_landmarks[0]
                drawer.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

            now = time.time()
            action = detector.update(hand, now)
            if action:
                pyautogui.press(action)   # action names are also the key names
                print(LABELS[action])
                label = LABELS[action]
                label_time = now

            # show the last action on screen for a second
            if now - label_time < 1:
                cv2.putText(frame, label, (20, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            1.2, (0, 255, 0), 3)

            cv2.imshow("Gesture Control", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        hands.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
