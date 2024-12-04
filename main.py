import tkinter as tk
from tkinter import ttk
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SystemMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("System Monitor")
        self.refresh_interval = 2000  # in milliseconds

        # Initialize data storage for graphs
        self.max_points = 30  # Number of points to display in the graph
        self.cpu_freq_data = []
        self.cpu_usage_data = []
        self.ram_total = psutil.virtual_memory().total / (1024 ** 3)  # in GB
        self.ram_used_data = []
        self.disk_usage_data = {}

        # Setup the UI
        self.setup_ui()

        # Start the update loop
        self.update_data()

    def setup_ui(self):
        # Create frames for CPU, RAM, and Storage
        cpu_frame = ttk.LabelFrame(self.root, text="CPU Information")
        cpu_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ram_frame = ttk.LabelFrame(self.root, text="RAM Information")
        ram_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        storage_frame = ttk.LabelFrame(self.root, text="Storage Information")
        storage_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # CPU Information Labels
        self.cpu_freq_label = ttk.Label(cpu_frame, text="Clock Speed: ")
        self.cpu_freq_label.pack(anchor='w', padx=5, pady=2)

        self.cpu_usage_label = ttk.Label(cpu_frame, text="Core Usage: ")
        self.cpu_usage_label.pack(anchor='w', padx=5, pady=2)

        # RAM Information Labels
        self.ram_total_label = ttk.Label(ram_frame, text=f"Total RAM: {self.ram_total:.2f} GB")
        self.ram_total_label.pack(anchor='w', padx=5, pady=2)

        self.ram_used_label = ttk.Label(ram_frame, text="Used RAM: ")
        self.ram_used_label.pack(anchor='w', padx=5, pady=2)

        self.ram_available_label = ttk.Label(ram_frame, text="Available RAM: ")
        self.ram_available_label.pack(anchor='w', padx=5, pady=2)

        # Storage Information Labels
        self.storage_labels = {}  # Dictionary to hold storage labels dynamically
        partitions = psutil.disk_partitions()
        for partition in partitions:
            label = ttk.Label(storage_frame, text=f"{partition.device}: Calculating...")
            label.pack(anchor='w', padx=5, pady=2)
            self.storage_labels[partition.device] = label

        # Setup matplotlib figures
        self.setup_graphs(cpu_frame, ram_frame)

    def setup_graphs(self, cpu_frame, ram_frame):
        # Create a notebook to hold multiple tabs
        notebook = ttk.Notebook(cpu_frame)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # CPU Frequency Graph
        self.cpu_freq_fig, self.cpu_freq_ax = plt.subplots(figsize=(4, 2))
        self.cpu_freq_line, = self.cpu_freq_ax.plot([], [], label='CPU Frequency (MHz)')
        self.cpu_freq_ax.set_title("CPU Clock Speed")
        self.cpu_freq_ax.set_xlabel("Time (s)")
        self.cpu_freq_ax.set_ylabel("MHz")
        self.cpu_freq_ax.set_ylim(0, 5000)  # Updated max limit to 5000 MHz
        self.cpu_freq_ax.legend()

        freq_canvas = FigureCanvasTkAgg(self.cpu_freq_fig, master=notebook)
        freq_canvas.draw()
        freq_canvas.get_tk_widget().pack(fill='both', expand=True)
        notebook.add(freq_canvas.get_tk_widget(), text='CPU Frequency')

        # CPU Usage Graph
        self.cpu_usage_fig, self.cpu_usage_ax = plt.subplots(figsize=(4, 2))
        self.cpu_usage_line, = self.cpu_usage_ax.plot([], [], label='CPU Usage (%)', color='green')
        self.cpu_usage_ax.set_title("CPU Core Usage")
        self.cpu_usage_ax.set_xlabel("Time (s)")
        self.cpu_usage_ax.set_ylabel("Usage (%)")
        self.cpu_usage_ax.set_ylim(0, 100)
        self.cpu_usage_ax.legend()

        usage_canvas = FigureCanvasTkAgg(self.cpu_usage_fig, master=notebook)
        usage_canvas.draw()
        usage_canvas.get_tk_widget().pack(fill='both', expand=True)
        notebook.add(usage_canvas.get_tk_widget(), text='CPU Usage')

        # RAM Usage Graph
        self.ram_used_fig, self.ram_used_ax = plt.subplots(figsize=(4, 2))
        self.ram_used_line, = self.ram_used_ax.plot([], [], label='Used RAM (GB)', color='blue')
        self.ram_used_ax.set_title("RAM Usage")
        self.ram_used_ax.set_xlabel("Time (s)")
        self.ram_used_ax.set_ylabel("GB")
        self.ram_used_ax.set_ylim(0, self.ram_total)
        self.ram_used_ax.legend()

        ram_used_canvas = FigureCanvasTkAgg(self.ram_used_fig, master=ram_frame)
        ram_used_canvas.draw()
        ram_used_canvas.get_tk_widget().pack(fill='both', expand=True)

        # Store canvas and axes for updating
        self.graphs = {
            'cpu_freq': (self.cpu_freq_fig, self.cpu_freq_ax, self.cpu_freq_line),
            'cpu_usage': (self.cpu_usage_fig, self.cpu_usage_ax, self.cpu_usage_line),
            'ram_used': (self.ram_used_fig, self.ram_used_ax, self.ram_used_line),
        }

    def update_data(self):
        # Get CPU information
        freq = psutil.cpu_freq().current if psutil.cpu_freq() else 0
        avg_usage = psutil.cpu_percent(interval=None)  # Overall CPU usage

        # Get RAM information
        ram = psutil.virtual_memory()
        ram_used = ram.used / (1024 ** 3)  # in GB
        ram_available = ram.available / (1024 ** 3)  # in GB

        # Update labels
        self.cpu_freq_label.config(text=f"Clock Speed: {freq:.2f} MHz")
        self.cpu_usage_label.config(text=f"CPU Usage: {avg_usage:.2f}%")
        self.ram_used_label.config(text=f"Used RAM: {ram_used:.2f} GB")
        self.ram_available_label.config(text=f"Available RAM: {ram_available:.2f} GB")

        # Update storage information
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                used = usage.used / (1024 ** 3)  # in GB
                available = usage.free / (1024 ** 3)  # in GB
                self.storage_labels[partition.device].config(
                    text=f"{partition.device}: Used: {used:.2f} GB, Available: {available:.2f} GB"
                )
            except PermissionError:
                self.storage_labels[partition.device].config(
                    text=f"{partition.device}: Permission Denied"
                )

        # Update data lists
        self.cpu_freq_data.append(freq)
        self.cpu_usage_data.append(avg_usage)
        self.ram_used_data.append(ram_used)

        # Keep only the latest max_points
        self.cpu_freq_data = self.cpu_freq_data[-self.max_points:]
        self.cpu_usage_data = self.cpu_usage_data[-self.max_points:]
        self.ram_used_data = self.ram_used_data[-self.max_points:]

        # Update graphs
        self.update_graph('cpu_freq', self.cpu_freq_data)
        self.update_graph('cpu_usage', self.cpu_usage_data)
        self.update_graph('ram_used', self.ram_used_data)

        # Schedule the next update
        self.root.after(self.refresh_interval, self.update_data)

    def update_graph(self, graph_name, data):
        fig, ax, line = self.graphs[graph_name]
        line.set_data(range(len(data)), data)
        ax.set_xlim(0, self.max_points)
        if graph_name == 'cpu_freq':
            ax.set_ylim(0, 5000)  # Updated max limit to 5000 MHz
        elif graph_name == 'cpu_usage':
            ax.set_ylim(0, 100)
        elif graph_name == 'ram_used':
            ax.set_ylim(0, self.ram_total)
        ax.figure.canvas.draw()
        ax.figure.canvas.flush_events()


def main():
    root = tk.Tk()
    app = SystemMonitorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
