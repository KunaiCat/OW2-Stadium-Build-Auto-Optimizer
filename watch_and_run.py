import sys
import time
import os
import subprocess
import psutil
from threading import Timer

class FileWatcher:
    def __init__(self):
        self.process = None
        self.last_modified_times = {}
        self.update_file_times()
        self.restart_timer = None
        self.restart_app()
    
    def update_file_times(self):
        """Get modification times of all Python files in the directory"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        for filename in os.listdir(script_dir):
            if filename.endswith('.py'):
                filepath = os.path.join(script_dir, filename)
                try:
                    mtime = os.path.getmtime(filepath)
                    self.last_modified_times[filepath] = mtime
                except OSError:
                    continue
    
    def check_for_changes(self):
        """Check if any Python files have been modified"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        for filename in os.listdir(script_dir):
            if filename.endswith('.py'):
                filepath = os.path.join(script_dir, filename)
                try:
                    mtime = os.path.getmtime(filepath)
                    last_mtime = self.last_modified_times.get(filepath)
                    
                    if last_mtime is None or mtime > last_mtime:
                        print(f"\nChange detected in {filename}")
                        self.last_modified_times[filepath] = mtime
                        return True
                except OSError:
                    continue
        return False
    
    def schedule_restart(self):
        """Schedule a restart after 15 seconds"""
        # Cancel any existing scheduled restart
        if self.restart_timer:
            self.restart_timer.cancel()
        
        # Schedule new restart
        print("\nWaiting 15 seconds for changes to settle...")
        self.restart_timer = Timer(15.0, self.restart_app)
        self.restart_timer.start()
    
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
            self.process = subprocess.Popen([python_exe, "-c", "from ui import main; main()"])
        except Exception as e:
            print(f"Error starting UI: {e}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Watching for changes in: {script_dir}")
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