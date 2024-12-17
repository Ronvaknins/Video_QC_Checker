import cv2
from tqdm import tqdm
import re
import sys

def frames_to_timecode(frame_count, fps):
    total_seconds = frame_count / fps
    hours = int(total_seconds // 3600)
    total_seconds %= 3600
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    frames = int((total_seconds - int(total_seconds)) * fps)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"

def is_frame_all_black(frame_gpu):
    # Convert the frame to grayscale using CUDA
    gray_frame_gpu = cv2.cuda.cvtColor(frame_gpu, cv2.COLOR_BGR2GRAY)
    # Download to CPU for checking blackness
    gray_frame = gray_frame_gpu.download()
    # Check if all pixel values are zero (black)
    return cv2.countNonZero(gray_frame) == 0

def calculate_histogram(frame_gpu):
    # Convert to grayscale on GPU before calculating histogram
    gray_frame_gpu = cv2.cuda.cvtColor(frame_gpu, cv2.COLOR_BGR2GRAY)
    # Download for histogram calculation
    gray_frame = gray_frame_gpu.download()
    hist = cv2.calcHist([gray_frame], [0], None, [256], [0, 256])
    return hist

def calculate_scene_frame_counts(video_file):
    cap = cv2.VideoCapture(video_file)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Create a tqdm progress bar with the total number of frames
    pbar = tqdm(total=frame_count)
    hist_threshold = 0.5  # Adjust as needed

    # Read the first frame
    ret, prev_frame = cap.read()
    if not ret:
        cap.release()
        return []

    # Upload the first frame to GPU memory
    prev_frame_gpu = cv2.cuda_GpuMat()
    prev_frame_gpu.upload(prev_frame)
    prev_hist = calculate_histogram(prev_frame_gpu)

    short_scene_tc = []

    frame_count_in_scene = 0
    frame_num = 0
    while True:
        frame_num += 1
        ret, frame = cap.read()
        if not ret:
            break
        
        # Upload the current frame to GPU memory
        frame_gpu = cv2.cuda_GpuMat()
        frame_gpu.upload(frame)

        # Calculate histogram for the current frame
        curr_hist = calculate_histogram(frame_gpu)

        # Calculate histogram correlation
        correlation = cv2.compareHist(prev_hist, curr_hist, cv2.HISTCMP_CORREL)

        # If correlation is below threshold, it indicates a scene change
        if correlation < hist_threshold:
            if frame_count_in_scene < fps - 10:
                tc = frames_to_timecode(frame_num, fps)
                f.write(f"Short Scene,{tc}\n")
                short_scene_tc.append(tc)

            frame_count_in_scene = 1
            if is_frame_all_black(frame_gpu):
                f.write(f"Black Frame,{frames_to_timecode(frame_num, fps)}\n")
        else:
            frame_count_in_scene += 1

        # Update previous histogram
        prev_hist = curr_hist
        pbar.update(1)

    pbar.close()
    cap.release()
    return short_scene_tc

video_file = sys.argv[1]
print(video_file)
matches = re.search(r'\\([^\\]+)\.(\w+)$', video_file)

# Create CSV file
file_path = matches.group(1) + ".csv"
f = open(file_path, 'w')
f.write("Type,TC\n")
calculate_scene_frame_counts(video_file)
f.close()
