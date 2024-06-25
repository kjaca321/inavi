import struct
import wave
import time
from datetime import datetime

import pvporcupine
from pvrecorder import PvRecorder

ACCESS_KEY = 'PICOVOICE KEY HERE'
KEYWORD = 'INAVI'
AUDIO_DEVICE_INDEX = -1
RECORD_TIME = 3.0


def listen_for_user(audio_path):

    # initialize porcupine with our custom wake word 'INAVI'
    porcupine = pvporcupine.create(
        access_key=ACCESS_KEY,
        library_path=None,
        model_path=None,
        keyword_paths=['/home/pi/TurboPi/robot_control/gpt_modules/assets/robot_raspi.ppn'],
        sensitivities=[0.5])

    # setup recorder to capture user voice
    recorder = PvRecorder(
        frame_length=porcupine.frame_length,
        device_index=AUDIO_DEVICE_INDEX)
    recorder.start()

    # setup wav file to write to
    wav_file = wave.open(audio_path, "w")
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(16000)

    print('Listening ...')

    # setup flags
    write_flag = False
    write_start_ts = None
    prev_pcm = None

    # keep listening till wake word is heard, record 3 seconds after wake word (adjustable)
    while (not write_flag) or (time.time() - write_start_ts < RECORD_TIME):
        # read from recorder
        pcm = recorder.read()
        if not prev_pcm:
            prev_pcm = pcm
        result = porcupine.process(pcm)

        # check if wake word is in result, if so save that frame and set appropriate flags
        if result >= 0:
            if not write_flag:
                write_flag = True
                write_start_ts = time.time()
                if prev_pcm:
                    wav_file.writeframes(struct.pack("h" * len(prev_pcm), *prev_pcm))
            print('[%s] Detected %s' % (str(datetime.now()), KEYWORD))

        # write to wav file if wake word has been detected
        if write_flag and wav_file is not None:
            wav_file.writeframes(struct.pack("h" * len(pcm), *pcm))

        prev_pcm = pcm

    # cleanup
    recorder.delete()
    porcupine.delete()
    wav_file.close()

    print("Command received")

