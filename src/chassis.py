"""
chassis.py
Mecanum wheel control class (forward, backward, and lateral movement)
Responsibilities: sensor subscription/unsubscription and basic chassis movement commands
"""

import time


class ChassisController:
    """
    Wrapper around ep_robot.chassis from the RoboMaster SDK
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
        time.sleep(1.0)  # Allow sensors to begin transmitting data

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
        """Move laterally along the y-axis — positive = right, negative = left"""
        self.chassis.move(x=0, y=distance_m, z=0, xy_speed=speed).wait_for_completed()

    def turn(self, angle_deg: float, speed: float):
        """Rotate the chassis — positive angle = left, negative angle = right, according to the RoboMaster SDK"""
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