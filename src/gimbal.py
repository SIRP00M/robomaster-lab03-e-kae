"""
gimbal.py
คลาสควบคุมป้อม/มุมกล้องกิมบอล (Gimbal)

หมายเหตุ: สคริปต์ต้นฉบับที่ให้มายังไม่มีการใช้งานกิมบอล
คลาสนี้เป็นโครงพื้นฐาน (skeleton) ให้ทีมต่อยอดฟังก์ชันเพิ่มเติมได้เอง
"""


class GimbalController:
    """Wrapper รอบ ep_robot.gimbal ของ RoboMaster SDK"""

    def __init__(self, ep_robot):
        self.gimbal = ep_robot.gimbal

    def recenter(self):
        """หมุนกิมบอลกลับตำแหน่งกึ่งกลาง"""
        self.gimbal.recenter().wait_for_completed()

    def move(self, pitch: float = 0, yaw: float = 0,
            pitch_speed: float = 100, yaw_speed: float = 100):
        self.gimbal.move(
            pitch=pitch,
            yaw=yaw,
            pitch_speed=pitch_speed,
            yaw_speed=yaw_speed,
        ).wait_for_completed()