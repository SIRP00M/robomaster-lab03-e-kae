"""
logger.py
คลาสสำหรับเก็บข้อมูล sensor (attitude, position, imu, esc) จาก callback ของ RoboMaster SDK
แล้ว save เป็น CSV + plot กราฟ
แยก logic มาจาก test.py เดิม (ที่ใช้ global dict/function) ให้เป็นคลาสที่ chassis.py เรียกใช้ได้
"""

import csv
import threading
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


class SensorLogger:
    """
    เก็บข้อมูลจาก callback ของ chassis (attitude, position, imu, esc)
    แล้ว save เป็น CSV และ plot กราฟให้อัตโนมัติ
    """

    def __init__(self, out_dir, run_id: str, tz_offset_hours: float = 7):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

        self.run_id = run_id
        self.tz = timezone(timedelta(hours=tz_offset_hours))

        self.lock = threading.Lock()
        self.t0 = time.time()

        self.logs = {
            "attitude": [],
            "position": [],
            "imu": [],
            "esc": [],
        }

    # ---------- helpers ----------
    def _now(self):
        dt = datetime.now(self.tz)
        return dt.isoformat(timespec="milliseconds")

    def _elapsed_s(self):
        return round(time.time() - self.t0, 4)

    # ---------- callbacks (เรียกจาก ChassisController.subscribe_sensors) ----------
    def cb_attitude(self, attitude_info):
        # SDK callback: (yaw, pitch, roll)
        yaw, pitch, roll = attitude_info

        with self.lock:
            self.logs["attitude"].append({
                "time_utc7": self._now(),
                "elapsed_s": self._elapsed_s(),
                "yaw_deg": yaw,
                "pitch_deg": pitch,
                "roll_deg": roll,
            })

    def cb_position(self, position_info):
        # SDK callback: (x, y, z) -- x/y = meter, z = degree
        x, y, z = position_info

        with self.lock:
            self.logs["position"].append({
                "time_utc7": self._now(),
                "elapsed_s": self._elapsed_s(),
                "x_m": x,
                "y_m": y,
                "z_deg": z,
            })

    def cb_imu(self, imu_info):
        # SDK callback: (acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z)
        acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z = imu_info

        with self.lock:
            self.logs["imu"].append({
                "time_utc7": self._now(),
                "elapsed_s": self._elapsed_s(),
                "acc_x_sdk_unit": acc_x,
                "acc_y_sdk_unit": acc_y,
                "acc_z_sdk_unit": acc_z,
                "gyro_x_sdk_unit": gyro_x,
                "gyro_y_sdk_unit": gyro_y,
                "gyro_z_sdk_unit": gyro_z,
            })

    def cb_esc(self, esc_info):
        # SDK callback: (speed[4], angle[4], timestamp, state)
        speed, angle, timestamp, state = esc_info

        with self.lock:
            self.logs["esc"].append({
                "time_utc7": self._now(),
                "elapsed_s": self._elapsed_s(),
                "speed_1_rpm": speed[0],
                "speed_2_rpm": speed[1],
                "speed_3_rpm": speed[2],
                "speed_4_rpm": speed[3],
                "angle_1_raw": angle[0],
                "angle_2_raw": angle[1],
                "angle_3_raw": angle[2],
                "angle_4_raw": angle[3],
                "esc_timestamp": timestamp,
                "esc_state": state,
            })

    # ---------- save ----------
    def _save_csv(self, name):
        rows = self.logs[name]
        if not rows:
            print(f"[WARN] no data for {name}")
            return None

        path = self.out_dir / f"{name}_{self.run_id}.csv"

        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        print(f"[SAVE] {path}")
        return path

    def save_all(self):
        """Save ทุก sensor เป็น CSV แล้วคืน dict ของ path (ใช้ต่อใน plot_all)"""
        return {
            "attitude": self._save_csv("attitude"),
            "position": self._save_csv("position"),
            "imu": self._save_csv("imu"),
            "esc": self._save_csv("esc"),
        }

    # ---------- plot ----------
    def _plot_csv(self, csv_path, title, y_columns):
        if csv_path is None:
            return

        df = pd.read_csv(csv_path)
        df["time_utc7"] = pd.to_datetime(df["time_utc7"])

        plt.figure(figsize=(12, 6))

        for col in y_columns:
            if col in df.columns:
                plt.plot(df["time_utc7"], df[col], label=col)

        plt.title(title)
        plt.xlabel("Time UTC+7")
        plt.ylabel("Value")
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=25)
        plt.tight_layout()

        png_path = csv_path.with_suffix(".png")
        plt.savefig(png_path, dpi=200)
        plt.close()

        print(f"[PLOT] {png_path}")

    def plot_all(self, csv_paths: dict):
        """รับ dict path จาก save_all() แล้ว plot กราฟทุก sensor"""
        self._plot_csv(
            csv_paths.get("attitude"),
            "RoboMaster Attitude vs Time UTC+7",
            ["yaw_deg", "pitch_deg", "roll_deg"],
        )

        self._plot_csv(
            csv_paths.get("position"),
            "RoboMaster Position vs Time UTC+7",
            ["x_m", "y_m", "z_deg"],
        )

        self._plot_csv(
            csv_paths.get("imu"),
            "RoboMaster IMU vs Time UTC+7",
            [
                "acc_x_sdk_unit",
                "acc_y_sdk_unit",
                "acc_z_sdk_unit",
                "gyro_x_sdk_unit",
                "gyro_y_sdk_unit",
                "gyro_z_sdk_unit",
            ],
        )

        self._plot_csv(
            csv_paths.get("esc"),
            "RoboMaster ESC Speed vs Time UTC+7",
            [
                "speed_1_rpm",
                "speed_2_rpm",
                "speed_3_rpm",
                "speed_4_rpm",
            ],
        )
