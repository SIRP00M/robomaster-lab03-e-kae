"""
vision.py
คลาสสตรีมภาพและประมวลผลกล้อง (OpenCV)

หมายเหตุ: สคริปต์ต้นฉบับที่ให้มายังไม่มีการใช้งานกล้อง
คลาสนี้เป็นโครงพื้นฐาน (skeleton) ให้ทีมต่อยอดฟังก์ชันเพิ่มเติมได้เอง
"""

import cv2


class VisionStream:
    """Wrapper รอบ ep_robot.camera ของ RoboMaster SDK สำหรับสตรีมและประมวลผลภาพ"""

    def __init__(self, ep_robot):
        self.camera = ep_robot.camera

    def start(self, display: bool = False):
        self.camera.start_video_stream(display=display)

    def stop(self):
        self.camera.stop_video_stream()

    def read_frame(self, timeout: float = 3.0):
        """อ่าน frame ปัจจุบันเป็นภาพ OpenCV (numpy array, BGR)"""
        return self.camera.read_cv2_image(timeout=timeout)

    def show_frame(self, window_name: str = "RoboMaster", timeout: float = 3.0):
        """แสดงผล frame ปัจจุบันในหน้าต่าง OpenCV (สำหรับ debug)"""
        frame = self.read_frame(timeout=timeout)
        cv2.imshow(window_name, frame)
        cv2.waitKey(1)
        return frame