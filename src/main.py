import sys
from engine import Engine
from gui import ChatApp

if __name__ == "__main__":
    support_pygame = True

    # Create engine instance
    engine = Engine(support_pygame=support_pygame)
    
    # Initialize and run GUI
    app = ChatApp(engine, support_pygame=support_pygame)
    app.mainloop()