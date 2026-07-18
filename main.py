import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from robomaster import robot
import robomaster

from src.config_loader import load_config
from src.chassis import ChassisController
from src.logger import SensorLogger

def main():
    # Load all settings from the YAML file
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
    chassis = None  # Set this first in case the robot cannot connect

    # Get the connection mode, such as "ap", from settings.yaml
    conn_type = config["robot"]["conn_type"]
    local_ip = config["robot"].get("local_ip")

    if local_ip:
        # Use the selected IP when the computer has many connections
        robomaster.config.LOCAL_IP_STR = local_ip
        print(f"[INFO] using local_ip = {local_ip}")

    try:
        ep_robot.initialize(conn_type=conn_type)

        chassis = ChassisController(
            ep_robot=ep_robot,
            logger=sensor_logger,
            freq=config["sensor"]["freq"],
        )

        # Start collecting sensor data before the robot moves
        chassis.subscribe_sensors()

        # Move the robot in a square using the configured values
        chassis.square_path(
            distance_m=config["movement"]["distance_m"],
            move_speed=config["movement"]["move_speed"],
            turn_angle=config["movement"]["turn_angle"],
            turn_speed=config["movement"]["turn_speed"],
            pause_s=config["movement"]["pause_s"],
        )

        time.sleep(1.0)  # Wait a little longer to collect data

    except Exception as e:
        # Show a message if something goes wrong
        print(f"[ERROR] An error occurred while running: {e!r}")

    finally:
        if chassis is not None:
            chassis.unsubscribe_sensors()
        ep_robot.close()

        # Save the data and make the graphs before the program ends
        print("[INFO] saving csv...")
        csv_paths = sensor_logger.save_all()

        print("[INFO] plotting graphs...")
        sensor_logger.plot_all(csv_paths)

        print(f"[DONE] files saved in: {out_dir}")


if __name__ == "__main__":
    main()
