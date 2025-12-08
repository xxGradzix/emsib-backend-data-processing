import matplotlib.pyplot as plt

class Visualizer:

    def plot_consumption(self, df):
        plt.plot(df["timestamp"], df["consumption"])
        plt.title("Energy Consumption Over Time")
        plt.xlabel("Time")
        plt.ylabel("kWh")
        plt.show()
