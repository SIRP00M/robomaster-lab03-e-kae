"""
main.py
สคริปต์รันหุ่นยนต์หลัก (Entry Point)
ดึงโค้ดทุกส่วน (config, chassis, logger) จากโฟลเดอร์ src/ มารวมกันที่นี่
"""

import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from robomaster import robot
import robomaster

from src.config_loader import load_config
from src.chassis import ChassisController
from src.logger import SensorLogger

def main():
    config = load_config("config/settings.yaml")

    tz = timezone(timedelta(hours=config["logging"]["timezone_offset_hours"]))
    run_id = datetime.now(tz).strftime("%Y%m%d_%H%M%S")
    out_dir = Path("data/raw") / f"run_{run_id}"

    sensor_logger = SensorLogger(
        out_dir=out_dir,
        run_id=run_id,
        tz_offset_hours=config["logging"]["timezone_offset_hours"],
    )

    ep_robot = robot.Robot()
    chassis = None  # กันไว้ก่อน เผื่อ initialize() ล้มเหลวก่อนสร้าง chassis จริง

    conn_type = config["robot"]["conn_type"]
    local_ip = config["robot"].get("local_ip")

    if local_ip:
        # ระบุ local IP เอง กรณีเครื่องมี network card หลายตัว
        # (WiFi + Ethernet + VPN ฯลฯ) แล้ว SDK เลือก adapter ผิดตัวอัตโนมัติ
        robomaster.config.LOCAL_IP_STR = local_ip
        print(f"[INFO] using local_ip = {local_ip}")

    try:
        ep_robot.initialize(conn_type="conn_type")

        chassis = ChassisController(
            ep_robot=ep_robot,
            logger=sensor_logger,
            freq=config["sensor"]["freq"],
        )

        chassis.subscribe_sensors()

        chassis.square_path(
            distance_m=config["movement"]["distance_m"],
            move_speed=config["movement"]["move_speed"],
            turn_angle=config["movement"]["turn_angle"],
            turn_speed=config["movement"]["turn_speed"],
            pause_s=config["movement"]["pause_s"],
        )

        time.sleep(1.0)  # เก็บข้อมูลหลังหยุด

    except Exception as e:
        # กันไม่ให้ error ระหว่างทาง (wifi หลุด, timeout ฯลฯ) ทำให้เสียข้อมูลที่เก็บมาได้แล้วทั้งหมด
        print(f"[ERROR] เกิดข้อผิดพลาดระหว่างรัน: {e!r}")

    finally:
        if chassis is not None:
            chassis.unsubscribe_sensors()
        ep_robot.close()

        # ย้าย save/plot มาไว้ใน finally เพื่อให้ save ข้อมูลที่เก็บได้เสมอ
        # ไม่ว่าข้างบนจะรันจบปกติหรือเกิด error ระหว่างทางก็ตาม
        print("[INFO] saving csv...")
        csv_paths = sensor_logger.save_all()

        print("[INFO] plotting graphs...")
        sensor_logger.plot_all(csv_paths)

        print(f"[DONE] files saved in: {out_dir}")


if __name__ == "__main__":
    main()