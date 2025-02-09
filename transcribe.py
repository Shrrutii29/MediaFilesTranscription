import os
import whisper
import subprocess

TRANSCRIPTIONS_DIR = "Transcriptions"

# Ensure that given directory exists
def directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Check if file contains audio or not
def has_audio(file_path):
    cmd = f'ffmpeg -i "{file_path}" 2>&1 | grep Audio'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return bool(result.stdout.strip())

# Recursively find all audio/video files in given folder
def find_mediafiles(folder_path):
    extensions = {'.mp3', '.wav', '.mp4', '.m4a', '.flac', '.ogg', '.mov', '.avi'}
    mediafiles = []
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                if has_audio(file_path):  
                    mediafiles.append(file_path)
                else:
                    print(f"Skipping file (No audio detected): {file_path}")
    
    return mediafiles

# Transcribes all media files in folder and save results in hierarchical structure same as audio/video files structure.
def transcribe_mediafiles(folder_path):
    model = whisper.load_model("tiny")
    mediafiles = find_mediafiles(folder_path)
    
    if not mediafiles:
        print("No valid media files found in given folder.")
        return
    
    for file_path in mediafiles:
        print(f"Processing: {file_path}")
        result = model.transcribe(file_path)
        transcription = result['text']
        
        relative_path = os.path.relpath(file_path, folder_path) 
        transcription_folder = os.path.join(TRANSCRIPTIONS_DIR, os.path.dirname(relative_path))  
        directory_exists(transcription_folder)
        
        base_filename = os.path.basename(file_path)
        output_file = os.path.join(transcription_folder, f"{base_filename}.txt")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcription)
        
        print(f"Transcription saved: {output_file}")

if __name__ == "__main__":
    folder_path = input("Enter the folder name containing media files: ")
    if os.path.exists(folder_path):
        transcribe_mediafiles(folder_path)
    else:
        print("Invalid folder name. Please check and try again.")
