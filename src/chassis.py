"""
chassis.py
คลาสควบคุมล้อ Mecanum (เดินหน้า, ถอยหลัง, สไลด์ข้าง)
รับผิดชอบ: subscribe/unsubscribe sensor และคำสั่งเคลื่อนที่พื้นฐานของ chassis
"""

import time


class ChassisController:
    """
    Wrapper รอบ ep_robot.chassis ของ RoboMaster SDK
    """

    def __init__(self, ep_robot, logger, freq: int = 20):
        self.chassis = ep_robot.chassis
        self.logger = logger
        self.freq = freq

    # ---------- sensor subscription ----------
    def subscribe_sensors(self):
        print("[INFO] subscribing sensors...")
        self.chassis.sub_attitude(freq=self.freq, callback=self.logger.cb_attitude)
        self.chassis.sub_position(cs=0, freq=self.freq, callback=self.logger.cb_position)
        self.chassis.sub_imu(freq=self.freq, callback=self.logger.cb_imu)
        self.chassis.sub_esc(freq=self.freq, callback=self.logger.cb_esc)
        time.sleep(1.0)  # ให้ sensor เริ่มส่งข้อมูลก่อน

    def unsubscribe_sensors(self):
        print("[INFO] unsubscribing sensors...")
        try:
            self.chassis.unsub_attitude()
            self.chassis.unsub_position()
            self.chassis.unsub_imu()
            self.chassis.unsub_esc()
        except Exception as e:
            print("[WARN] unsubscribe error:", e)

    # ---------- movement ----------
    def move_forward(self, distance_m: float, speed: float):
        self.chassis.move(x=distance_m, y=0, z=0, xy_speed=speed).wait_for_completed()

    def move_backward(self, distance_m: float, speed: float):
        self.chassis.move(x=-distance_m, y=0, z=0, xy_speed=speed).wait_for_completed()

    def slide(self, distance_m: float, speed: float):
        """สไลด์ข้าง (แกน y) — บวก = ขวา, ลบ = ซ้าย"""
        self.chassis.move(x=0, y=distance_m, z=0, xy_speed=speed).wait_for_completed()

    def turn(self, angle_deg: float, speed: float):
        """หมุน chassis — angle_deg บวก = หมุนซ้าย, ลบ = หมุนขวา (ตาม RoboMaster SDK)"""
        self.chassis.move(x=0, y=0, z=angle_deg, z_speed=speed).wait_for_completed()

    def square_path(self, distance_m, move_speed, turn_angle, turn_speed, pause_s=1.0, sides=4):
        print("[INFO] Start square path")
        for i in range(sides):
            print(f"[MOVE] Side {i + 1}")
            self.move_forward(distance_m, move_speed)
            time.sleep(pause_s)

            print("[TURN] Right")
            self.turn(-abs(turn_angle), turn_speed)
            time.sleep(pause_s)

        print("[INFO] Square path completed")
