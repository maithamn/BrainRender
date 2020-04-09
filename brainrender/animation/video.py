from vtkplotter import Video
import datetime
from tqdm import tqdm
import os
import numpy as np
from tempfile import TemporaryDirectory
from termcolor import cprint

from vtkplotter import screenshot

from brainrender.animation.video_utils import save_videocap_to_video, get_cap_from_images_folder

class BasicVideoMaker:
    """
        Wrapper around vtkplotter Video class to facilitate the creation of videos from
        brainrender scenes.

        Use kwargs to specify:
            - save_fld: folder where to save video
            - save_name: video name
            - video_format: e.g. mp4
            - duration: video duration in seconds
            - niters: number of iterations (frames) when creating the video
            - fps: framerate of video
    """
    def __init__(self, scene, **kwargs):
        self.scene = scene
        
        # Parss keyword argumets
        self.save_fld = kwargs.pop('save_fld', self.scene.output_videos)
        self.save_name = kwargs.pop('save_name', 'brainrender_video_'+
                            f'_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}')
        self.video_format = kwargs.pop('video_format', 'mp4')

        self.duration = kwargs.pop('duration', 3)
        self.niters = kwargs.pop('niters', 60)
        self.fps = kwargs.pop("fps", 30)

    def parse_kwargs(self, **kwargs):
        """
            Parses arguments for video creation
            Use kwargs to specify:
                - save_fld: folder where to save video
                - save_name: video name
                - video_format: e.g. mp4
                - duration: video duration in seconds
                - niters: number of iterations (frames) when creating the video
                - fps: framerate of video

            Arguments not specified in kwargs will be assigned default values
        """
        self.save_fld = kwargs.pop('save_fld', self.save_fld)
        self.save_name = kwargs.pop('save_name', self.save_name)
        self.video_format = kwargs.pop('video_format', self.video_format)
        self.video_format.replace(".", "")
        self.duration = kwargs.pop('duration', None)
        self.niters = int(kwargs.pop('niters', self.niters))
        self.fps = int(kwargs.pop("fps", self.fps))

        self.complete_save_path = os.path.join(self.save_fld, self.save_name+"."+self.video_format)


    def initialize_video_creation(self):
        self.tmp_dir = TemporaryDirectory()
        self.frames = []

    def add_frame(self):
        frame_path = os.path.join(self.tmp_dir.name, str(len(self.frames))+".png")
        screenshot(filename=frame_path)
        self.frames.append(frame_path)

    def make_frames(self, azimuth=0, elevation=0, roll=0):
        """
        Creates the frames of a video, called from make_video. 
        To make a custom video with more complex animation, subclass BasicVideoMaker and specify a new make_frames method

        :param azimuth: integer, specify the rotation in degrees per frame on the relative axis. (Default value = 0)
        :param elevation: integer, specify the rotation in degrees per frame on the relative axis. (Default value = 0)
        :param roll: integer, specify the rotation in degrees per frame on the relative axis. (Default value = 0)
        """
        cprint("Creating frames", 'green', attrs=['bold'])
        for i in tqdm(range(self.niters)):
            # render the scene first
            self.scene.render(interactive=False, video=True)  

            # Move the camera
            self.scene.plotter.camera.Elevation(elevation)
            self.scene.plotter.camera.Azimuth(azimuth)
            self.scene.plotter.camera.Roll(roll) 

            # Add frame
            self.add_frame()

    def close(self):
        # Check final duration and fps
        if self.duration is not None:
            self.fps = np.floor(len(self.frames) / float(self.duration))
            print("Recalculated video FPS to", self.fps)
        else:
            self.fps = int(self.fps)

        # Make video
        cprint("Saving video to file", 'green', attrs=['bold'])
        cap = get_cap_from_images_folder(self.tmp_dir.name)
        save_videocap_to_video(cap, self.complete_save_path, self.video_format, fps=self.fps)

        # Remove saved screenshots
        self.tmp_dir.cleanup()

        cprint(f"\nVideo creation completed, file saved at {self.complete_save_path}", 'green', attrs=['bold'])


    def make_video(self, azimuth=0, elevation=0, roll=0, **kwargs):
        """
        Creates a video using user defined parameters

        :param azimuth: integer, specify the rotation in degrees per frame on the relative axis. (Default value = 0)
        :param elevation: integer, specify the rotation in degrees per frame on the relative axis. (Default value = 0)
        :param roll: integer, specify the rotation in degrees per frame on the relative axis. (Default value = 0)
        :param kwargs: use to change destination folder, video name, fps, duration ... check 'self.parse_kwargs' for details. 
        """
        self.parse_kwargs(**kwargs)
        self.initialize_video_creation()

        curdir = os.getcwd() # we need to cd to the folder where the video is saved and then back here
        os.chdir(self.save_fld)
        cprint(f"Saving video in {self.save_fld}. Video name: {self.save_name}.{self.video_format} - {self.niters} frames", 'green', attrs=['bold'])

        # Check arguments are ok
        if os.path.isfile(self.complete_save_path):
            cprint(f"A video file with path {self.complete_save_path} exists alread", 'red', attrs=['bold'])
            yn = ""
            while yn.lower() != "y":
                yn = input("If you continue you'll overwrite it [y/n]: ")
                if yn.lower() == "n":
                    print("Exiting...")
                    return

        if 'mp4' not in self.video_format and "avi" not in self.video_format: raise ValueError("Currently only .mp4 video format is supported")

        if self.duration is not None and self.fps is not None:
            print("An argument was passed for both duration and fps, but can't specify both at the same time"+
                    "The fps argument will be ignored.")

        # Render the scene first [to set the camera]
        self.scene.render(interactive=False, verbose=False)

        # Make frames
        self.make_frames(azimuth=azimuth, elevation=elevation, roll=roll)

        # merge the recorded frames and crate a video
        self.close()  

