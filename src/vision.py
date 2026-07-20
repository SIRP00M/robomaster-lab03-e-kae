"""
vision.py
Class for camera streaming and image processing using OpenCV

Note: The original script does not currently use the camera.
This class provides a basic skeleton that the team can extend with additional functionality.
"""

import cv2


class VisionStream:
    """Wrapper around ep_robot.camera from the RoboMaster SDK for image streaming and processing"""

    def __init__(self, ep_robot):
        self.camera = ep_robot.camera

    def start(self, display: bool = False):
        self.camera.start_video_stream(display=display)

    def stop(self):
        self.camera.stop_video_stream()

    def read_frame(self, timeout: float = 3.0):
        """Read the current frame as an OpenCV image (NumPy array in BGR format)"""
        return self.camera.read_cv2_image(timeout=timeout)

    def show_frame(self, window_name: str = "RoboMaster", timeout: float = 3.0):
        """Display the current frame in an OpenCV window for debugging"""
        frame = self.read_frame(timeout=timeout)
        cv2.imshow(window_name, frame)
        cv2.waitKey(1)
        return frame