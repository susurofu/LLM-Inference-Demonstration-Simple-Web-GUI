# file with tkinter GUI to set_up demonstration
from pathlib import Path
import re
import threading

import tkinter as tk
from tkinter import messagebox  # Required for alert pop-ups
from tkinter.simpledialog import askstring
from tkinter import ttk

from cloudflare_installs.install_script_mac import _install_cloudflared_mac
from cloudflare_installs.install_script_linux import _install_cloudflared_linux
from set_access_password import _set_password
from run_server_from_gui import start_demo

class SetupForm(tk.Tk):
    def __init__(self):
        super().__init__()
    
        self.title("Setup of Demonstration Interface")
        self.geometry("850x550")

        # Configure layout using the grid manager
        self.columnconfigure(1, weight=1)

        self.set_instructions_button = tk.Button(self, text="Instructions", command=self.set_instructions)
        self.set_instructions_button.grid(row=1, column=0, padx=15, pady=20)

        self.cloudlare_btn = tk.Button(self, text="Cloudflared", command=self.set_cloudlare)
        self.cloudlare_btn.grid(row=1, column=1, padx=15, pady=20)

        self.set_model_btn = tk.Button(self, text="Set model (ollama)", command=self.set_model) # expand this and add selection of the model from list
        self.set_model_btn.grid(row=1, column=2, padx=15, pady=20)

        self.password_setup_btn = tk.Button(self, text="Set password", command=self.set_password) # expand this and add selection of the model from list
        self.password_setup_btn.grid(row=2, column=1, padx=15, pady=20)

        self.run_server_btn = tk.Button(self, text="Start server", command=self.run_server) # expand this and add selection of the model from list
        self.run_server_btn.grid(row=2, column=2, padx=15, pady=20)




    def set_instructions(self):
        instruction = askstring(title="Instructions setting", prompt="Enter instructions to display at the web page here. You can also modify them in backend/instruction.txt. In this case, keep this input empty and modify the instruction.txt.")
        if instruction is not None:
            backend_dir = Path("backend")#
            instruction_path = backend_dir / 'instruction.txt'
            with open (instruction_path, 'w', encoding="utf-8") as f:
                f.write(instruction)


    def set_cloudlare(self):
        popup = tk.Toplevel(self)
        popup.title("Cloudfalred settings")
        popup.geometry("300x150")

        def install_cloudflared_mac():
            _install_cloudflared_mac()
                    
        
        def install_cloudflared_linux():
            _install_cloudflared_linux()

        install_cloudlare_mac = tk.Button(popup, text="Install for MacOS", width=10, command=install_cloudflared_mac)
        install_cloudlare_mac.pack(side="left", padx=20, expand=True)
        install_cloudlare_linux = tk.Button(popup, text="Install for Linux", width=10, command=install_cloudflared_linux)
        install_cloudlare_linux.pack(side="left", padx=20, expand=True)

    def set_model(self):
        popup = tk.Toplevel(self)
        popup.title("Choose Ollama model")
        popup.geometry("300x150")

        import ollama

        ollama_list = ollama.list()

        choices = [model.model for model in ollama_list.models]

        combo = ttk.Combobox(
            popup,
            values=choices,
            state="readonly"
        )
        combo.set("Choose a model")
        combo.pack(pady=20)

        def write_selected_model():
                    model_name = combo.get()
                    model_write_path = Path("backend") / "model.txt"
                    if model_name not in ["", "Choose a model"]:
                        with open (model_write_path, "w", encoding='utf-8') as f:
                            f.write(model_name)
                        messagebox.showinfo("Notification", "Model set successfully")
                    else:
                        messagebox.showwarning("Notification", "No model selected")

        set_model_btn = tk.Button(popup, text="Select model", width=10, command=write_selected_model)
        set_model_btn.pack(side="left", padx=20, expand=True)

    def set_password(self):
        popup = tk.Toplevel(self)
        popup.title("Password setting")
        popup.geometry("300x180")

        password_entry_1 = tk.Entry(popup, show="*")
        password_entry_1.pack(pady=10)

        password_entry_2 = tk.Entry(popup, show="*")
        password_entry_2.pack(pady=10)

        def check_password():
            pswd_1 = password_entry_1.get()
            pswd_2 = password_entry_2.get()

            if pswd_1 == pswd_2 and pswd_1 != "":
                _set_password(pswd_1)
                messagebox.showinfo(
                    "Notification",
                    "Password has been selected"
                )
                popup.destroy()
            else:
                messagebox.showwarning(
                    "Notification",
                    "Input passwords do not match or password is empty"
                )

        pswd_input_btn = tk.Button(
            popup,
            text="Set password",
            width=12,
            command=check_password
        )
        pswd_input_btn.pack(pady=10)

    def run_server(self):
        popup = tk.Toplevel(self)
        popup.title("Server")
        popup.geometry("450x220")

        status_label = tk.Label(
            popup,
            text="Server is stopped"
        )
        status_label.pack(pady=10)

        url_entry = tk.Entry(
            popup,
            width=55
        )
        url_entry.pack(pady=10)

        def start_server():
            start_btn.config(state="disabled")
            status_label.config(text="Starting server...")

            def worker():
                try:
                    url, uvicorn_process, cloudflare_process = start_demo()

                    # Store processes in the class
                    self.uvicorn_process = uvicorn_process
                    self.cloudflare_process = cloudflare_process
                    self.server_url = url

                    # Tkinter UI updates should happen on main thread
                    self.after(
                        0,
                        lambda: server_started(url)
                    )

                except Exception as e:
                    self.after(
                        0,
                        lambda: server_error(str(e))
                    )

            threading.Thread(
                target=worker,
                daemon=True
            ).start()

        def server_started(url):
            status_label.config(
                text="Server is running"
            )

            url_entry.delete(0, tk.END)
            url_entry.insert(0, url)

            stop_btn.config(state="normal")

            messagebox.showinfo(
                "Server",
                f"Server started successfully:\n\n{url}"
            )

        def server_error(error):
            status_label.config(
                text="Failed to start server"
            )

            start_btn.config(state="normal")

            messagebox.showerror(
                "Server error",
                error
            )

        def stop_server():
            try:
                if hasattr(self, "cloudflare_process"):
                    if self.cloudflare_process.poll() is None:
                        self.cloudflare_process.terminate()

                if hasattr(self, "uvicorn_process"):
                    if self.uvicorn_process.poll() is None:
                        self.uvicorn_process.terminate()

                status_label.config(
                    text="Server is stopped"
                )

                url_entry.delete(0, tk.END)

                start_btn.config(state="normal")
                stop_btn.config(state="disabled")

            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Could not stop server:\n{e}"
                )

        def copy_url():
            url = url_entry.get()

            if url:
                self.clipboard_clear()
                self.clipboard_append(url)

                messagebox.showinfo(
                    "URL",
                    "Connection URL copied to clipboard."
                )

        start_btn = tk.Button(
            popup,
            text="Start server",
            width=15,
            command=start_server
        )
        start_btn.pack(pady=5)

        stop_btn = tk.Button(
            popup,
            text="Stop server",
            width=15,
            command=stop_server,
            state="disabled"
        )
        stop_btn.pack(pady=5)

        copy_btn = tk.Button(
            popup,
            text="Copy URL",
            width=15,
            command=copy_url
        )
        copy_btn.pack(pady=5)

if __name__ == "__main__":
    app = SetupForm()
    app.mainloop()
