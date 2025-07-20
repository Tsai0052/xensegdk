import os
import threading
import time
import cv2
import json
import argparse
import numpy as np
import h5py

from xensesdk.omni.widgets import ExampleView
from xensesdk.xenseInterface.XenseSensor import Sensor

'''
只保存Rectify图像，在并行采集时能保证30fps
'''
data_to_save = [
    Sensor.OutputType.Rectify, 
    # Sensor.OutputType.Difference,
    # Sensor.OutputType.Depth,
    # Sensor.OutputType.Marker2D,
    # Sensor.OutputType.Force,
    # Sensor.OutputType.ForceNorm,
    # # Sensor.OutputType.ForceResultant,
    # Sensor.OutputType.Mesh3D,
    # Sensor.OutputType.Mesh3DInit,
    # Sensor.OutputType.Mesh3DFlow,
]

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

def initialize_sensor(available_cameras, sensor_config_path): 
    sensors = []
    for camera_index, config_number in available_cameras.items():
        config_path = os.path.join(sensor_config_path, f"QJ-SW-{config_number:03d}")
        sensor = Sensor.create(camera_index, config_path, check_serial = False)
        sensors.append(sensor)
        print(f"Sensor {camera_index} initialized with config path: {config_path}")
    return sensors

def record_individual_tactile_data(sensor, save_path, stop_event):
    os.makedirs(save_path, exist_ok=True)

    sensor.startSaveSensorInfo(save_path, data_to_save)
    while not stop_event.is_set():
        time.sleep(0.01)
    sensor.stopSaveSensorInfo()

def start_recording_threads(sensors, stop_event, output_root):
    threads = []
    os.makedirs(output_root, exist_ok=True)

    for sensor in sensors:
        thread = threading.Thread(target=record_individual_tactile_data, args=(sensor, output_root, stop_event))
        thread.start()
        threads.append(thread)
    return threads

def wait_for_exit(stop_event):
    input("Recording... Press [Enter] to stop.\n")
    stop_event.set()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--job_id', required=True)
    parser.add_argument('--sn_code', default = "A2D0015AB00003" )
    parser.add_argument('--output_root', default="./")
    parser.add_argument('--sensor_config_path', default="./config_0.2.1")

    args = parser.parse_args()

    available_cameras = {0: 55, 2: 93, 4: 91, 6: 65}
    sensors = initialize_sensor(available_cameras, args.sensor_config_path)

    stop_event = threading.Event()

    threads = start_recording_threads(sensors, stop_event, args.output_root)

    exit_thread = threading.Thread(target=wait_for_exit, args=(stop_event,))
    exit_thread.start()

    try:
        while not stop_event.is_set():
            time.sleep(0.1)
    finally:
        for thread in threads:
            thread.join()
        exit_thread.join()
        cv2.destroyAllWindows()
        print("Recording over")
