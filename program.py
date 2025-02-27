import cv2
import mediapipe as mp

from models.models import Hand

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)
with (mp_hands.Hands(max_num_hands=1, model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
      as hands):
    while cap.isOpened():
        success, image = cap.read()
        image = cv2.flip(image, 1)

        if not success:
            print("Ignoring empty camera frame.")
            continue

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        image_height, image_width, _ = image.shape
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                hand = Hand(hand_landmarks)

                print(hand.get_state())

                # print(hand_landmarks)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

        # Display the image to the user.
        cv2.imshow('MediaPipe Hands', image)

        if cv2.waitKey(100) & 0xFF == 27:
            break
cap.release()
