import cv2
from tqdm import tqdm
import re
import sys
def frames_to_timecode(frame_count, fps):
    total_seconds = frame_count / fps
    hours = 0
    total_seconds %= 3600
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    frames = int((total_seconds - int(total_seconds)) * fps)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"

def is_frame_all_black(frame):
    # Convert the frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Check if all pixel values are zero (black)
    return cv2.countNonZero(gray_frame) == 0

def calculate_scene_frame_counts(video_file):
    cap = cv2.VideoCapture(video_file)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Create a tqdm progress bar with the total number of frames
    pbar = tqdm(total=frame_count)
    # Define parameters for histogram comparison
    hist_threshold = 0.5  # Adjust as needed
    hist_size = 256
    hist_range = (0, 256)
    hist_channels = [0]

    # Read the first frame
    ret, prev_frame = cap.read()
    prev_hist = cv2.calcHist([prev_frame], hist_channels, None, [hist_size], hist_range)

    short_scene_tc = []

    # Loop through the frames
    frame_count_in_scene = 0
    frame_num = 0
    while True:
        frame_num += 1 
        ret, frame = cap.read()
        if not ret:
            break
        
        # Calculate histogram for the current frame
        curr_hist = cv2.calcHist([frame], hist_channels, None, [hist_size], hist_range)

        # Calculate histogram correlation
        correlation = cv2.compareHist(prev_hist, curr_hist, cv2.HISTCMP_CORREL)

        # If correlation is below threshold, it indicates a scene change
        if correlation < hist_threshold:
            if(frame_count_in_scene < fps-10):
                tc = frames_to_timecode(frame_num,fps)
                f.write("Short Scene,{0}\n".format(tc))
                short_scene_tc.append(tc)

            frame_count_in_scene = 1
            if is_frame_all_black(frame):
                
                f.write("Black Frame,{0}\n".format(frames_to_timecode(frame_num,fps)))
                ##print("Black at TC: {0}".format(frames_to_timecode(frame_num,fps)))
        else:
            frame_count_in_scene += 1


        # Update previous histogram
        prev_hist = curr_hist
        pbar.update(1)

    pbar.close()
    cap.release()
    return short_scene_tc




# Close the file

video_file = sys.argv[1]
print(video_file)
matches = re.search(r'\\([^\\]+)\.(\w+)$', video_file)

# Example usage
# creat csv file
file_path = matches.group(1)+".csv"
f = open(file_path, 'w')
#creating the CSV file headers
f.write("Type,TC\n")
calculate_scene_frame_counts(video_file)
#print("TC of scence detected less then one frame:", scene_frame_counts)
f.close()
# Open a file in write mode (creates a new file if it doesn't exist)

