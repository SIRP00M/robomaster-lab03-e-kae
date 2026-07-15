"""
config_loader.py
ฟังก์ชันสำหรับอ่านไฟล์ config/settings.yaml และแปลงเป็น Dictionary
เพื่อให้ทุกโมดูล (chassis, gimbal, vision, logger, main) เรียกใช้พารามิเตอร์ชุดเดียวกัน
"""

from pathlib import Path
import yaml


def load_config(path="config/settings.yaml") -> dict:
    """
    อ่านไฟล์ .yaml แล้วคืนค่าเป็น dict

    Parameters
    ----------
    path : str | Path
        ตำแหน่งไฟล์ settings.yaml (ค่า default = config/settings.yaml
        โดยอ้างอิงจาก working directory ที่รัน main.py)

    Returns
    -------
    dict
        ค่า config ทั้งหมด เช่น config["movement"]["distance_m"]
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"ไม่พบไฟล์ config: {path.resolve()}")

    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)
