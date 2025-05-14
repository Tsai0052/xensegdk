# 并法采集robot数据和tactile数据，后用时间戳对齐

import cv2
from xensesdk.omni.widgets import ExampleView
from xensesdk.xenseInterface.XenseSensor import Sensor

import threading
import time
import sys
import numpy as np
import os

sensor_config_path = "/home/xuckham07/xense_dp/config_0.2.1"
data_save_path = "/home/xuckham07/xense_dp/raw_data/test_record_script"

class Sensor:
    def __init__(self, camera_index, config_path):
        self.camera_index = camera_index
        self.config_path = config_path
        self.sensor = Sensor.create(camera_index, config_path=config_path, check_serial=False)

def check_cameras(max_index):
    available_cameras = {} # key: camera index, value: camera config number
    for i in range(max_index + 1):
        cap = cv2.VideoCapture(i)
        if not cap.isOpened():
            continue

        while(True):
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow(f"Camera {i}", frame)
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
        cv2.destroyAllWindows()
        cap.release()

        available_cameras[i] = int(input("Enter camera config number for camera {}: ".format(i)))

    return available_cameras

def initailize_sensor(available_cameras):
    sensors = []
    for camera_index, config_number in available_cameras.items():
        sensor = Sensor(camera_index, config_path=os.path.join(sensor_config_path, f"QJ-SW-0{config_number}"))
        sensors.append(sensor)
        print(f"Sensor {camera_index} initialized with config number {config_number}")
    return sensors


def record_individual_tactile_data(sensor, save_path, stop_event):
    data_to_save = [
    Sensor.OutputType.Difference,
    Sensor.OutputType.Depth,
    Sensor.OutputType.Marker2D,
    Sensor.OutputType.Rectify
    ]
    sensor.startSaveSensorInfo(save_path, data_to_save)
    while not stop_event.is_set():
        time.sleep(0.01)  # 每10ms检查一次，响应更快
    sensor.stopSaveSensorInfo()
    print(f"Tactile data saved to {save_path}")

def record_tactile_data(sensors,stop_event):
    threads = []
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    for sensor in sensors:
        save_path = os.path.join(data_save_path, f"tactile_data_{sensor.camera_index}_{timestamp}")
        thread = threading.Thread(target=record_individual_tactile_data, args=(sensor, save_path,stop_event))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print("All tactile data recorded.")

if __name__ == "__main__":
    # max_index = 6
    # available_cameras = check_cameras(max_index)
    sensors = initailize_sensor(available_cameras={1: 93, 2: 55, 4: 96, 6: 65})

    stop_event = threading.Event()

    record_tactile_data(sensors,stop_event)
    
    print("Press 'q' to stop recording...")
    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Stopping recording...")
            stop_event.set()  # 通知所有子线程退出
            break
        time.sleep(0.01)
