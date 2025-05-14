import cv2

def check_cameras(max_index=6):
    for i in range(max_index + 1):
        cap = cv2.VideoCapture(i)
        if not cap.isOpened():
            print(f"Camera {i}: Cannot open")
            continue

        ret, frame = cap.read()
        if ret:
            print(f"Camera {i}: Successfully opened and grabbed a frame.")
        else:
            print(f"Camera {i}: Opened, but failed to grab a frame.")

        cap.release()

if __name__ == "__main__":
    check_cameras()