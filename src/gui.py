import customtkinter as ctk
import threading
from engine import Engine
from sim.core.event_bus import EventBus, EventType
from log import Logger

class ChatApp(ctk.CTk):
    def __init__(self, engine: Engine):
        super().__init__()
        self.engine = engine
        
        # Configure window
        self.title("CozyJelly Brain Simulator")
        self.geometry("1300x850")
        
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Grid layout (0: Sidebar, 1: Main Area)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        
        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="JELLY BRAIN", font=ctk.CTkFont(size=24, weight="bold"))
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
        self.web_search_var = ctk.BooleanVar(value=False)
        self.web_search_check = ctk.CTkCheckBox(
            self.sidebar_frame,
            text="Support Web Search", 
            variable=self.web_search_var, 
            command=self.toggle_serper_input,
            font=ctk.CTkFont(size=12)
        )
        self.web_search_check.grid(row=5, column=0, padx=20, pady=(5, 5), sticky="w")
        
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
        self.status_label.grid(row=10, column=0, padx=20, pady=20)
        
        # Left Views Frame (6 Views) - Scrollable to prevent squishing
        self.left_views_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.left_views_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=(20, 10))
        
        # Configure layout for the 6 views inside the frame
        self.left_views_frame.grid_columnconfigure(0, weight=1)
        self.left_views_frame.grid_columnconfigure(1, weight=1)
        
        # Create the 6 text views with explicit heights for scroll container
        self.biometrics_view = self.create_text_view(self.left_views_frame, "BIOMETRICS & MATRIX", 0, 0, height=220)
        self.world_detail_view = self.create_text_view(self.left_views_frame, "World Detail", 0, 1, height=220)
        self.agent_chat_log_view = self.create_text_view(self.left_views_frame, "agent chat log", 1, 0, height=250)
        self.world_log_view = self.create_text_view(self.left_views_frame, "world log", 1, 1, height=250)
        self.ascii_map_view = self.create_text_view(self.left_views_frame, "ascii map", 2, 0, columnspan=2, height=350)
        self.system_log_view = self.create_text_view(self.left_views_frame, "system log", 3, 0, columnspan=2, height=200)

        # Input Area
        self.input_container = ctk.CTkFrame(self, fg_color="transparent")
        self.input_container.grid(row=1, column=1, sticky="ew", padx=25, pady=(0, 20))
        self.input_container.grid_columnconfigure(0, weight=1)
        
        self.user_input = ctk.CTkEntry(self.input_container, placeholder_text="Message AI...", height=50)
        self.user_input.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.user_input.bind("<Return>", lambda e: self.on_send())
        
        self.send_button = ctk.CTkButton(self.input_container, text="Send", width=100, height=50, command=self.on_send)
        self.send_button.grid(row=0, column=1)
        
        # Handle close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize state
        self.user_input.configure(state="disabled", placeholder_text="Auto Play Mode - Input Disabled")
        self.send_button.configure(state="disabled")
        
        # Subscribe to Event Bus for headless decoupling
        self.event_bus = EventBus()
        self.event_bus.subscribe(EventType.BIOMETRICS_UPDATED, self.refresh_biometrics)
        self.event_bus.subscribe(EventType.WORLD_DETAIL_UPDATED, self.refresh_world_detail)
        self.event_bus.subscribe(EventType.AGENT_CHAT_LOG_APPENDED, self.append_agent_chat_log)
        self.event_bus.subscribe(EventType.WORLD_LOG_APPENDED, self.append_world_log)
        self.event_bus.subscribe(EventType.ASCII_MAP_UPDATED, self.refresh_ascii_map)
        self.event_bus.subscribe(EventType.SYSTEM_LOG_APPENDED, self.append_system_log)

        # Initialize Engine
        self.engine.start()
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
            
            # Start simulation immediately
            model_name = self.model_spinner.get()
            if model_name != "Select a model...":
                self.log_to_chat("System", "Auto Play sequence initiated...")
                threading.Thread(target=self.engine.run, args=(model_name, "Auto Start"), daemon=True).start()
            else:
                self.log_to_chat("System", "Auto Play failed: No model selected.")
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
        self.agent_chat_log_view.configure(state="normal")
        self.agent_chat_log_view._textbox.insert("end", "AI: ")
        self.last_ai_msg_index = self.agent_chat_log_view._textbox.index("end-1c")
        self.agent_chat_log_view._textbox.insert("end", "Thinking...\n\n")
        self.agent_chat_log_view.configure(state="disabled")
        self.agent_chat_log_view.see("end")

    def _update_thinking_text(self, text):
        if not self.last_ai_msg_index:
            return
            
        self.agent_chat_log_view.configure(state="normal")
        # Find where "AI: " ends
        line_start = self.agent_chat_log_view._textbox.index(f"{self.last_ai_msg_index} linestart")
        pass

    def finalize_ai_message(self, content):
        self.agent_chat_log_view.configure(state="normal")
        # Clear the "Thinking..." or previous stream
        # Delete the last line and insert final content
        self.agent_chat_log_view._textbox.delete("end-3c linestart", "end-1c")
        self.agent_chat_log_view._textbox.insert("end", f"AI: {content}\n\n")
        
        self.agent_chat_log_view.configure(state="disabled")
        self.agent_chat_log_view.see("end")

    def reenable_input(self):
        self.user_input.configure(state="normal")
        self.send_button.configure(state="normal")
        self.user_input.focus()

    def log_to_chat(self, sender, message):
        if sender == "System":
            self.append_system_log(f"{sender}: {message}")
        else:
            self.append_agent_chat_log(f"{sender}: {message}")

    def create_text_view(self, parent, title, row, column, columnspan=1, height=200):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=column, columnspan=columnspan, sticky="nsew", padx=5, pady=5)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=0)
        frame.grid_columnconfigure(0, weight=1)
        
        label = ctk.CTkLabel(
            frame, 
            text=title.upper(), 
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
            text_color="#3B82F6"
        )
        label.grid(row=0, column=0, padx=10, pady=(5, 2), sticky="ew")
        
        font_family = "Consolas" if any(x in title.lower() for x in ["map", "biometrics"]) else "Inter"
        textbox = ctk.CTkTextbox(
            frame, 
            font=ctk.CTkFont(family=font_family, size=14),
            wrap="none",
            height=height
        )
        
        # Adjust line spacing for better visibility and readability
        if "map" in title.lower():
            # For ASCII map, keep line spacing smaller to preserve grid aspect ratio
            textbox._textbox.configure(spacing1=2, spacing2=2, spacing3=2)
        else:
            # For general text logs, increase line spacing to make it highly legible
            textbox._textbox.configure(spacing1=5, spacing2=5, spacing3=5)

        textbox.grid(row=1, column=0, padx=5, pady=0, sticky="nsew")
        textbox.configure(state="disabled")
        
        # Bind Ctrl + MouseWheel to zoom font size
        textbox.bind("<Control-MouseWheel>", lambda event, tb=textbox: self.on_zoom(event, tb))
        
        # Horizontal scrollbar linked to textbox
        h_scrollbar = ctk.CTkScrollbar(frame, orientation="horizontal", height=12)
        h_scrollbar.grid(row=2, column=0, padx=5, pady=(2, 5), sticky="ew")
        
        h_scrollbar.configure(command=textbox._textbox.xview)
        textbox._textbox.configure(xscrollcommand=h_scrollbar.set)
        
        return textbox

    def on_zoom(self, event, textbox):
        font = textbox.cget("font")
        if not font:
            return "break"
        
        current_size = font.cget("size")
        if event.delta > 0:
            new_size = current_size + 1
        else:
            new_size = current_size - 1
            
        if 8 <= new_size <= 45:
            font.configure(size=new_size)
            
        return "break"

    def _update_text_view(self, textbox, text, scroll_to_end=False):
        if text is None:
            text = ""
        current_text = textbox.get("1.0", "end-1c")
        if current_text == text:
            return
            
        try:
            x_pos = textbox._textbox.xview()
            y_pos = textbox._textbox.yview()
        except Exception:
            x_pos, y_pos = None, None

        textbox.configure(state="normal")
        # Standard delete and insert on the underlying tkinter Text widget to avoid CustomTkinter insert bugs
        textbox._textbox.delete("1.0", "end")
        textbox._textbox.insert("1.0", text)
        textbox.configure(state="disabled")
        
        if scroll_to_end:
            textbox.see("end")
        elif x_pos is not None and y_pos is not None:
            try:
                textbox._textbox.xview_moveto(x_pos[0])
                textbox._textbox.yview_moveto(y_pos[0])
            except Exception:
                pass

    def _append_text_view(self, textbox, text):
        if text is None:
            text = ""
        try:
            y_pos = textbox._textbox.yview()
            is_at_bottom = y_pos[1] >= 0.95
        except Exception:
            is_at_bottom = True

        textbox.configure(state="normal")
        textbox._textbox.insert("end", text + "\n")
        textbox.configure(state="disabled")
        
        if is_at_bottom:
            textbox.see("end")

    def refresh_biometrics(self, text):
        self.after(0, lambda: self._update_text_view(self.biometrics_view, text))

    def refresh_world_detail(self, text):
        self.after(0, lambda: self._update_text_view(self.world_detail_view, text))

    def append_agent_chat_log(self, text):
        self.after(0, lambda: self._append_text_view(self.agent_chat_log_view, text))

    def append_world_log(self, text):
        self.after(0, lambda: self._append_text_view(self.world_log_view, text))

    def refresh_ascii_map(self, text):
        self.after(0, lambda: self._update_text_view(self.ascii_map_view, text))

    def append_system_log(self, text):
        self.after(0, lambda: self._append_text_view(self.system_log_view, text))

    def on_closing(self):
        Logger.log("Stopping engine and closing application...")
        self.engine.stop()
        self.destroy()

if __name__ == "__main__":
    # Test block
    eng = Engine()
    app = ChatApp(eng)
    app.mainloop()
