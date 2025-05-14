"""Main entry point for the Stadium Builder application."""
import tkinter as tk
from services.file_service import FileService
from services.item_service import ItemService
from services.optimizer import OptimizerService
from ui.main_window import MainWindow

def main():
    """Initialize and run the application."""
    # Create services
    file_service = FileService("items.json")
    item_service = ItemService(file_service)
    optimizer_service = OptimizerService()
    
    # Create and run main window
    window = MainWindow(item_service, optimizer_service)
    window.run()

if __name__ == "__main__":
    main() 