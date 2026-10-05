import imageio_ffmpeg
import shutil
import os
import sys

def fix_ffmpeg():
    original_path = imageio_ffmpeg.get_ffmpeg_exe()
    
    # Target directory is the virtual environment's Scripts folder
    venv_scripts = os.path.dirname(sys.executable)
    target_path = os.path.join(venv_scripts, "ffmpeg.exe")
    
    if not os.path.exists(target_path):
        print(f"Copying FFmpeg from {original_path} to {target_path}...")
        shutil.copy2(original_path, target_path)
        print("Done! FFmpeg is now globally available in the virtual environment.")
    else:
        print("FFmpeg is already patched.")

if __name__ == "__main__":
    fix_ffmpeg()
