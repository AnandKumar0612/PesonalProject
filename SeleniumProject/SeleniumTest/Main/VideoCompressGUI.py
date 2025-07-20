import os
import ffmpeg
import tkinter as tk
from tkinter import filedialog, messagebox


def compress_video(video_full_path, size_upper_bound, two_pass=True, filename_suffix='_cps'):
    filename, extension = os.path.splitext(video_full_path)
    extension = '.mp4'
    output_file_name = filename + filename_suffix + extension

    total_bitrate_lower_bound = 11000
    min_audio_bitrate = 32000
    max_audio_bitrate = 256000
    min_video_bitrate = 100000

    try:
        probe = ffmpeg.probe(video_full_path)
        duration = float(probe['format']['duration'])
        audio_bitrate = float(next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)['bit_rate'])
        target_total_bitrate = (size_upper_bound * 1024 * 8) / (1.073741824 * duration)

        if target_total_bitrate < total_bitrate_lower_bound:
            messagebox.showerror("Error", "Bitrate is too low. Compression stopped.")
            return False

        best_min_size = (min_audio_bitrate + min_video_bitrate) * (1.073741824 * duration) / (8 * 1024)
        if size_upper_bound < best_min_size:
            messagebox.showwarning("Warning", f"Low quality! Recommended min size: {int(best_min_size)} KB")

        if 10 * audio_bitrate > target_total_bitrate:
            audio_bitrate = max(min_audio_bitrate, min(target_total_bitrate / 10, max_audio_bitrate))

        video_bitrate = target_total_bitrate - audio_bitrate
        if video_bitrate < 1000:
            messagebox.showerror("Error", "Video bitrate too low! Compression stopped.")
            return False

        i = ffmpeg.input(video_full_path)
        status_label.config(text="Compressing... Please wait.", fg="blue")
        root.update_idletasks()

        if two_pass:
            ffmpeg.output(i, os.devnull, **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}) \
                .overwrite_output().run()
            ffmpeg.output(i, output_file_name,
                          **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}) \
                .overwrite_output().run()
        else:
            ffmpeg.output(i, output_file_name,
                          **{'c:v': 'libx264', 'b:v': video_bitrate, 'c:a': 'aac', 'b:a': audio_bitrate}) \
                .overwrite_output().run()

        if os.path.getsize(output_file_name) <= size_upper_bound * 1024:
            messagebox.showinfo("Success", f"Compression successful! Output: {output_file_name}")
            status_label.config(text=f"Done! Saved at {output_file_name}", fg="green")
            return output_file_name
        else:
            return compress_video(output_file_name, size_upper_bound)

    except FileNotFoundError as e:
        messagebox.showerror("Error", "FFmpeg not found! Please install FFmpeg.")
        return False


# ------------------- Tkinter GUI -------------------
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov;*.mkv")])
    if file_path:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, file_path)


def start_compression():
    video_path = entry_path.get()
    size_limit = entry_size.get()

    if not video_path:
        messagebox.showerror("Error", "Please select a video file.")
        return
    if not size_limit.isdigit():
        messagebox.showerror("Error", "Please enter a valid file size in MB.")
        return

    size_kb = int(size_limit) * 1000
    two_pass = var_two_pass.get()

    status_label.config(text="Starting compression...", fg="black")
    root.update_idletasks()

    output_file = compress_video(video_path, size_kb, two_pass)
    if output_file:
        status_label.config(text=f"Compression complete: {output_file}", fg="green")
    else:
        status_label.config(text="Compression failed!", fg="red")


# ------------------- GUI Layout -------------------
root = tk.Tk()
root.title("Video Compressor")
root.geometry("500x300")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(pady=20)

# File selection
tk.Label(frame, text="Select Video File:").grid(row=0, column=0, sticky="w")
entry_path = tk.Entry(frame, width=40)
entry_path.grid(row=0, column=1, padx=5)
tk.Button(frame, text="Browse", command=select_file).grid(row=0, column=2)

# Size input
tk.Label(frame, text="Max Size (MB):").grid(row=1, column=0, sticky="w")
entry_size = tk.Entry(frame, width=10)
entry_size.grid(row=1, column=1, padx=5)

# Two-pass checkbox
var_two_pass = tk.BooleanVar(value=True)
chk_two_pass = tk.Checkbutton(frame, text="Enable Two-Pass Encoding", variable=var_two_pass)
chk_two_pass.grid(row=2, columnspan=3, pady=10)

# Start button
tk.Button(frame, text="Compress Video", command=start_compression, bg="blue", fg="white").grid(row=3, columnspan=3,
                                                                                               pady=10)

# Status label
status_label = tk.Label(root, text="", fg="black")
status_label.pack()

root.mainloop()
