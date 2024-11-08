import os
import asyncio
import edge_tts
import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import tempfile
import threading
import sys

# Initialize pygame for audio playback
pygame.mixer.init()

# Create the Tkinter window
root = tk.Tk()
root.title("Chuyển văn bản thành âm thanh")
root.geometry("1500x680")  # Tăng kích thước form (chiều ngang rộng hơn)
root.configure(bg='#2b2b2b')  # Màu nền của form (dark mode)

# Edge TTS voice options
voice_options = {
    "vi_male": "vi-VN-NamMinhNeural",   
    "vi_female": "vi-VN-HoaiMyNeural",   
    "en_male": "en-US-GuyNeural",       
    "en_female": "en-US-JennyNeural"     
}

MAX_TEXT_LENGTH = 10000  

async def preview_audio(text, voice):
    if not text.strip():
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập văn bản để chuyển thành âm thanh!")
        return

    if len(text) > MAX_TEXT_LENGTH:
        show_warning_and_stop()
        text = text[:MAX_TEXT_LENGTH]  

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_path = temp_file.name
    temp_file.close()  

    communicate = edge_tts.Communicate(text, voice=voice)
    await communicate.save(temp_path)

    pygame.mixer.music.load(temp_path)
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.unload()
    os.remove(temp_path)

async def save_audio(text, voice):
    # Kiểm tra nếu văn bản rỗng
    if not text.strip():
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập văn bản để lưu thành âm thanh!")
        return

    if len(text) > MAX_TEXT_LENGTH:
        show_warning_and_stop()
        text = text[:MAX_TEXT_LENGTH]  

    file_path = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("Audio files", "*.mp3")])
    if file_path:
        communicate = edge_tts.Communicate(text, voice=voice)
        await communicate.save(file_path)
        messagebox.showinfo("Thành công", "Xuất file âm thanh thành công!")

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
            if len(text) > MAX_TEXT_LENGTH:
                text = text[:MAX_TEXT_LENGTH] 
                show_warning_and_stop()
            text_input.delete(1.0, tk.END)
            text_input.insert(tk.END, text)

def run_async(func, *args):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(func(*args))

def show_warning_and_stop():
    def stop_app():
        root.quit()  
    
    warning_window = tk.Toplevel(root)
    warning_window.title("Cảnh báo")
    warning_window.geometry("500x150")
    warning_window.configure(bg='#2b2b2b')

    tk.Label(warning_window, text="Văn bản quá dài! tắt thông báo này để rút ngắn văn bản.", fg="#ffffff", bg="#2b2b2b", font=("Arial", 12)).pack(pady=10)
    
   
tk.Label(root, text="Nhập văn bản:", fg="#ffffff", bg="#2b2b2b", font=("Arial", 14)).pack(pady=10)

text_input = tk.Text(root, wrap=tk.WORD, height=12, font=("Arial", 12), bg="#333333", fg="#ffffff", insertbackground="white")
text_input.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)  # Để Text widget tự động mở rộng chiều ngang

tk.Label(root, text="Ngôn ngữ và giọng nói:", fg="#ffffff", bg="#2b2b2b", font=("Arial", 14)).pack(pady=10)
voice_var = tk.StringVar(value="vi_male")
tk.Radiobutton(root, text="Tiếng Việt - Nam", variable=voice_var, value="vi_male", fg="#ffffff", bg="#2b2b2b", selectcolor="#2b2b2b", font=("Arial", 12)).pack(anchor="w", padx=30)
tk.Radiobutton(root, text="Tiếng Việt - Nữ", variable=voice_var, value="vi_female", fg="#ffffff", bg="#2b2b2b", selectcolor="#2b2b2b", font=("Arial", 12)).pack(anchor="w", padx=30)
tk.Radiobutton(root, text="Tiếng Anh - Nam", variable=voice_var, value="en_male", fg="#ffffff", bg="#2b2b2b", selectcolor="#2b2b2b", font=("Arial", 12)).pack(anchor="w", padx=30)
tk.Radiobutton(root, text="Tiếng Anh - Nữ", variable=voice_var, value="en_female", fg="#ffffff", bg="#2b2b2b", selectcolor="#2b2b2b", font=("Arial", 12)).pack(anchor="w", padx=30)


button_style = {"fg": "#ffffff", "bg": "#4CAF50", "font": ("Arial", 12), "activebackground": "#45a049"}
tk.Button(root, text="Xem trước", command=lambda: threading.Thread(target=run_async, args=(preview_audio, text_input.get(1.0, tk.END), voice_options[voice_var.get()])).start(), **button_style).pack(pady=10, padx=30)
tk.Button(root, text="Xuất file âm thanh", command=lambda: threading.Thread(target=run_async, args=(save_audio, text_input.get(1.0, tk.END), voice_options[voice_var.get()])).start(), **button_style).pack(pady=10, padx=30)
tk.Button(root, text="Mở file văn bản", command=open_file, **button_style).pack(pady=10, padx=30)

root.mainloop()
