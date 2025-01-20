# HandTracking
 A simple little Python project that uses `mediapipe hands` to track the hands and a little bit of `flask` to make a
 web application where you can interact with some gesture.

# Gestures
Here is a list of all the gesture that can be recognised:
- `open`: a open hand, where all fingers are straight out
- `closed`: a fist, where the hand is closed in a fist
- `thumbs_up`: the *like* sign, where you make a fist with your thumb up
- `thumbs_down`: the *dislike* sign, the opposite direction as the `thumbs_up`
- `zooming`: (works best in vertical position), where you stick out your pinky and thumb
- `pointing`: (not very precise), where you stick out your index and point

# How to run
## Standalone
You can run this program as simple standalone where it simply prints on the CMD the state of the hand.

## Flask
You can run it as a Flask app with a web interface on `127.0.0.1:5000`.