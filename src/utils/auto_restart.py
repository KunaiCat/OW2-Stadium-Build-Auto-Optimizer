"""File watcher utility for auto-reloading the application on code changes."""
import sys
import time
import os
import subprocess
import psutil
from threading import Timer, Thread, Event
import select

def get_src_dir():
    """Get the src directory path, handling both direct execution and import cases."""
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # If we're in utils/, go up one level to get to src/
    if os.path.basename(current_dir) == 'utils':
        return os.path.dirname(current_dir)
    
    # If we're already in src/, use current directory
    return current_dir

class FileWatcher:
    def __init__(self):
        self.process = None
        self.last_modified_times = {}
        self.src_dir = get_src_dir()
        self.update_file_times()
        self.restart_timer = None
        self.restart_app()
    
    def update_file_times(self):
        """Get modification times of all Python files in the src directory"""
        for root, _, files in os.walk(self.src_dir):
            for filename in files:
                if filename.endswith(('.py', '.pyw')):
                    filepath = os.path.join(root, filename)
                    try:
                        mtime = os.path.getmtime(filepath)
                        self.last_modified_times[filepath] = mtime
                    except OSError:
                        continue
    
    def check_for_changes(self):
        """Check if any Python files have been modified"""
        for root, _, files in os.walk(self.src_dir):
            for filename in files:
                if filename.endswith(('.py', '.pyw')):
                    filepath = os.path.join(root, filename)
                    try:
                        mtime = os.path.getmtime(filepath)
                        last_mtime = self.last_modified_times.get(filepath)
                        
                        if last_mtime is None or mtime > last_mtime:
                            print(f"\nChange detected in {os.path.relpath(filepath, self.src_dir)}")
                            self.last_modified_times[filepath] = mtime
                            return True
                    except OSError:
                        continue
        return False
    
    def schedule_restart(self):
        """Schedule a restart after 15 seconds, with countdown and Enter-to-skip."""
        # Cancel any existing scheduled restart
        if self.restart_timer:
            self.restart_timer.cancel()

        print("\nWaiting 15 seconds for changes to settle... (press Enter to reload immediately)")
        skip_event = Event()

        def wait_for_enter():
            # Use select for non-blocking input
            while not skip_event.is_set():
                if sys.stdin in select.select([sys.stdin], [], [], 1)[0]:
                    _ = sys.stdin.readline()
                    skip_event.set()
                    break

        def countdown_and_restart():
            for i in range(14, 0, -1):
                if skip_event.is_set():
                    break
                print(i)
                time.sleep(1)
            skip_event.set()
            self.restart_app()

        # Start both threads
        Thread(target=wait_for_enter, daemon=True).start()
        Thread(target=countdown_and_restart, daemon=True).start()
    
    def restart_app(self):
        """Restart the UI application"""
        # Kill the old process and its children if it exists
        if self.process:
            try:
                parent = psutil.Process(self.process.pid)
                children = parent.children(recursive=True)
                for child in children:
                    child.terminate()
                parent.terminate()
                print("Terminated previous instance")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Start new process
        print("\nStarting UI application...")
        try:
            # Use the same Python interpreter that's running this script
            python_exe = sys.executable
            main_script = os.path.join(self.src_dir, "main.py")
            
            # Create the process with the working directory set to src/
            self.process = subprocess.Popen(
                [python_exe, main_script],
                cwd=self.src_dir  # Set working directory to src/
            )
        except Exception as e:
            print(f"Error starting UI: {e}")

def main():
    src_dir = get_src_dir()
    print(f"Watching for changes in: {src_dir}")
    print("Press Ctrl+C to stop")
    
    watcher = FileWatcher()
    
    try:
        while True:
            if watcher.check_for_changes():
                watcher.schedule_restart()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping file watcher...")
        if watcher.restart_timer:
            watcher.restart_timer.cancel()
        if watcher.process:
            watcher.process.terminate()

if __name__ == "__main__":
    main() 