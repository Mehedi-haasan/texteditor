import tkinter as tk
from tkinter import Toplevel, Listbox, messagebox, simpledialog, filedialog
import difflib
import re
import os
from tkinter.scrolledtext import ScrolledText
import subprocess
from PIL import Image, ImageTk
import pytesseract
import speech_recognition as sr
import threading

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
class AdvancedBanglaTextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("বাংলা সহায়ক")
        self.root.geometry("1000x700")

        self.dictionary_file_path = "D:\\TextEditor\\data\\words.txt"
        self.sentences_file_path = "D:\\TextEditor\\data\\sentences.txt"

        # Text Area
        self.text_area = ScrolledText(self.root, wrap='word', undo=True, font=("Nirmala UI", 12))
        self.text_area.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

        # Status Bar
        self.status_bar = tk.Label(self.root, text="Developing by Rabiul Islam student of CSE", anchor="w", relief=tk.SUNKEN, font=("Nirmala UI", 10))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Menu Bar
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # File Menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Save As", command=self.save_as_file)
        self.file_menu.add_command(label="Print", command=self.print_file, accelerator="Ctrl+P")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit_editor, accelerator="Ctrl+Q")

        # Edit Menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Undo", command=self.text_area.edit_undo, accelerator="Ctrl+Z")
        self.edit_menu.add_command(label="Redo", command=self.text_area.edit_redo, accelerator="Ctrl+Y")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut", command=self.cut_text, accelerator="Ctrl+X")
        self.edit_menu.add_command(label="Copy", command=self.copy_text, accelerator="Ctrl+C")
        self.edit_menu.add_command(label="Paste", command=self.paste_text, accelerator="Ctrl+V")

        # Tools Menu
        self.tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Tools", menu=self.tools_menu)
        self.tools_menu.add_command(label="বানান পরিক্ষা করুন", command=self.check_spelling)
        self.tools_menu.add_command(label="ভূল শব্দ পরিবর্তন করুন", command=self.manual_correction)
        self.tools_menu.add_command(label="স্বয়ংক্রিয় সংশোধন করুন", command=self.auto_correct)
        self.tools_menu.add_separator()
        self.tools_menu.add_command(label="নির্দিষ্ট শব্দ পরিবর্তন করুন", command=self.find_replace)
        self.tools_menu.add_separator()
        self.tools_menu.add_command(label="ছবি থেকে লেখা আনুন", command=self.open_image_for_ocr)
        self.tools_menu.add_separator()
        self.tools_menu.add_command(label="কন্ঠধনি দিয়ে লেখুন", command=self.start_voice_typing)
        self.tools_menu.add_command(label="কন্ঠধনি বন্ধ করুন", command=self.stop_voice_typing)
        
        self.voice_typing_active = False
        # Data Containers
        self.bangla_words = set()
        self.bangla_sentences = []

        # Sentence Suggestions
        self.text_area.bind('<KeyRelease>', self.show_suggestions)
        self.suggestion_box = None

        # Highlighting Configurations
        self.text_area.tag_configure("highlight", background="yellow", foreground="black")
        self.text_area.tag_configure("misspelled", foreground="red")

        # Bindings for Shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-q>', lambda e: self.exit_editor())
        self.root.bind('<Control-p>', lambda e: self.print_file())
        self.root.bind('<Control-f>', lambda e: self.find_replace())

        # Load Data
        self.load_dictionary()
        self.load_sentences()

    # File Menu Operations
    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.status_bar.config(text="New file opened.")

    def open_file(self):
        file_path = filedialog.askopenfilename(title="Open File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, file.read())
                self.status_bar.config(text=f"Opened file: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")

    def save_file(self):
        file_path = filedialog.asksaveasfilename(title="Save File", defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.text_area.get(1.0, tk.END).strip())
                self.status_bar.config(text=f"File saved: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def save_as_file(self):
        self.save_file()

    def print_file(self):
        try:
            content = self.text_area.get(1.0, tk.END).strip()
            with open("temp_print.txt", "w", encoding="utf-8") as file:
                file.write(content)
            subprocess.run(["notepad.exe", "/p", "temp_print.txt"], check=True)
            os.remove("temp_print.txt")
            self.status_bar.config(text="File printed successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print: {str(e)}")

    def exit_editor(self):
        self.root.quit()

    # Edit Menu Operations
    def cut_text(self):
        self.text_area.event_generate("<<Cut>>")
        self.status_bar.config(text="Cut text.")

    def copy_text(self):
        self.text_area.event_generate("<<Copy>>")
        self.status_bar.config(text="Copied text.")

    def paste_text(self):
        self.text_area.event_generate("<<Paste>>")
        self.status_bar.config(text="Pasted text.")

    # Dictionary and Sentence Operations
    def load_dictionary(self):
        try:
            with open(self.dictionary_file_path, 'r', encoding='utf-8') as file:
                self.bangla_words = set(line.strip() for line in file if line.strip())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dictionary: {str(e)}")

    def load_sentences(self):
        try:
            with open(self.sentences_file_path, 'r', encoding='utf-8') as file:
                self.bangla_sentences = [line.strip() for line in file if line.strip()]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sentences: {str(e)}")
    def find_replace(self):
        
        def replace_text():
            find_text = find_entry.get()
            replace_text = replace_entry.get()
            content = self.text_area.get(1.0, tk.END).strip()
            new_content = content.replace(find_text, replace_text)
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, new_content)
            messagebox.showinfo("পরিবর্তন", f"বাংলা শব্দ '{find_text}' থেকে '{replace_text}'পরিবর্তিত হয়েছে")

        find_replace_dialog = Toplevel(self.root)
        find_replace_dialog.title("নির্দিষ্ট শব্দ পরিবর্তন করুন")

        tk.Label(find_replace_dialog, text="কোন শব্দ করতে চানঃ").grid(row=0, column=0, padx=5, pady=5)
        find_entry = tk.Entry(find_replace_dialog, width=30)
        find_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(find_replace_dialog, text="যে শব্দে পরিবর্তন করতে চানঃ").grid(row=1, column=0, padx=5, pady=5)
        replace_entry = tk.Entry(find_replace_dialog, width=30)
        replace_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(find_replace_dialog, text="সব শব্দ পরিবর্তন করুন", command=replace_text).grid(row=2, column=0, columnspan=2, pady=10)
    
    
    
    
    def check_spelling(self):
        try:
            content = self.text_area.get(1.0, tk.END).strip()
            words = content.split()
            misspelled = [word for word in words if word not in self.bangla_words]

            self.text_area.tag_remove("misspelled", "1.0", tk.END)
            if not misspelled:
                messagebox.showinfo("শব্দ পরিক্ষা", "অভিনন্দন! কোন ভূল শব্দ পাওয়া যায় নি")
                return

            for word in misspelled:
                start_pos = "1.0"
                while True:
                    start_pos = self.text_area.search(word, start_pos, stopindex=tk.END)
                    if not start_pos:
                        break
                    end_pos = f"{start_pos}+{len(word)}c"
                    self.text_area.tag_add("misspelled", start_pos, end_pos)
                    start_pos = end_pos

            messagebox.showinfo("বানান পরিক্ষা", "দুঃখিত! ভূল বানান খুঁজে পাওয়া গেছে। লাল রঙ করা শব্দ গুলো ভূল বানান বলে বিবেচিত হয়েছে")
        except Exception as e:
            messagebox.showerror("Error", f"Error in spell check: {str(e)}")

    # Sentence Suggestions and Predictions
    def show_suggestions(self, event=None):
        self.highlight_last_sentence()
        content = self.text_area.get(1.0, tk.END).strip()
        last_sentence = self.extract_last_sentence(content)
        if not last_sentence or not self.bangla_sentences:
            if self.suggestion_box:
                self.suggestion_box.destroy()
            return
        suggestions = difflib.get_close_matches(last_sentence, self.bangla_sentences, n=5, cutoff=0.3)
        if suggestions:
            self.display_suggestions(suggestions)
    
    def manual_correction(self):
        """Manually correct misspelled words."""
        content = self.text_area.get(1.0, tk.END).strip()
        words = content.split()
        corrected_content = []

        for word in words:
            if word in self.bangla_words:
                corrected_content.append(word)
            else:
                suggestions = difflib.get_close_matches(word, self.bangla_words, n=5)
                replacement = self.get_user_choice(word, suggestions)
                corrected_content.append(replacement if replacement else word)

        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, " ".join(corrected_content))
        messagebox.showinfo("ভূল শব্দ পরিবর্তন", "ভূল শব্দ গুলো সঠিক ভাবে পরিবর্তিত হয়েছে ")

    
    
    def auto_correct(self):
        """Automatically replace misspelled words with the closest suggestions."""
        content = self.text_area.get(1.0, tk.END).strip()
        words = content.split()
        corrected_content = []

        for word in words:
            if word in self.bangla_words:
                corrected_content.append(word)
            else:
                suggestion = difflib.get_close_matches(word, self.bangla_words, n=1)
                corrected_content.append(suggestion[0] if suggestion else word)

        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, " ".join(corrected_content))
        messagebox.showinfo("স্বয়ংক্রিয় সংশোধন", "স্বয়ংক্রিয় সংশোধন সম্পূর্ন হয়েছে")
    
    
    def extract_last_sentence(self, text):
        sentences = re.split(r'[।,?!]', text)
        return sentences[-1].strip() if sentences else ""

    def calculate_suggestion_box_position(self):
        cursor_position = self.text_area.index(tk.INSERT)
        bbox = self.text_area.bbox(cursor_position)
        if bbox:
            x_offset = self.root.winfo_x() + self.text_area.winfo_x() + bbox[0]+30
            y_offset = self.root.winfo_y() + self.text_area.winfo_y() + bbox[1] + bbox[3]+40
            return f"300x150+{x_offset}+{y_offset}"
        else:
            x = self.root.winfo_x() + self.text_area.winfo_x()
            y = self.root.winfo_y() + self.text_area.winfo_height()
            return f"300x150+{x}+{y}"

    def display_suggestions(self, suggestions):
        if self.suggestion_box:
            self.suggestion_box.destroy()
        self.suggestion_box = Toplevel(self.root)
        self.suggestion_box.wm_overrideredirect(True)
        self.suggestion_box.geometry(self.calculate_suggestion_box_position())
        self.suggestion_box.resizable(False, False)
        listbox = Listbox(self.suggestion_box, font=("Nirmala UI", 12))
        listbox.pack(fill=tk.BOTH, expand=1)
        for suggestion in suggestions:
            listbox.insert(tk.END, suggestion)
        listbox.bind("<<ListboxSelect>>", lambda event: self.apply_suggestion(event, listbox))

    def apply_suggestion(self, event, listbox):
        """Apply the selected suggestion and fetch the next sentence prediction."""
        selection = listbox.curselection()
        if selection:
           selected_suggestion = listbox.get(selection[0])
        
        # Get the current content and last sentence
           content = self.text_area.get(1.0, tk.END).strip()
           last_sentence = self.extract_last_sentence(content)

           if last_sentence:
            # Replace the last sentence with the selected suggestion
              updated_content = re.sub(rf"{re.escape(last_sentence)}$", selected_suggestion, content)
           else:
            # If there's no last sentence, just append the selected suggestion
              updated_content = content + " " + selected_suggestion

        # Update the text area with the new content
           self.text_area.delete(1.0, tk.END)
            
           self.text_area.insert(tk.END, updated_content + " ")

        # Fetch the next sentence suggestions
           next_suggestions = self.get_next_sentence_suggestions(selected_suggestion)

           if next_suggestions:
                self.display_suggestions(next_suggestions)
           else:
               if self.suggestion_box:
                  self.suggestion_box.destroy()
                  self.suggestion_box = None


    def get_next_sentence_suggestions(self, current_sentence):
        """Generate the next sentence suggestions based on the selected sentence."""
    # Ensure that the current sentence exists
        if not current_sentence or not self.bangla_sentences:
           return []

    # Find potential "next sentences" in the list
        next_sentences = []
        for i, sentence in enumerate(self.bangla_sentences):
          if sentence.strip() == current_sentence.strip():
            # Add the next sentence, if it exists
            if i + 1 < len(self.bangla_sentences):
                next_sentences.append(self.bangla_sentences[i + 1])

    # Return up to 5 suggestions
        return next_sentences[:5]


    
    def get_user_choice(self, word, suggestions):
    
        choice = None

        def on_select(event):
            nonlocal choice
            choice = listbox.get(listbox.curselection())
            dialog.destroy()

        dialog = Toplevel(self.root)
        dialog.title(f"ভূল শব্দ '{word}' পরিবর্তন করুন")
        tk.Label(dialog, text=f" '{word}' এর পরিবর্তে কোন শব্দটি ব্যাবহার করতে চান,তা নির্বাচন করুন").pack(pady=5)

        listbox = Listbox(dialog, selectmode=tk.SINGLE, font=("Nirmala UI", 12))
        listbox.pack(pady=5, padx=10)

        for suggestion in suggestions:
            listbox.insert(tk.END, suggestion)

        listbox.bind('<<ListboxSelect>>', on_select)

        def manual_entry():
            nonlocal choice
            choice = simpledialog.askstring("নিজের শব্দ ব্যবহার করুন", f" '{word}' এর পরিবর্তে শব্দটি লিখুন")
            dialog.destroy()

        tk.Button(dialog, text="নিজের শব্দ ব্যবহার করুন", command=manual_entry).pack(pady=5)

        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)

        return choice
    
    
    
    def highlight_last_sentence(self):
        self.text_area.tag_remove("highlight", "1.0", tk.END)
        content = self.text_area.get(1.0, tk.END).strip()
        last_sentence = self.extract_last_sentence(content)
        if last_sentence:
            start_idx = content.rfind(last_sentence)
            if start_idx != -1:
                start_line, start_char = self.text_area.index(f"1.0 + {start_idx} chars").split(".")
                end_idx = f"{start_line}.{int(start_char) + len(last_sentence)}"
                self.text_area.tag_add("highlight", f"{start_line}.{start_char}", end_idx)
    
    
    def extract_bangla_text(self, image_path):
        
        try:
            # Open the image
            image = Image.open(image_path)

            # Perform OCR using Tesseract with the Bangla language
            text = pytesseract.image_to_string(image, lang="ben+eng")

            return text
        except Exception as e:
            # Handle errors (e.g., file not found, Tesseract issues)
            return f"Error: {str(e)}"
    
    
    
    
    
    def open_image_for_ocr(self):
        """
        Open a file dialog to select an image, extract the Bangla text, and display it in the text area.
        """
        image_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        if image_path:
            try:
                # Extract Bangla text from the selected image
                text = self.extract_bangla_text(image_path)

                # Clear the text area and insert the extracted text
                self.text_area.insert(tk.END, "\n" + text)

                # Update status bar
                self.status_bar.config(text="Developing by Rabiul Islam student of CSE")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to extract text: {str(e)}")

    def start_voice_typing(self):
        if self.voice_typing_active:
            messagebox.showinfo("Voice Typing", "Voice typing is already active.")
            return

        self.voice_typing_active = True
        self.status_bar.config(text="Voice Typing Started. Say 'stop' to stop.")
        threading.Thread(target=self.voice_typing, daemon=True).start()

    def stop_voice_typing(self):
        self.voice_typing_active = False
        self.status_bar.config(text="Voice Typing Stopped.")
        

    def voice_typing(self):
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)

            while self.voice_typing_active:
                try:
                    self.status_bar.config(text="Listening for voice input...")
                    audio = recognizer.listen(source, timeout=5)

                    # Recognize speech in Bangla
                    text = recognizer.recognize_google(audio, language="bn-BD")
                    self.text_area.insert(tk.END, text + " ")
                    self.text_area.yview(tk.END)

                    if "stop" in text.lower():
                        self.stop_voice_typing()

                except sr.UnknownValueError:
                    self.status_bar.config(text="Developing by Rabiul Islam student of CSE")
                except sr.RequestError as e:
                    self.status_bar.config(text=f"Speech recognition error: {e}")
                    self.stop_voice_typing()
                    break
                except Exception as e:
                    self.status_bar.config(text=f"Error: {e}")
                    self.stop_voice_typing()
                    break

    

if __name__ == "__main__":
    root = tk.Tk()
    editor = AdvancedBanglaTextEditor(root)
    root.mainloop()
