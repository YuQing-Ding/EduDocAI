import tkinter as tk
import os
import sys
from os import path
from tkinter import filedialog, messagebox
import openai
import threading
from PIL import Image, ImageTk
import docx
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import PyPDF2
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', path.dirname(path.abspath(__file__)))
    return path.join(base_path, relative_path)
class NumberEntry(tk.Entry):
    def __init__(self, master=None, **kwargs):
        tk.Entry.__init__(self, master, **kwargs)
        vcmd = self.register(self.validate_input)
        self.config(validate="key", validatecommand=(vcmd, "%P"))

    def validate_input(self, new_text):
        if new_text == "" or new_text.isdigit() and 5 <= int(new_text) <= 999:
            return True
        return False

class PDFProcessor:
    def __init__(self):
        self.text = ""

    def extract_text(self, pdf_path):
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                self.text += page.extract_text()

    def get_text(self):
        return self.text

class DocumentProcessor:
    def __init__(self):
        self.pdf_text = ""
        self.txt_text = ""

    def extract_text_from_pdf(self, pdf_path):
        pdf_processor = PDFProcessor()
        pdf_processor.extract_text(pdf_path)
        self.pdf_text = pdf_processor.get_text()

    def extract_text_from_txt(self, txt_path):
        with open(txt_path, 'r', encoding='utf-8') as txt_file:
            self.txt_text = txt_file.read()

    def get_pdf_text(self):
        return self.pdf_text

    def get_txt_text(self):
        return self.txt_text

class ChatGPTInterface:
    def __init__(self, api_key):
        openai.api_key = api_key

    def generate_response(self, pdf_input, txt_input, question_count):
        messages = [
            {"role": "system", "content": "College instructor"},
            {"role": "user", "content": f"Generate {question_count} exam question(s) based on the [Course Outcomes and Objectives] part from document and random type from the template ,the template of the exam question style has been provided\nTemplate of the exam question style:{txt_input}\nDocument:{pdf_input}"}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages
        )
        return response.choices[0].message['content']

def get_api_key():
    openai_key = "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"  # Your OpenAI Key!
    return openai_key

def show_loading_prompt():
    loading_window = tk.Toplevel(root)
    loading_window.title("QuizEngineAI")
    loading_window.attributes('-topmost', True)
    loading_window.overrideredirect(True)

    loading_label = tk.Label(loading_window, text="QuizEngine is reading and planning the document.\nPlease wait...")
    loading_label.pack(padx=10, pady=10)

    loading_window.update_idletasks()  # Update the window to make sure it's displayed
    loading_window.geometry(f"+{root.winfo_x() + root.winfo_width()//2 - loading_window.winfo_width()//2}+{root.winfo_y() + root.winfo_height()//2 - loading_window.winfo_height()//2}")
    return loading_window

def process_files_and_generate_response():
    global selected_pdf_filename
    global global_question_count
    pdf_file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    txt_file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])

    if pdf_file_path and txt_file_path:
        selected_pdf_filename = os.path.basename(pdf_file_path)
        selected_pdf_filename = selected_pdf_filename.split('_')[0]
        root.update()
        loading_window = show_loading_prompt()

        api_key = get_api_key()
        doc_processor = DocumentProcessor()
        doc_processor.extract_text_from_pdf(pdf_file_path)
        doc_processor.extract_text_from_txt(txt_file_path)
        extracted_pdf_text = doc_processor.get_pdf_text()
        extracted_txt_text = doc_processor.get_txt_text()
        
        chat_gpt_interface = ChatGPTInterface(api_key)
        response = chat_gpt_interface.generate_response(extracted_pdf_text, extracted_txt_text, global_question_count.get())

        response_text.config(state=tk.NORMAL)
        response_text.delete('1.0', tk.END)
        response_text.insert(tk.END, response)
        response_text.config(state=tk.DISABLED)
        

        loading_window.destroy()
class PrototypeDisclaimer:
    def __init__(self, root):
        self.root = root
        self.disclaimer_window = tk.Toplevel(root)
        self.disclaimer_window.title("Prototype Disclaimer")
        self.disclaimer_window.attributes('-topmost', True)
        self.disclaimer_window.overrideredirect(True)
        
        disclaimer_label = tk.Label(self.disclaimer_window, text="Warning!!!\nThis is a prototype version.\nSome strange failures may occur.\n(e.g. unstable software, offensive language in generated results).", fg="red", font=("Helvetica", 14, "bold"))
        disclaimer_label.pack(padx=10, pady=10)
        
        continue_button = tk.Button(self.disclaimer_window, text="Continue", command=self.close_disclaimer)
        continue_button.pack(pady=10)

        self.disclaimer_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - self.disclaimer_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - self.disclaimer_window.winfo_height()) // 2
        self.disclaimer_window.geometry(f"+{x}+{y}")

    def close_disclaimer(self):
        self.disclaimer_window.destroy()
        self.root.deiconify()  # Show the main UI window after closing the disclaimer window

# Create GUI window
root = tk.Tk()
root.title("ReaderEngineAI - Beta V0.01")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - 300) // 2
y = (screen_height - 200) // 2
root.iconphoto(True, tk.PhotoImage(file=resource_path('icon.png')))
original_image = Image.open(resource_path('nscc_sa.png'))
resized_image = original_image.resize((128, 128))
global_question_count = tk.IntVar()
global_question_count.set(5)  # Set a default value
disclaimer = PrototypeDisclaimer(root)
root.withdraw()  # Hide the main UI window initially

# Create GUI components
choose_files_button = tk.Button(root, text="Select PDF and TXT files", command=process_files_and_generate_response)
response_text = tk.Text(root, wrap=tk.WORD, state=tk.DISABLED)
programmer_label = tk.Label(root, text="PROGRAMMER: YUQING (SCOTT) DING")
project_manager_label = tk.Label(root, text="PRODUCT MANAGER: DAVIS BOUDREAU")
copyright_label = tk.Label(root, text="© 2023 NSCC - NOVA SCOTIA COMMUNITY COLLEGE")
logo_image = ImageTk.PhotoImage(resized_image)
logo_label = tk.Label(root, image=logo_image)
question_count_label = tk.Label(root, text="Question Count (Min = 5):")
question_count_entry = NumberEntry(root, textvariable=global_question_count)
# Layout GUI components
choose_files_button.pack(pady=10)
response_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
programmer_label.pack(side="bottom", anchor="se", padx=10)
project_manager_label.pack(side="bottom", anchor="se", padx=10)
copyright_label.pack(side="bottom", anchor="se", padx=10, pady=10)
logo_label.pack(side="bottom", anchor="sw")
question_count_label.pack(pady=5)
question_count_entry.pack(pady=5)

# GUI Main Loop
root.geometry("500x600+{}+{}".format(x, y))
root.mainloop()
