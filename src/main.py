import sys

from engine import Engine
from gui import ChatApp

if __name__ == "__main__":
    # Create engine instance
    engine = Engine()

    # Initialize and run GUI
    app = ChatApp(engine)
    app.mainloop()
