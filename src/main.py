import os
from datetime import datetime
from tkinter import filedialog, Label
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import tkinter as tk

import mplcursors
import seaborn as sns
import matplotlib.dates as mdates
import pandas as pd

from src.OwnParser import Parser


def open_file(file_type: str) -> str:
    """
     Open a file dialog and return the selected file path.

     :param file_type: The type of file to open (e.g., "temperature", "door")
     :return: The selected file path, or an empty string if no file was chosen

    """
    user_home = os.path.expanduser("~")
    top = tk.Toplevel(root)
    top.transient(root)
    top.withdraw()

    filepath = filedialog.askopenfilename(
        initialdir=user_home,
        title=f"Choose {file_type}",
        filetypes=(("html", "*.html"),)
    )

    top.destroy()
    return filepath or ""


def close_app() -> None:
    """
    Creteates a message box to notify the user that the application will close.

    :return: None
    """
    mainwindow = tk.Tk()
    mainwindow.title("Protocol2graph")
    mainwindow.geometry("800x600")

    label = Label(mainwindow, text="No temperature file found", bg="red")
    label.pack()

    mainwindow.lift()
    mainwindow.focus_force()

    mainwindow.mainloop()
    exit()


def process_door_file(door_file_path: str, ax):
    """
    Process the door file and draw the door openings on the given axis.
    :param door_file_path:
    :param ax:
    :return:
    """
    if not door_file_path:
        return

    with open(door_file_path, 'r', encoding='utf-8') as door_file:
        doors = Parser.getDooropenings(door_file.read())

    for door in doors:
        if door.open_time and door.close_time:
            ax.axvspan(door.open_time, door.close_time, color='gray', alpha=0.3)

    return doors


def on_xlims_change(event_ax) -> None:
    """
    Adjusts the x-axis grid when zooming into the chart.
    :param event_ax:
    :return:
    """
    x_min, x_max = event_ax.get_xlim()
    x_min = mdates.num2date(x_min)
    x_max = mdates.num2date(x_max)
    time_diff = x_max - x_min

    if time_diff < pd.Timedelta(minutes=30):
        event_ax.xaxis.set_major_locator(mdates.MinuteLocator())
        event_ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    else:
        event_ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        event_ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

    fig.canvas.draw_idle()


def parse_temperature_file(temperature_file_path: str):
    """
    Parses the temperature file and extracts the temperature data.
    :param temperature_file_path: filepath of the file with temperature protocol
    :return:
    """
    with open(temperature_file_path, 'r', encoding='utf-8') as temperature_file:
        temperatures_parsed = Parser.getTempratures(temperature_file.read())

    y_temperatures_t1 = []
    y_temperatures_t2 = []
    y_temperatures_hf = []
    y_temperatures_ct = []
    x_temperatures = []

    for temperature_object in temperatures_parsed[1]:
        y_temperatures_t1.append(temperature_object.t1)
        y_temperatures_t2.append(temperature_object.t2)
        y_temperatures_hf.append(temperature_object.hf)
        y_temperatures_ct.append(temperature_object.ct)

        timestamp = datetime.strptime(temperature_object.date + " " + temperature_object.time, "%Y-%m-%d %H:%M:%S")
        x_temperatures.append(timestamp)

    return x_temperatures, y_temperatures_t1, y_temperatures_t2, y_temperatures_hf, y_temperatures_ct, temperatures_parsed


# Funktion zum Erstellen des Temperaturplots
def create_temperature_plot(ax,
                            x_temperatures: list,
                            y_temperatures_t1: list,
                            y_temperatures_t2: list,
                            y_temperatures_hf: list,
                            y_temperatures_ct: list,
                            temperatures_parsed
                            ):
    """
    Creates the temperature plot and adds cursor functionality.

    :param ax:
    :param x_temperatures: list with timestamps
    :param y_temperatures_t1: list with temperatures in chamber 1
    :param y_temperatures_t2: list with temperature in chamber 2
    :param y_temperatures_hf: list with temperatures in the maschine-room (IO-Board)
    :param y_temperatures_ct: list with temperatures of core temperature sensor
    :param temperatures_parsed: list with parsed temperature_file
    :return:
    """
    lines = []

    lines.append(ax.plot(x_temperatures, y_temperatures_t1, label="Temperature Chamber 1", marker="o")[0])
    if y_temperatures_t2 and any(temp != 0 for temp in y_temperatures_t2):
        lines.append(ax.plot(x_temperatures, y_temperatures_t2, label="Temperature Chamber 2", marker="o")[0])
    lines.append(ax.plot(x_temperatures, y_temperatures_ct, label="Core temperature", marker="o")[0])
    lines.append(ax.plot(x_temperatures, y_temperatures_hf, label="Component temperature", marker="o")[0])

    cursor = mplcursors.cursor(lines, hover=True)

    @cursor.connect("add")
    def on_add(sel):
        x, y = sel.target
        sel.annotation.set_text(f"{y:.1f} °C")

    schraffur_patch = mpatches.Patch(color='gray', alpha=0.3, label='Door open')
    ax.legend(handles=[schraffur_patch] + ax.get_legend_handles_labels()[0])

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.set_xlabel("Date and time")
    ax.set_ylabel(f"Temperatures in {temperatures_parsed[0].measurement}")

    ax.callbacks.connect('xlim_changed', on_xlims_change)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    temperature_file_path = open_file('Temperature-File')
    door_file_path = open_file('Door-Opening-File')

    if not temperature_file_path:
        close_app()

    temperature_filename = os.path.basename(temperature_file_path)

    x_temperatures, y_temperatures_t1, y_temperatures_t2, y_temperatures_hf, y_temperatures_ct, temperatures_parsed = parse_temperature_file(
        temperature_file_path)

    sns.set_style("whitegrid")
    fig, ax = plt.subplots()
    fig.canvas.manager.set_window_title(f"Temperaturen - {temperature_filename}")

    if door_file_path:
        process_door_file(door_file_path, ax)

    create_temperature_plot(ax, x_temperatures, y_temperatures_t1, y_temperatures_t2, y_temperatures_hf,
                            y_temperatures_ct, temperatures_parsed)

    plt.show()
