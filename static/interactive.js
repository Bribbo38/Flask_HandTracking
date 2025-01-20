document.addEventListener('DOMContentLoaded', async () => {
    let isCapturing = false;
    let stream;

    const videoInput = document.getElementById('input_video');
    const canvasOutput = document.getElementById('output_canvas');
    const stateOutput = document.getElementById("output_state");
    const startCaptureButton = document.getElementById('start_capture');
    const stopCaptureButton = document.getElementById('stop_capture');

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

        let context = canvasOutput.getContext('2d');
        context.clearRect(0, 0, context.canvas.width, context.canvas.height); // Pulisci canvas

        startCaptureButton.disabled = false;
        stopCaptureButton.disabled = true;
    }

    async function captureLoop() {
        if (!isCapturing) return;

        const base64Image = captureFrame(videoInput);
        if (!base64Image) {
            console.error('Failed to capture frame');
            return;
        }

        const data = await sendImageToBackend(base64Image);

        if (isCapturing) {
            if (data?.annotated_image) {
                const img = new Image();
                img.onload = () => {
                    const ctx = canvasOutput.getContext('2d');
                    canvasOutput.width = videoInput.videoWidth;
                    canvasOutput.height = videoInput.videoHeight;
                    ctx.drawImage(img, 0, 0, canvasOutput.width, canvasOutput.height);
                };
                img.src = data.annotated_image;
            }

            if (data?.hand_state) {
                stateOutput.innerHTML = `State: ${data.hand_state}`;
            }
        }

        requestAnimationFrame(captureLoop);
    }

    function captureFrame(videoElement) {
        if (videoElement.videoWidth === 0 || videoElement.videoHeight === 0) {
            console.error('Video not ready');
            return null;
        }

        const offscreenCanvas = document.createElement('canvas');
        offscreenCanvas.width = videoElement.videoWidth;
        offscreenCanvas.height = videoElement.videoHeight;
        const ctx = offscreenCanvas.getContext('2d');
        ctx.drawImage(videoElement, 0, 0);
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

    startCaptureButton.addEventListener('click', startCapture);
    stopCaptureButton.addEventListener('click', stopCapture);
    stopCaptureButton.disabled = true;
});