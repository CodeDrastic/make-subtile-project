#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 15 15:32:01 2025
@author:ardh

"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget,QFileDialog

from moviepy import VideoFileClip
from deep_translator import GoogleTranslator
import whisper

class subtitle_creator(QMainWindow):
    def __init__(self):
        super().__init__()
        
        #main window properties 
        self.setWindowTitle(" subtile creator")   # the title of the application
        self.setGeometry(0, 0, 600, 400)      #the dimensions x, y, width, height
        
        self.initUI()    #makes the code cleaner by initializing the UI elements and keep the difined under the function
        
    def initUI(self):
        
        #create the main widget on top of which other widgets are placed
        centralwidget = QWidget()                       
        self.setCentralWidget(centralwidget)     
        layout = QVBoxLayout()
        centralwidget.setLayout(layout)
        
        #create video selection lable
        self.video_label = QLabel('select Video file')
        layout.addWidget(self.video_label)
        
        #creates the video input lable
        self.video_input = QLineEdit(self)                        #why self
        self.video_input.setPlaceholderText("video files only")
        self.video_input.setReadOnly(True)               #this makes the line edit readable but not editable
        layout.addWidget(self.video_input)
        
        #creates the button so that may browse the file explorer 
        self.file_button = QPushButton("Browse", self)
        self.file_button.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.file_button)
        
        #name the subtitle file
        self.subtitle_name = QLabel("Enter Subtitle File Name (.srt):")
        layout.addWidget(self.subtitle_name)
        
        self.output_input = QLineEdit(self)
        layout.addWidget(self.output_input)
        
        #start button for the subtitle creation process
        self.start_button = QPushButton("Generate Subtitles", self)
        self.start_button.clicked.connect(self.generate_subtitles)
        layout.addWidget(self.start_button)
        
        # Output Status
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
    
    #saving the chosen file    
    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Video File", "", "Video Files (*.mp4 *.mkv *.avi)")
        if file_path:
            self.video_input.setText(file_path)
    def generate_subtitles(self):
        video_path = self.video_input.text()
        subtitle_filename = self.output_input.text().strip()
        
        if not video_path:
           self.status_label.setText("Please select a video file.")
           return

        if not subtitle_filename.endswith(".srt"):
           self.status_label.setText("Invalid subtitle filename. It must end with .srt")
           return

        try:
           # Step 1: Extract Audio
           audio_path = self.extract_audio(video_path)

           # Step 2: Transcribe Audio
           transcription_segments = self.transcribe_with_whisper(audio_path)

           # Step 3 and 4: Translate & Write Subtitles
           self.write_srt(transcription_segments, subtitle_filename)

           self.status_label.setText("Subtitles created successfully!")

        except Exception as e:
           self.status_label.setText(f"Error: {str(e)}")     #the e catches the error that is given in python 
           
           
    def extract_audio(self, video_path, audio_path="audio.wav"):
        clip = VideoFileClip(video_path)
        clip.audio.write_audiofile(audio_path)
        return audio_path

    def transcribe_with_whisper(self, audio_path):
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result['segments']

    def translate_text(self, text, target_lang = "en"):
        
        translated_text = GoogleTranslator(source="auto",target_lang="en" ).translate(text)
        
        return translated_text

    def format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        sec = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        return f"{hours:02}:{minutes:02}:{sec:02},{milliseconds:03}"

    def write_srt(self, transcription_segments, output_path, target_lang="en"):
        with open(output_path, 'w', encoding="utf-8") as f:
            for i, segment in enumerate(transcription_segments):
                start_time = segment["start"]
                end_time = segment["end"]
                text = segment["text"]
                translated_text = self.translate_text(text, target_lang="en")

                f.write(f"{i+1}\n")
                f.write(f"{self.format_time(start_time)} --> {self.format_time(end_time)}\n")
                f.write(text+"\n")
                f.write(translated_text + "\n\n")       
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = subtitle_creator()
    window.show()
    sys.exit(app.exec_())