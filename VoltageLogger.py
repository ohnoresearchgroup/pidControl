import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import threading
import time
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from labjackPID import LabJackPID

class VoltageLoggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voltage Logger")
        
        self.lj = LabJackPID()

        self.acquisition_running = False
        self.data = []
        self.times = []

        # File name input
        self.file_name_label = tk.Label(root, text="Set File Name:")
        self.file_name_label.grid(row=0, column=0, padx=10, pady=10)
        self.file_name_entry = tk.Entry(root)
        self.file_name_entry.grid(row=0, column=1, padx=10, pady=10)

        # Folder save location
        self.folder_label = tk.Label(root, text="Save Location:")
        self.folder_label.grid(row=3, column=0, padx=10, pady=10)
        self.folder_path_var = tk.StringVar()
        self.folder_entry = tk.Entry(root, textvariable=self.folder_path_var, width=40)
        self.folder_entry.grid(row=3, column=1, padx=10, pady=10)
        self.browse_button = tk.Button(root, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=3, column=2, padx=10, pady=10)

        # Start acquisition button
        self.start_button = tk.Button(root, text="Start Acquisition", command=self.start_acquisition)
        self.start_button.grid(row=4, column=0, columnspan=1, pady=10)

        # Stop acquisition button
        self.stop_button = tk.Button(root, text="Stop Acquisition", command=self.stop_acquisition, state=tk.DISABLED)
        self.stop_button.grid(row=4, column=1, columnspan=1, pady=10)

        self.plot_window = None

    def browse_folder(self):
        """Open a folder dialog to select a save location."""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_path_var.set(folder_path)

    def save_config(self):
        """Save the file name and folder location."""
        self.file_name = self.file_name_entry.get()
        self.folder_path = self.folder_path_var.get()

        if not self.file_name:
            messagebox.showerror("Error", "Please enter a file name.")
            return False
        
        if not self.folder_path:
            messagebox.showerror("Error", "Please select a save location.")
            return False

        # Save the configuration
        self.full_path = f"{self.folder_path}/{self.file_name}.csv"
        try:
            with open(self.full_path, "w") as file:
                
                #write headings
                file.write("period,voltage\n")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
            return False

    def start_acquisition(self):
        """Start the data acquisition process."""
        if self.acquisition_running:
            return

        if not self.save_config():
            return
        

        self.acquisition_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Start a new thread for acquisition
        self.acquisition_thread = threading.Thread(target=self.acquire_data)
        self.acquisition_thread.daemon = True
        self.acquisition_thread.start()

        # Open plot window
        self.open_plot_window()

    def stop_acquisition(self):
        """Stop the data acquisition process."""
        self.acquisition_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def acquire_data(self):
        try:
            with open(self.full_path, "a") as file:
                while self.acquisition_running:
                    #check to see if data is ready
                    
                    v = self.lj.readVoltage(1)
                    t = datetime.now()
                    
                    self.data.append(v)
                    self.times.append(t)
                    
                    file.write(f"{t},{v}\n")
                    

                    # Update plot
                    if self.plot_window:
                        self.plot_ax.clear()
                        self.plot_ax.set_title("Acquisition Data")
                        self.plot_ax.set_xlabel("Time")
                        self.plot_ax.set_ylabel("Voltage")
                        self.plot_ax.plot(self.times, self.data)
                        self.plot_canvas.draw()
                            
                    time.sleep(0.5)
                        
        except Exception as e:
            messagebox.showerror("Error", f"Failed during acquisition: {e}")

    def open_plot_window(self):
        """Open a separate window for plotting data."""
        if self.plot_window is None or not tk.Toplevel.winfo_exists(self.plot_window):
            self.plot_window = tk.Toplevel(self.root)
            self.plot_window.title("Acquisition Data Plot")

            self.plot_figure = plt.Figure(figsize=(6, 5), dpi=100)
            self.plot_ax = self.plot_figure.add_subplot(111)
            self.plot_ax.set_title("Acquisition Data")
            self.plot_ax.set_xlabel("Time (s)")
            self.plot_ax.set_ylabel("Value")

            self.plot_canvas = FigureCanvasTkAgg(self.plot_figure, master=self.plot_window)
            self.plot_canvas_widget = self.plot_canvas.get_tk_widget()
            self.plot_canvas_widget.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = VoltageLoggerApp(root)
    root.mainloop()
