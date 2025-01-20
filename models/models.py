import mediapipe as mp

mp_hands = mp.solutions.hands


class Proximity:
    def __init__(self, tip, origin):
        self.x = abs(tip.x - origin.x)
        self.y = abs(tip.y - origin.y)
        self.z = abs(tip.z - origin.z)

    def __str__(self):
        return f"Proximity(x={self.x:.3f}, y={self.y:.3f}, z={self.z:.3f})"


class Finger:
    def __init__(self, tip, origin):
        self.tip = tip
        self.origin = origin
        self.proximity = Proximity(tip, origin)

    def is_bent(self, threshold=0.05):
        """Verifica se il dito è piegato (tip vicino a MCP lungo l'asse y)."""
        return self.proximity.y < threshold

    def is_close_to_origin(self, origin, origin_threshold=0.2, z_threshold=0.05):
        """Verifica se il tip del dito è vicino al centro dell'origine (2D e 3D)."""
        # Distanza euclidea nel piano xy
        distance_to_palm_xy = ((self.tip.x - origin.x) ** 2 + (self.tip.y - origin.y) ** 2) ** 0.5
        # Differenza sull'asse z
        distance_to_palm_z = abs(self.tip.z - origin.z)
        return distance_to_palm_xy < origin_threshold and distance_to_palm_z < z_threshold


class Hand:
    def __init__(self, hand_landmarks):
        self.thumb = Finger(
            hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP],
            hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
        )
        self.index = Finger(
            hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP],
            hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
        )
        self.middle = Finger(
            hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP],
            hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
        )
        self.ring = Finger(
            hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP],
            hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]
        )
        self.pinky = Finger(
            hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP],
            hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
        )
        self.palm = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
        self.fingers = [self.index, self.middle, self.ring, self.pinky]

    def calculate_distance(self, point1, point2):
        """Calcola la distanza euclidea tra due punti."""
        return ((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2 + (point1.z - point2.z) ** 2) ** 0.5

    def calculate_hand_span(self):
        """Calcola la distanza tra il pollice e il mignolo (spanning della mano)."""
        return self.calculate_distance(self.thumb.tip, self.pinky.tip)

    def is_fist(self, bent_threshold=0.05, origin_threshold=0.2, z_threshold=0.05):
        """Verifica se la mano è chiusa a pugno."""
        all_fingers_closed = all(
            finger.is_bent(bent_threshold) and finger.is_close_to_origin(self.palm, origin_threshold, z_threshold)
            for finger in self.fingers
        )
        thumb_close_to_index = self.thumb.is_close_to_origin(self.index.tip, origin_threshold=0.15,
                                                             z_threshold=z_threshold)
        return all_fingers_closed and thumb_close_to_index

    def is_open(self, bent_threshold=0.1, spread_threshold=0.15):
        """Verifica se la mano è completamente aperta"""
        all_fingers_open = all(
            not finger.is_bent(bent_threshold) and
            not finger.is_close_to_origin(self.palm, origin_threshold=spread_threshold)
            for finger in self.fingers
        )
        thumb_spread = self.calculate_distance(self.thumb.tip, self.index.tip)
        thumb_open = thumb_spread > spread_threshold
        return all_fingers_open and thumb_open

    def is_thumbs_up(self):
        """Verifica se il pollice è alzato verso l'alto e le altre dita sono piegate."""
        thumb_up = self.thumb.tip.y < self.thumb.origin.y  # Pollice sopra rispetto al palmo
        return (
                thumb_up and
                all(finger.is_bent() for finger in self.fingers)
        )

    def is_thumbs_down(self):
        """Verifica se il pollice è rivolto verso il basso."""
        thumb_down = self.thumb.tip.y > self.thumb.origin.y  # Pollice sotto rispetto al palmo
        return (
                thumb_down and
                all(finger.is_bent() for finger in self.fingers)
        )

    def is_zooming(self, threshold=0.3):
        """Verifica se il pollice e il mignolo sono molto distanti (zoom)."""
        # Calcola la distanza tra il pollice e il mignolo
        thumb_tip = self.thumb.tip
        pinky_tip = self.pinky.tip
        hand_span = self.calculate_distance(thumb_tip, pinky_tip)

        # Stabilisci una soglia per considerare il gesto come zoom
        return hand_span > threshold

    def is_pointing_right(self, bent_threshold=0.1, spread_threshold=0.2):
        """Verifica se l'indice è esteso e puntato a destra."""
        # Verifica che l'indice sia esteso
        index_extended = not self.index.is_bent(bent_threshold) and not self.index.is_close_to_origin(self.palm,
                                                                                                      spread_threshold)

        # Verifica che tutte le altre dita siano piegate
        other_fingers_bent = all(
            finger.is_bent(bent_threshold) for finger in [self.thumb, self.middle, self.ring, self.pinky])

        # Controlla la direzione: indice puntato a destra rispetto al palmo (specchiato)
        pointing_right = self.index.tip.x < self.palm.x

        return index_extended and other_fingers_bent and pointing_right

    def is_pointing_left(self, bent_threshold=0.1, spread_threshold=0.2):
        """Verifica se l'indice è esteso e puntato a sinistra."""
        # Verifica che l'indice sia esteso
        index_extended = not self.index.is_bent(bent_threshold) and not self.index.is_close_to_origin(self.palm,
                                                                                                      spread_threshold)

        # Verifica che tutte le altre dita siano piegate
        other_fingers_bent = all(
            finger.is_bent(bent_threshold) for finger in [self.thumb, self.middle, self.ring, self.pinky])

        # Controlla la direzione: indice puntato a sinistra rispetto al palmo (specchiato)
        pointing_left = self.index.tip.x > self.palm.x

        return index_extended and other_fingers_bent and pointing_left

    def debug_hand_state(self):
        """Stampa lo stato della mano per il debugging."""
        print(f"Thumb proximity: {self.thumb.proximity}")
        for i, finger in enumerate(self.fingers):
            print(f"Finger {i} proximity: {finger.proximity}")

    def get_state(self):
        """Ritorna lo stato della mano in base ai gesti riconosciuti."""
        if self.is_open():
            return 'open'
        elif self.is_fist():
            return 'closed'
        elif self.is_thumbs_up():
            return 'thumbs_up'
        elif self.is_thumbs_down():
            return 'thumbs_down'
        elif self.is_pointing_right():
            return 'pointing_right'
        elif self.is_pointing_left():
            return 'pointing_left'
        elif self.is_zooming():
            return 'zooming'
        else:
            return 'unknown'
