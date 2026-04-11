from RealtimeSTT import AudioToTextRecorder

if __name__ == '__main__':
    recorder = AudioToTextRecorder(input_device_index = 2)

    with AudioToTextRecorder() as recorder:
        print(recorder.text())

    """
    recorder.start()
    input("Press Enter to stop recording...")
    recorder.stop()
    print("Transcription: ", recorder.text())"""