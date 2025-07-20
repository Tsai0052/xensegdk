import cv2
import json
import argparse
from pathlib import Path
from collections import namedtuple

VideoInfo = namedtuple('VideoInfo', ['video_name', 'duration', 'fps', 'frames'])

def analyze_video(video_path, json_path):
    with open(json_path) as f:
        timestamps = json.load(f)
    
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return None
    
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    
    duration = (timestamps[-1] - timestamps[0]) / 1e9
    fps = frame_count / duration
    
    return VideoInfo(video_path.name, duration, fps, frame_count)

def find_file_pairs(data_root):
    data_path = Path(data_root)
    pairs = []
    
    for json_file in data_path.glob("*_ts.json"):
        sensor_name = json_file.stem.replace("_ts", "")
        video_file = list(data_path.glob(f"{sensor_name}*.mp4"))
        assert len(video_file) == 1
        video_file = video_file[0]
        
        pairs.append((video_file, json_file))
    
    return pairs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_root", required=True)
    args = parser.parse_args()
    
    file_pairs = find_file_pairs(args.data_root)
    assert len(file_pairs) == 4
    
    for video_path, json_path in file_pairs:
        info = analyze_video(video_path, json_path)
        if info:
            print(f"{info.video_name}: {info.duration:.2f}s, {info.fps:.1f} FPS, {info.frames} frames")
        else:
            print(f"{video_path.stem}: 分析失败")

if __name__ == "__main__":
    main()