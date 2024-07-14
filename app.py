import threading
from math import hypot

import cv2
import mediapipe as mp
import numpy as np
import screen_brightness_control as sbc
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

mpHands = mp.solutions.hands
hands = mpHands.Hands(
    static_image_mode=False,
    model_complexity=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75,
    max_num_hands=2
)

cap = cv2.VideoCapture(0)
brightness_adjusting = False
brightness_thread = None
lock = threading.Lock()

def adjust_brightness():
    global brightness_adjusting
    print("Brightness adjustment thread started.")
    while True:
        with lock:
            if not brightness_adjusting:
                print("Brightness adjustment stopped.")
                break

        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frameRGB)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                for id, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)

                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mpHands.HAND_CONNECTIONS)

            thumb_x, thumb_y = int(hand_landmarks.landmark[4].x * w), int(hand_landmarks.landmark[4].y * h)
            index_x, index_y = int(hand_landmarks.landmark[8].x * w), int(hand_landmarks.landmark[8].y * h)

            cv2.circle(frame, (thumb_x, thumb_y), 10, (0, 255, 0), cv2.FILLED)
            cv2.circle(frame, (index_x, index_y), 10, (0, 255, 0), cv2.FILLED)

            length = hypot(index_x - thumb_x, index_y - thumb_y)
            brightness_level = np.interp(length, [15, 220], [0, 100])
            sbc.set_brightness(int(brightness_level))

        cv2.imshow('Hand Brightness Control', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    print("Exiting brightness adjustment thread.")

@app.route('/adjust-brightness', methods=['GET'])
def start_brightness_adjustment():
    global brightness_adjusting, brightness_thread
    with lock:
        if not brightness_adjusting:
            brightness_adjusting = True
            brightness_thread = threading.Thread(target=adjust_brightness)
            brightness_thread.start()
    print("Brightness adjustment started.")
    return jsonify({'status': 'Brightness adjustment started'})

@app.route('/stop-brightness', methods=['GET'])
def stop_brightness_adjustment():
    global brightness_adjusting, brightness_thread
    with lock:
        brightness_adjusting = False
    if brightness_thread is not None:
        brightness_thread.join()
        brightness_thread = None
    cap.release()
    cv2.destroyAllWindows()
    print("Brightness adjustment stopped.")
    return jsonify({'status': 'Brightness adjustment stopped'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
