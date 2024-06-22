from openai import OpenAI
import os
import pwd
import subprocess

os.environ['OPENAI_API_KEY'] = "sk-proj-wGlurmBriyif87iiMWAMT3BlbkFJ1xhf2FL0Pgpknd0v1koU"


def speech_to_text(input_file_path):
    client = OpenAI()
    audio_file = open(input_file_path, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )
    return transcription.text


def text_to_speech(input_text, output_file_path):
    client = OpenAI()
    response = client.audio.speech.create(
        model="tts-1",
        voice="echo",
        input=input_text
    )
    response.stream_to_file(output_file_path)


def play_audio(file_path):

    # Drop privileges by setting UID and GID
    def drop_privileges():
        os.setgid(user_gid)
        os.setuid(user_uid)

    # drop sudo privleges to run as regular
    user_info = pwd.getpwnam('pi')
    user_uid = user_info.pw_uid
    user_gid = user_info.pw_gid
    user_home = user_info.pw_dir

    # Prepare the environment for the user
    env = os.environ.copy()
    env['HOME'] = user_home
    env['USER'] = 'pi'
    env['LOGNAME'] = 'pi'
    env['XDG_RUNTIME_DIR'] = f"/run/user/{user_uid}"
    subprocess.run(f"mpg123 -f -200000 {file_path}", preexec_fn=drop_privileges, env=env, shell=True)
