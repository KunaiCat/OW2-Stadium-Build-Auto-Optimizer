import sys
import subprocess
from services.file_service import FileService
from services.item_service import ItemService
from services.optimizer import OptimizerService
from ui.main_menu import MainMenu


def ensure_requirements():
    try:
        # Try importing a key dependency (replace 'somepackage' with a real one)
        import tkinter  # or any other package you use
    except ImportError:
        print("Missing dependencies. Installing requirements...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed. Please re-run the script.")
        sys.exit(0)


def main():
    ensure_requirements()
    
    file_service = FileService()
    item_service = ItemService(file_service)
    optimizer_service = OptimizerService()
    
    # Create and run main window
    app = MainMenu(item_service, optimizer_service)
    app.run()


if __name__ == "__main__":
    main() 