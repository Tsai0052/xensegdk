import cv2
import time
import threading
import json
import os
import argparse
import shutil

FPS = 30.0

def initialize_cam():
    caps = []
    for i in range(1, 5):
        cap = cv2.VideoCapture(f"/dev/cam_{i}")
        if cap.isOpened():
            print(f"cam_{i} initialized successfully.")
        else:
            print(f"cam_{i} initialization failed.")
        caps.append(cap)
    return caps

def record_single(cap, index, stop_event, output_root, fourcc):
    out = cv2.VideoWriter(os.path.join(output_root,f"cam_{index}.mp4"), fourcc, FPS, (640, 480))
    timestamps = [0] * int(FPS * 300)
    
    timestamp_idx = 0
    while not stop_event.is_set():
        t_b = time.time_ns()
        ret, frame = cap.read()
        t_a = time.time_ns()
        t = (t_a + t_b)//2
        assert ret and frame is not None
        timestamps[timestamp_idx] = t
        timestamp_idx+=1

        out.write(frame)
    
    cap.release()
    out.release()
    print(f"cam_{index} released")
    
    with open(os.path.join(output_root,f"cam_{index}.json"), "w") as f:
        timestamps = list(filter(lambda ts: ts != 0, timestamps))
        json.dump(timestamps, f)

def start_recording(caps, stop_event, output_root, fourcc):
    threads = []
    for i in range(4):
        cap = caps[i]
        thread = threading.Thread(target=record_single, args=(cap, i+1, stop_event, output_root, fourcc))
        thread.start()
        threads.append(thread)
    return threads

def wait_for_exit(stop_event):
    input("Recording... Press [Enter] to stop.\n")
    stop_event.set()

def analyze_video(cam_index):
    print(f"cam_{cam_index} data analysis:")
    video_path = os.path.join(args.output_root,f"cam_{cam_index}.mp4")
    json_path = os.path.join(args.output_root,f"cam_{cam_index}.json")
    cap = cv2.VideoCapture(video_path)
    with open(json_path, 'r') as f:
        timestamps = json.load(f)
    timestamps = [stamp for stamp in timestamps if stamp!=0]
    if not cap.isOpened():
        print(f"Video loading failed.")
        return
    
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    assert(frame_count == len(timestamps))

    duration = (timestamps[-1] - timestamps[0]) / 1e9
    fps = frame_count / duration

    print(f"Duration: {duration}s")
    print(f"FPS: {fps}")

    cap.release()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--task-id', required=True)
    parser.add_argument('--job_id', required=True)
    parser.add_argument('--sn_code', default = "A2D0015AB00003" )
    parser.add_argument('--output_root', default="./")
    args = parser.parse_args()

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # 确保输出目录存在
    os.makedirs(args.output_root, exist_ok=True)

    caps = initialize_cam()
    assert len(caps) == 4
    stop_event = threading.Event()
    threads = start_recording(caps, stop_event, args.output_root, fourcc)
    exit_thread = threading.Thread(target=wait_for_exit, args=(stop_event,))
    exit_thread.start()
    
    try:
        while not stop_event.is_set():
            time.sleep(0.1)
    finally:
        for thread in threads:
            thread.join()
        exit_thread.join()
        print("Recording over")

        print("======================Analysing======================")
        for i in range(1,5):
            analyze_video(i)