
import tkinter as tk
from tkinter import messagebox
import math

class StreamInput:
    def __init__(self, parent, label, row, stream_type):
        self.frame = tk.Frame(parent)
        self.frame.grid(row=row, column=0, columnspan=3, pady=2)

        self.label = tk.Label(self.frame, text=label)
        self.label.grid(row=0, column=0)

        self.fluid_var = tk.StringVar(value="Gas")
        self.fluid_menu = tk.OptionMenu(self.frame, self.fluid_var, "Gas", "Oil", "Water", command=self.update_unit_label)
        self.fluid_menu.grid(row=0, column=1)

        self.flow_entry = tk.Entry(self.frame, width=10)
        self.flow_entry.insert(0, "0")
        self.flow_entry.grid(row=0, column=2)
        self.flow_label = tk.Label(self.frame, text="Flow (MMSCFD)")
        self.flow_label.grid(row=0, column=3)

        self.pressure_entry = tk.Entry(self.frame, width=10)
        self.pressure_entry.insert(0, "0")
        self.pressure_entry.grid(row=0, column=4)
        self.pressure_label = tk.Label(self.frame, text="Pressure (psi)")
        self.pressure_label.grid(row=0, column=5)

        self.api_entry = tk.Entry(self.frame, width=10)
        self.api_entry.grid(row=0, column=6)
        self.api_label = tk.Label(self.frame, text="API (if Oil)")
        self.api_label.grid(row=0, column=7)

        self.stream_type = stream_type

    def update_unit_label(self, selection):
        if selection == "Gas":
            self.flow_label.config(text="Flow (MMSCFD)")
        else:
            self.flow_label.config(text="Flow (BPD)")

    def get_data(self):
        try:
            flow = float(self.flow_entry.get())
            pressure = float(self.pressure_entry.get())
            api = self.api_entry.get()
            api_val = float(api) if api else None
            return {
                "type": self.fluid_var.get(),
                "flow": flow,
                "pressure": pressure,
                "api": api_val,
                "stream_type": self.stream_type
            }
        except ValueError:
            return None

def calculate():
    try:
        all_streams = motive_streams + suction_streams
        total_mass_flow = 0
        rho_list = []

        R = 10.73
        T = 520
        MW = 18
        gamma = 1.3

        for stream in all_streams:
            data = stream.get_data()
            if data["flow"] <= 0:
                continue

            fluid_type = data["type"]
            flow = data["flow"]
            pressure = data["pressure"]
            api = data["api"]

            if fluid_type == "Gas":
                rho = (pressure * MW) / (R * T)
                velocity = math.sqrt(gamma * R * T * 144 / MW)
                lbmol = (flow * 1e6) / (R * T)
                mass_flow = lbmol * MW
            else:
                rho = 62.4 if fluid_type == "Water" else ((141.5 / (api + 131.5)) * 62.4 if api else 53)
                velocity = 150 if fluid_type == "Oil" else 100
                ft3 = flow * 5.615  # Convert BPD to ft³/day
                mass_flow = ft3 * rho

            rho_list.append(rho)
            total_mass_flow += mass_flow

        if total_mass_flow == 0 or not rho_list:
            messagebox.showerror("Input Error", "Please enter valid flow and pressure values.")
            return

        avg_rho = sum(rho_list) / len(rho_list)
        avg_velocity = 125
        mass_flow_rate = total_mass_flow / 86400

        area_throat = mass_flow_rate / (avg_rho * avg_velocity)
        diameter_throat = 2 * math.sqrt(area_throat / math.pi)
        diameter_throat_in = diameter_throat * 12
        diameter_mixing_in = 2 * diameter_throat_in

        result_text = (
            f"Total Mass Flow: {total_mass_flow:.2f} lbm/day\n"
            f"Avg Density: {avg_rho:.2f} lb/ft³\n"
            f"Nozzle Throat Diameter: {diameter_throat_in:.2f} in\n"
            f"Mixing Chamber Diameter: {diameter_mixing_in:.2f} in"
        )
        result_label.config(text=result_text)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def add_motive_stream():
    row = len(motive_streams) + len(suction_streams) + 1
    stream = StreamInput(root, f"Motive Stream {len(motive_streams)+1}", row, "motive")
    motive_streams.append(stream)

def add_suction_stream():
    row = len(motive_streams) + len(suction_streams) + 1
    stream = StreamInput(root, f"Suction Stream {len(suction_streams)+1}", row, "suction")
    suction_streams.append(stream)

root = tk.Tk()
root.title("Multi-Stream Ejector Sizing Tool")

motive_streams = []
suction_streams = []

tk.Button(root, text="Add Motive Stream", command=add_motive_stream).grid(row=0, column=0)
tk.Button(root, text="Add Suction Stream", command=add_suction_stream).grid(row=0, column=1)
tk.Button(root, text="Calculate", command=calculate).grid(row=0, column=2)

result_label = tk.Label(root, text="", justify="left", font=("Courier", 10))
result_label.grid(row=999, column=0, columnspan=3, pady=20)

root.mainloop()
