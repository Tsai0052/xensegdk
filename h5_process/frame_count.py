import subprocess
import json
video_path = '/home/xuckham07/xense_dp/raw_data/test_xensegdk/batch_20250425_165203/sensor_4_rectify_video_2025_04_25_16_52_03.mp4'
def get_frame_count(video_path):
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-count_frames',
        '-show_entries', 'stream=nb_read_frames',
        '-print_format', 'json',
        video_path
    ]
    output = subprocess.check_output(cmd).decode('utf-8')
    data = json.loads(output)
    frame_count = int(data['streams'][0]['nb_read_frames'])
    return frame_count

print(f"Total frames: {get_frame_count(video_path)}")
