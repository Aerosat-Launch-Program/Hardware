import picamera

# Initialize the camera
camera = picamera.PiCamera()

try:
    # Start recording a video
    camera.start_recording('video.h264')
    # Record for 10 seconds (you can change the duration)
    camera.wait_recording(10)
    # Stop recording
    camera.stop_recording()
    print("Video captured and saved as 'video.h264'")
finally:
    # Close the camera to release resources
    camera.close()
