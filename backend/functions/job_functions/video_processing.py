from moviepy.editor import VideoFileClip
import numpy as np
import subprocess
import librosa
import cv2
import av

def corruption_check(video):
    check = av.open(video)
    if not check or not check.streams.video:
        return False
    return True
    
def video_processing(video, temp_video):
    output_path = video
    command = [
        'ffmpeg',
        "-hwaccel", "cuda",
        '-i', temp_video,
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-b:v', '2M',
        '-vf', 'yadif',
        output_path
    ]
    subprocess.run(command)
    return True

def audio_profile(video, path):
    video = VideoFileClip(video)
    audio = f'{path}.wav'
    video.audio.write_audiofile(audio, codec='pcm_s16le')
    y, sr = librosa.load(audio, sr=None, mono=True)
    volume = np.mean(librosa.feature.rms(y=y))
    audio_json = {
        'duration': video.duration,
        'sample_rate': sr,
        'channels': y.shape[0],
        'average_volume': volume,
    }
    return audio_json

def visual_profile(video, is_thumbnail, serial, thumbnail_location=''):
    image_added = False
    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        return False
    
    total_saturation = 0
    frame_count = 0
    if is_thumbnail is False:
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        target_frame = int(total_frames * 0.1)
        thumbnail_path = f'{thumbnail_location}{serial}.jpg'
    
        ret, frame = cap.read()
        if not ret:
            return False
        
        cv2.imwrite(thumbnail_path, frame)
        image_added = True
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        
    ret, frame = cap.read()
    if not ret:
        return False
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    saturation = np.sum(hsv[:, :, 1])
    total_saturation += saturation
    frame_count += 1
    
    average_saturation = total_saturation / frame_count if frame_count > 0 else 0
    
    visual_profile_data = {
    'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) != 0 else 0,
    'resolution': (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))),
    'frame_rate': cap.get(cv2.CAP_PROP_FPS),
    'average_saturation': average_saturation
    }
    
    return visual_profile_data, image_added
