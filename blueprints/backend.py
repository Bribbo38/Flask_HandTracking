import base64

import cv2
import numpy as np
from flask import Blueprint, request, jsonify
import mediapipe as mp

from models.models import Hand

app = Blueprint('backend', __name__)

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


# For webcam input:
@app.route('/render', methods=['POST'])
def render():
    try:
        data = request.json

        send_image_response = data.get('send_image_response', False)

        # Decodifica l'immagine base64
        image_data = base64.b64decode(data['image'].split(',')[1])
        np_array = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        # Inverti l'immagine (effetto specchio)
        # image = cv2.flip(image, 1)

        # Elaborazione con MediaPipe
        with (mp_hands.Hands(
                max_num_hands=1,
                model_complexity=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5)
        as hands):

            # Converti l'immagine in RGB per MediaPipe
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image_rgb)
            hand = None

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    hand = Hand(hand_landmarks)

            # Draw the hand annotations on the image.
            image.flags.writeable = True
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())

        # Converti l'immagine annotata in base64
        _, buffer = cv2.imencode('.jpg', image)
        annotated_image_base64 = base64.b64encode(buffer).decode('utf-8')

        return {
            'annotated_image': f'data:image/jpeg;base64,{annotated_image_base64}' if send_image_response else None,
            'hand_state': f'{hand.get_state()}' if hand else None
        }, 200

    except Exception as e:
        print(e)
        return {'error': str(e)}, 500


if __name__ == '__main__':
    app.run(debug=True)
