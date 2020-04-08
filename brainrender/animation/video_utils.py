import cv2
import os

# ------------------------ Create opencv video writers ----------------------- #
def open_cvwriter(filepath, w=None, h=None, framerate=None, format=".mp4", iscolor=False):
    """
        Creats an instance of cv.VideoWriter to write frames to video using python opencv

        :param filepath: str, path to file to save
        :param w,h: width and height of frame in pixels
        :param framerate: fps of output video
        :param format: video format
        :param iscolor: bool, set as true if images are rgb, else false if they are gray
    """
    try:
        if "avi" in format:
            fourcc = cv2.VideoWriter_fourcc("M", "J", "P", "G")  
        else:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        videowriter = cv2.VideoWriter(filepath, fourcc, framerate, (w, h), iscolor)
    except:
        raise ValueError("Could not create videowriter")
    else:
        return videowriter

# --------------------- Manipulate opened video captures --------------------- #
def cap_set_frame(cap, frame_number):
    """
        Sets an opencv video capture object to a specific frame
    """
    cap.set(1, frame_number)

def get_cap_selected_frame(cap, show_frame):
    """ 
        Gets a frame from an opencv video capture object to a specific frame
    """
    cap_set_frame(cap, show_frame)
    ret, frame = cap.read()

    if not ret:
        return None
    else:
        return frame


def get_video_params(cap):
    """ 
        Gets video parameters from an opencv video capture object
    """
    if isinstance(cap, str):
        cap = cv2.VideoCapture(cap)

    frame = get_cap_selected_frame(cap, 0)
    if frame.shape[1] == 3:
        is_color = True
    else: is_color = False
    cap_set_frame(cap, 0)

    nframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    return nframes, width, height, fps, is_color


# --------------------------- Create video captures -------------------------- #

def get_cap_from_file(videopath):
    """
        Opens a video file as an opencv video capture
    """
    try:
        cap = cv2.VideoCapture(videopath)
    except Exception as e:
        raise ValueError("Could not open video at: " + videopath + f"\n {e}")

    ret, frame = cap.read()
    if not ret:
        raise ValueError("Something went wrong, can't read form video: " + videopath)
    else:
        cap_set_frame(cap, 0)
    return cap


def get_cap_from_images_folder(folder):
    if not os.path.isdir(folder):
        raise ValueError(f"Folder {folder} doesn't exist")
    if not os.listdir(folder):
        raise ValueError(f"Folder {folder} is empty")

    # Create video capture
    cap = cv2.VideoCapture(os.path.join(folder, "%1d.png"))

    # Check all went well
    ret, frame = cap.read()
    if not ret:
        raise ValueError("Something went wrong, can't read form folder: " + folder)
    else:
        cap_set_frame(cap, 0)
    return cap




# ---------------------- Create video from video capture --------------------- #
def save_videocap_to_video(cap, savepath, fmt, fps=30):
    """
        Saves the content of a videocapture opencv object to a file
    """
    if "." not in fmt: fmt = "."+fmt
    # Creat video writer
    nframes, width, height, _, _ = get_video_params(cap)
    writer = open_cvwriter(savepath, w=width, h=height, framerate=fps, format=fmt, iscolor=True)

    # Save frames
    while True:
        ret, frame = cap.read()
        if not ret: break

        writer.write(frame)

    # Release everything if job is finished
    cap.release()
    writer.release()


