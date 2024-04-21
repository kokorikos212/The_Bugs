import speech_recognition as sr 
import os 
from pydub import AudioSegment
from pydub.silence import split_on_silence

import pyaudio
import wave
import tkinter as tk
import threading

class AudioRecorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.is_recording = False

        self.r = sr.Recognizer()
       

    def start_recording(self):
        """ Start the recording stream and the recording loop. """
        self.stream = self.audio.open(format=self.FORMAT,
                                      channels=self.CHANNELS,
                                      rate=self.RATE,
                                      input=True,
                                      frames_per_buffer=self.CHUNK)
        self.is_recording = True
        self.frames = []
        print("Recording started...")
        threading.Thread(target=self.record_loop).start()

    def record_loop(self):
        """ Continuously capture audio data from the microphone while recording is active. """
        try:
            while self.is_recording:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                self.frames.append(data)
        except Exception as e:
            print(f"Error while recording: {e}")
            self.is_recording = False

    def stop_recording(self):
        """ Stop the recording stream and terminate the recording session. """
        if self.stream and self.is_recording:
            self.is_recording = False
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()
            self.record = self.save_recording()
            print("Recording stopped.")

    def save_recording(self):
        """ Save the recorded data to a WAV file. """
        try:
            wf = wave.open("output.wav", 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            # print("Recording saved as output.wav")
            return "output.wav"
        
        except Exception as e:
            print(f"Failed to save recording: {e}")

    def on_button_press(self):
        if not self.is_recording:
            self.start_recording()

    def on_button_release(self):
        if self.is_recording:
            self.stop_recording()

    def speech_model():
        path = "speech_feature/output.wav" 
    
    # a function that splits the audio file into chunks
    # and applies speech recognition
    def get_large_audio_transcription(self, path):
        """
        Splitting the large audio file into chunks
        and apply speech recognition on each of these chunks
        """
        print(f"__get_large_audio_transcription__{path}") 
        # create a speech recognition object
        # path = "SpeechSamples/rec1.wav" 
        # open the audio file using pydub
        sound = AudioSegment.from_wav(path)  
        # split audio sound where silence is 700 miliseconds or more and get chunks
        chunks = split_on_silence(sound,
            # experiment with this value for your target audio file
            min_silence_len = 500,
            # adjust this per requirement
            silence_thresh = sound.dBFS-14,
            # keep the silence for 1 second, adjustable as well
            keep_silence=500,
        )
        folder_name = "audio-chunks"
        # create a directory to store the audio chunks
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        whole_text = ""
        # process each chunk 
        for i, audio_chunk in enumerate(chunks, start=1):
            # export audio chunk and save it in
            # the `folder_name` directory.
            chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
            audio_chunk.export(chunk_filename, format="wav")
            # recognize the chunk
            with sr.AudioFile(chunk_filename) as source:
                audio_listened = self.r.record(source)
                # try converting it to text
                try:
                    text = self.r.recognize_google(audio_listened)
                except sr.UnknownValueError as e:
                    print("Error:", str(e))
                else:
                    text = f"{text.capitalize()}. "
                    print(chunk_filename, ":", text)
                    whole_text += text
        # return the text for all chunks detected
        return whole_text


def main():
    path = "output.wav"
    root = tk.Tk()
    root.title("Audio Recorder")

    recorder = AudioRecorder()
    # recorder.start_recording()
    
    button = tk.Button(root, text="Record", command=recorder.on_button_press)
    button.pack()

    button_stop = tk.Button(root, text="Stop", command=recorder.on_button_release)
    button_stop.pack()

    root.mainloop()
    
    u_said_text = recorder.get_large_audio_transcription(path)
    print(u_said_text) 

if __name__ == "__main__":
    main()
