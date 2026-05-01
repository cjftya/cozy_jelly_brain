import customtkinter as ctk
import threading
from engine import Engine
from log import Logger

class ChatApp(ctk.CTk):
    def __init__(self, engine: Engine):
        super().__init__()
        self.engine = engine
        
        # Configure window
        self.title("Iris AI Chat Simulator")
        self.geometry("1100x750")
        
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Grid layout (0: Sidebar, 1: Main)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="IRIS SIM", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))
        
        # API Key Section
        self.api_key_label = ctk.CTkLabel(self.sidebar_frame, text="Google API Key", font=ctk.CTkFont(size=13, weight="bold"))
        self.api_key_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.api_key_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Enter Google API Key...", show="*")
        self.api_key_entry.grid(row=2, column=0, padx=20, pady=(5, 10), sticky="ew")

        self.serper_key_label = ctk.CTkLabel(self.sidebar_frame, text="Serper API Key", font=ctk.CTkFont(size=13, weight="bold"))
        self.serper_key_label.grid(row=3, column=0, padx=20, pady=(5, 0), sticky="w")
        self.serper_key_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="Enter Serper API Key...", show="*")
        self.serper_key_entry.grid(row=4, column=0, padx=20, pady=(5, 10), sticky="ew")

        # Web Search Support
        self.web_search_var = ctk.BooleanVar(value=True)
        self.web_search_check = ctk.CTkCheckBox(
            self.sidebar_frame, 
            text="Support Web Search", 
            variable=self.web_search_var, 
            command=self.toggle_serper_input,
            font=ctk.CTkFont(size=12)
        )
        self.web_search_check.grid(row=5, column=0, padx=20, pady=(5, 15), sticky="w")
        
        # Model Selection Section
        self.model_label = ctk.CTkLabel(self.sidebar_frame, text="Select Model", font=ctk.CTkFont(size=13, weight="bold"))
        self.model_label.grid(row=6, column=0, padx=20, pady=(10, 0), sticky="w")
        
        initial_models = self.engine.get_model_list()
        if not initial_models:
            initial_models = ["Select a model..."]
            
        self.model_spinner = ctk.CTkOptionMenu(self.sidebar_frame, values=initial_models)
        self.model_spinner.grid(row=7, column=0, padx=20, pady=(5, 20), sticky="ew")
        
        # System Start Button
        self.start_button = ctk.CTkButton(
            self.sidebar_frame, 
            text="System Start", 
            command=self.on_system_start,
            font=ctk.CTkFont(weight="bold"),
            height=40
        )
        self.start_button.grid(row=8, column=0, padx=20, pady=10, sticky="ew")
        
        # Divider or status
        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="Ready", text_color="gray")
        self.status_label.grid(row=11, column=0, padx=20, pady=20)
        
        # Main Chat Area
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        self.chat_display = ctk.CTkTextbox(self.main_frame, font=ctk.CTkFont(size=14))
        self.chat_display.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 20))
        self.chat_display.configure(state="disabled")
        
        # Input Area
        self.input_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.input_container.grid(row=1, column=0, sticky="ew")
        self.input_container.grid_columnconfigure(0, weight=1)
        
        self.user_input = ctk.CTkEntry(self.input_container, placeholder_text="Message AI...", height=50)
        self.user_input.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.user_input.bind("<Return>", lambda e: self.on_send())
        
        self.send_button = ctk.CTkButton(self.input_container, text="Send", width=100, height=50, command=self.on_send)
        self.send_button.grid(row=0, column=1)
        
        # Handle close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize Engine
        self.engine.start(output_callback=self.on_engine_output)
        self.last_ai_msg_index = None

    def on_system_start(self):
        google_api_key = self.api_key_entry.get()
        serper_api_key = self.serper_key_entry.get()
        use_web_search = self.web_search_var.get()
        
        # Validation
        if not google_api_key:
            self.log_to_chat("System", "Please enter a valid Google API Key.")
            return
        
        if use_web_search and not serper_api_key:
            self.log_to_chat("System", "Web Search is enabled. Please enter a Serper API Key.")
            return
        
        try:
            self.engine.load(google_api_key, serper_api_key, use_web_search)
            self.status_label.configure(text="System Online", text_color="#4CAF50")
            self.log_to_chat("System", f"Engine loaded (Web Search: {'ON' if use_web_search else 'OFF'}). Ready to simulate.")
            
            # Refresh model list
            models = self.engine.get_model_list()
            if models:
                self.model_spinner.configure(values=models)
                self.model_spinner.set(models[0])
        except Exception as e:
            self.status_label.configure(text="Load Error", text_color="#F44336")
            self.log_to_chat("System", f"Error loading engine: {str(e)}")

    def toggle_serper_input(self):
        if self.web_search_var.get():
            self.serper_key_entry.configure(state="normal")
            self.serper_key_label.configure(text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        else:
            self.serper_key_entry.configure(state="disabled")
            self.serper_key_label.configure(text_color="gray")

    def on_send(self):
        prompt = self.user_input.get().strip()
        if not prompt:
            return
        
        self.user_input.delete(0, 'end')
        self.log_to_chat("User", prompt)
        
        model_name = self.model_spinner.get()
        if model_name == "Select a model...":
            self.log_to_chat("System", "Please select a model first.")
            return

        # Disable input while thinking
        self.user_input.configure(state="disabled")
        self.send_button.configure(state="disabled")
        
        # Start thinking thread
        threading.Thread(target=self.run_chat_logic, args=(model_name, prompt), daemon=True).start()

    def run_chat_logic(self, model_name, prompt):
        try:
            # First, prepare the AI message area
            self.after(0, self.prepare_ai_message)
            
            # Final response update
            content = self.engine.run(model_name, prompt)
            self.after(0, lambda: self.finalize_ai_message(content))
            
        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: self.log_to_chat("System", f"Execution error: {error_msg}"))
        finally:
            self.after(0, self.reenable_input)

    def prepare_ai_message(self):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", "AI: ")
        self.last_ai_msg_index = self.chat_display.index("end-1c")
        self.chat_display.insert("end", "Thinking...\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def on_engine_output(self, text, is_final=False):
        # Update the thinking status/spinner
        if self.last_ai_msg_index:
            self.after(0, lambda: self._update_thinking_text(text))

    def _update_thinking_text(self, text):
        if not self.last_ai_msg_index:
            return
            
        self.chat_display.configure(state="normal")
        # Find where "AI: " ends
        line_start = self.chat_display.index(f"{self.last_ai_msg_index} linestart")
        # We want to replace the text after "AI: " on that line
        # Simple way: delete from line_start + 4 chars to end of that line
        # But indices in tkinter can be tricky with line breaks.
        # Let's just append to the end for now if it's simpler, or find the specific line.
        
        # Find the line that starts with "AI: " and is near the end
        # For simplicity in this sim, we just replace the last "Thinking..." part
        # Actually, let's just use a more robust way to find the last AI response line
        pass

    def finalize_ai_message(self, content):
        self.chat_display.configure(state="normal")
        # Clear the "Thinking..." or previous stream
        # (This logic would be more complex for true streaming, but for a sim we can just replace)
        
        # Delete the last line and insert final content
        self.chat_display.delete("end-3c linestart", "end-1c")
        self.chat_display.insert("end", f"AI: {content}\n\n")
        
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def reenable_input(self):
        self.user_input.configure(state="normal")
        self.send_button.configure(state="normal")
        self.user_input.focus()

    def log_to_chat(self, sender, message):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"{sender}: {message}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def on_closing(self):
        Logger.log("Stopping engine and closing application...")
        self.engine.stop()
        self.destroy()

if __name__ == "__main__":
    # Test block
    eng = Engine()
    app = ChatApp(eng)
    app.mainloop()
