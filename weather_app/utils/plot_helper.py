#If more complex plotting logic is required, add helper functions here.

def prepare_plot_data(data):
    times = [entry["time"] for entry in data]
    rain_values = [entry["rain"] for entry in data]
    return times, rain_values
