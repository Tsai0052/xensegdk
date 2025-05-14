import os
import threading
import time
import cv2
import sys
from xensesdk.omni.widgets import ExampleView
from xensesdk.xenseInterface.XenseSensor import Sensor

sensor_config_path = r"/home/xuckham07/xense_dp/config_0.2.1"
data_save_root = r"/home/xuckham07/xense_dp/raw_data/move_tmp"

class FullSensor:
    def __init__(self, camera_index, config_path):
        self.camera_index = camera_index
        self.config_path = config_path
        self.sensor = Sensor.create(camera_index,config_path=config_path, check_serial=False)
    def startSaveSensorInfo(self, save_path, data_to_save):
        self.sensor.startSaveSensorInfo(save_path, data_to_save)
    def stopSaveSensorInfo(self):
        self.sensor.stopSaveSensorInfo()
    def release(self):
        self.sensor.release()
        print(f"Sensor {self.camera_index} released.")

def check_cameras(max_index):
    available_cameras = {} 
    for i in range(max_index + 1):
        cap = cv2.VideoCapture(i)
        if not cap.isOpened():
            continue

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow(f"Camera {i}", frame)
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
        cv2.destroyAllWindows()
        cap.release()

        available_cameras[i] = int(input(f"Enter camera config number for camera {i}: "))

    return available_cameras

def initialize_sensor(available_cameras): 
    sensors = []
    for camera_index, config_number in available_cameras.items():
        config_path = os.path.join(sensor_config_path, f"QJ-SW-0{config_number}")
        sensor = FullSensor(camera_index, config_path)
        sensors.append(sensor)
        print(f"Sensor {camera_index} initialized with config path: {config_path}")
    return sensors

def record_individual_tactile_data(sensor, save_path, stop_event):
    os.makedirs(save_path, exist_ok=True)

    data_to_save = [
        Sensor.OutputType.Rectify,
        Sensor.OutputType.Difference,
    ]
    sensor.startSaveSensorInfo(save_path, data_to_save)
    print(f"Started recording for camera {sensor.camera_index} at {save_path}")
    while not stop_event.is_set():
        time.sleep(0.01)
    sensor.stopSaveSensorInfo()
    print(f"Stopped recording for camera {sensor.camera_index}")

def start_recording_threads(sensors, stop_event):
    threads = []
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    data_save_path = os.path.join(data_save_root, f"batch_{timestamp}")
    os.makedirs(data_save_path, exist_ok=True)

    for sensor in sensors:
        save_path = os.path.join(data_save_path, f"tactile_data_{sensor.camera_index}_{timestamp}")
        thread = threading.Thread(target=record_individual_tactile_data, args=(sensor, save_path, stop_event))
        thread.start()
        threads.append(thread)
    return threads

def wait_for_exit(stop_event):
    input("Recording... Press [Enter] to stop.\n")
    stop_event.set()

if __name__ == "__main__":
    # available_cameras = check_cameras(max_index=6)
    # print(available_cameras)
    available_cameras = {0: 93, 2: 55, 4: 96, 6: 65}
    sensors = initialize_sensor(available_cameras)

    stop_event = threading.Event()

    threads = start_recording_threads(sensors, stop_event)

    exit_thread = threading.Thread(target=wait_for_exit, args=(stop_event,))
    exit_thread.start()

    try:
        # 主线程等待退出信号
        while not stop_event.is_set():
            time.sleep(0.1)
    finally:
        for thread in threads:
            thread.join()
        exit_thread.join()
        cv2.destroyAllWindows()
        print("All tactile data collection completed.")
