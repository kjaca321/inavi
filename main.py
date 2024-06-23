import os
import json

from modules.listener import listen_for_user
from modules.voice_apis import speech_to_text, text_to_speech, play_audio
from modules.function_chooser import choose_function
from modules.vision_understanding import describe_view
from modules.motor_controls import move_ahead, turn_robot

USER_VOICE_FILE = '/robot_control/modules/assets/user_voice.wav'
GPT_VOICE_FILE = '/robot_control/modules/assets/gpt_voice.wav'
CAM_PIC_FILE = '/robot_control/modules/assets/cam_view.png'


if __name__ == "__main__":

    while True:

        # use picovoice with wake word to listen to for user
        listen_for_user(USER_VOICE_FILE)

        # use openai speech to text to get this into text
        user_request = speech_to_text(USER_VOICE_FILE)

        # classify which function to call
        func = choose_function(user_request)

        # decide whether describing visually or motor movement
        if func.name == 'describe_view':
            # take image
            os.system('v4l2-ctl -d /dev/video4 -c auto_exposure=1')
            os.system('v4l2-ctl -d /dev/video4 -c exposure_time_absolute=500')
            os.system(f'ffmpeg -y -f v4l2 -input_format yuyv422 -video_size 1280x720 -i /dev/video4 -vframes 1 -q:v 2 {CAM_PIC_FILE}')
            
            # generate description, play converted audio
            scene_description = describe_view(CAM_PIC_FILE)
            text_to_speech(scene_description, GPT_VOICE_FILE)
            play_audio(GPT_VOICE_FILE)

        elif func.name == 'move_ahead':
            arguments_dict = json.loads(func.arguments)

            dist = 1 # default distance if none specified (meters)

            if 'distance' in arguments_dict:
                # reassign distance with given parameters
                dist = arguments_dict['distance']
                if arguments_dict['units'] == 'feet':
                    dist *= 0.3048 # convert feet to meters

            # move for given distance, avoiding obstacles
            move_ahead(dist)

        elif func.name == 'turn_robot':
            # turn robot for given angle
            turn_robot(func.arguments)
