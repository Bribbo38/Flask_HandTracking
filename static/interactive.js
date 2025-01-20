document.addEventListener('DOMContentLoaded', async () => {
    let isCapturing = false;
    let isRecording = false;
    let stream;
    let x, y;
    let boxSize = 20;
    let speed = 10;
    let record = [];

    const videoInput = document.getElementById('input_video');
    const output = document.getElementById('display');
    const stateOutput = document.getElementById("output_state");
    const startCaptureButton = document.getElementById('start_capture');
    const stopCaptureButton = document.getElementById('stop_capture');

    const startRecordingButton = document.getElementById('start_recording');
    const stopRecordingButton = document.getElementById('stop_recording');
    const playbackButton = document.getElementById('playback');

    output.width = window.innerWidth;
    output.height = window.innerHeight;
    const ctx = output.getContext('2d');

    async function startCapture() {
        isCapturing = true;

        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: window.innerWidth, height: window.innerHeight
                }
            });

            videoInput.srcObject = stream;

            startCaptureButton.disabled = true;
            stopCaptureButton.disabled = false;
            startRecordingButton.disabled = false;

            window.scrollTo(0, document.body.scrollHeight);
            videoInput.addEventListener('loadedmetadata', () => captureLoop());
        } catch (error) {
            console.error('Error accessing webcam:', error);
        }
    }

    function stopCapture() {
        isCapturing = false;
        if (stream) {
            stream.getTracks().forEach(track => track.stop()); // Ferma lo stream
        }

        clearScreen();

        startCaptureButton.disabled = false;
        stopCaptureButton.disabled = true;
        stopRecording();
        startRecordingButton.disabled = true;
    }

    function startRecording() {
        record = [] // Pulisci memoria
        record.push({x: x, y: y}) // Save start coordinates
        isRecording = true;
        startRecordingButton.disabled = true;
        stopRecordingButton.disabled = false;
        playbackButton.disabled = true;
    }

    function stopRecording() {
        isRecording = false;
        startRecordingButton.disabled = false;
        stopRecordingButton.disabled = true;

        if (record.length > 0)
            playbackButton.disabled = false;

        boxSize = 20;
    }

    async function captureLoop() {
        if (!isCapturing) return;

        const base64Image = captureFrame(videoInput);
        if (!base64Image) {
            console.error('Failed to capture frame');
            return;
        }

        const data = await sendImageToBackend(base64Image);

        if (data?.hand_state) {
            stateOutput.innerHTML = `State: ${data.hand_state}`;
            moveCube(data.hand_state);
        }


        if (!isCapturing) {
            clearScreen();
        } else {
            requestAnimationFrame(captureLoop);
        }
    }

    function captureFrame(videoElement) {
        if (videoElement.videoWidth === 0 || videoElement.videoHeight === 0) {
            console.error('Video not ready');
            return null;
        }

        const offscreenCanvas = document.createElement('canvas');
        offscreenCanvas.width = videoElement.videoWidth;
        offscreenCanvas.height = videoElement.videoHeight;
        const ctxOff = offscreenCanvas.getContext('2d');
        ctxOff.drawImage(videoElement, 0, 0);
        return offscreenCanvas.toDataURL('image/jpeg');
    }

    async function sendImageToBackend(base64Image) {
        try {
            const response = await fetch('/api/render', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: base64Image,
                })
            });

            if (response.status === 200) {
                return response.json();
            }

            console.log("Server Error", response.json());
            return null;
        } catch (error) {
            console.log('Error communicating with backend', error);
            return null;
        }
    }

    function clearScreen() {
        ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

        x = ctx.canvas.width / 2 - boxSize;
        y = ctx.canvas.height / 2 - boxSize;

        drawCube();
    }

    function drawCube() {
        ctx.fillStyle = '#333';
        ctx.fillRect(x, y, boxSize, boxSize);
    }

    function moveCube(state) {
        ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

        switch (state) {
            case 'thumbs_up':
                if (y > 0) y -= speed;
                break;

            case 'thumbs_down':
                if (y < output.height - boxSize) y += speed;
                break;

            case 'pointing_left':
                if (x > 0) x -= speed;
                break;

            case 'pointing_right':
                if (x < output.width - boxSize) x += speed;
                break;

            case 'open':
                if (boxSize < 100) boxSize += speed;
                break;

            case 'closed':
                if (boxSize > 10) boxSize -= speed;
                break;
        }

        if (isRecording) {
            record.push(state);
        }

        drawCube();
    }

    async function playback() {
        stopCapture()
        startCaptureButton.disabled = true;
        playbackButton.disabled = true;

        x = record[0].x;
        y = record[0].y;

        for (const i of record.slice(1)) { // from the second position
            await sleep(100);
            moveCube(i);
        }

        playbackButton.disabled = false;
        startCaptureButton.disabled = false;
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    startCaptureButton.addEventListener('click', startCapture);
    stopCaptureButton.addEventListener('click', stopCapture);
    startRecordingButton.addEventListener('click', startRecording);
    stopRecordingButton.addEventListener('click', stopRecording);

    playbackButton.addEventListener('click', playback);

    stopCaptureButton.disabled = true;
    startRecordingButton.disabled = true;
    stopRecordingButton.disabled = true;
    playbackButton.disabled = true;

    clearScreen();
});