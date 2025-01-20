# HandTracking
A simple little Python project that uses `mediapipe hands` to track the hands and a little bit of `flask` to make a
web application where you can interact with some gesture.
The web application has two pages:
1. `Display`: A page to show the hand state and the tracking
2. `Interact`: A page where you can guide a cube with the following gestures:
- `open`: makes the cube bigger
- `closed`: makes the cube smaller
- `pointing_right`: moves the cube right
- `pointing_left`: moves the cube left
- `thumbs_up`: moves the cube up
- `thumbs_down`: moves the cube down

In the `Interact` page you can also `Record` and `Playback` the recording.

# Gestures
Here is a list of all the gesture that can be recognised:
- `open`: a open hand, where all fingers are straight out
- `closed`: a fist, where the hand is closed in a fist
- `thumbs_up`: the *like* sign, where you make a fist with your thumb up
- `thumbs_down`: the *dislike* sign, the opposite direction as the `thumbs_up`
- `zooming`: (works best in vertical position), where you stick out your pinky and thumb
- `pointing_right`: (not very precise), where you stick out your index and point on the right
- `pointing_left`: like the `pointing_right` but for the left side

# How to run
## Standalone
You can run this program as simple standalone where it simply prints on the CMD the state of the hand.

## Flask
You can run it as a Flask app with a web interface on `127.0.0.1:5000`.