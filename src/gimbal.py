"""
gimbal.py
Class for controlling the gimbal-mounted camera angle

Note: The original script does not currently use the gimbal.
This class provides a basic skeleton that the team can extend with additional functionality.
"""


class GimbalController:
    """Wrapper around ep_robot.gimbal from the RoboMaster SDK"""

    def __init__(self, ep_robot):
        self.gimbal = ep_robot.gimbal

    def recenter(self):
        """Return the gimbal to its center position"""
        self.gimbal.recenter().wait_for_completed()

    def move(self, pitch: float = 0, yaw: float = 0,
            pitch_speed: float = 100, yaw_speed: float = 100):
        self.gimbal.move(
            pitch=pitch,
            yaw=yaw,
            pitch_speed=pitch_speed,
            yaw_speed=yaw_speed,
        ).wait_for_completed()