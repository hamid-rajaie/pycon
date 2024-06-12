import numpy as np
import pandas as pd
from asammdf import MDF, Signal


class SignalGenerator:
    def __init__(self):
        df = pd.DataFrame()

        # ======================================================================
        # time is in second
        # ======================================================================
        start_time_sec = 200
        d_time_sec = 0.01
        duration_sec = 180 + d_time_sec
        end_time_sec = start_time_sec + duration_sec

        time = pd.Series(np.arange(start_time_sec, end_time_sec, d_time_sec), name="timestamp")
        df["timestamp"] = time.values

        freq_1 = 0.01
        sig_1 = np.sin(2 * np.pi * freq_1 * time)
        df["velocity"] = sig_1.values

        freq_2 = 0.04
        sig_2 = np.sin(2 * np.pi * freq_2 * time)
        df["acceleration"] = sig_2.values

        time_stamps = df["timestamp"]
        sig_3 = pd.Series(index=time_stamps.index, dtype=str)
        mask = (0 <= time_stamps) & (time_stamps <= 300)
        sig_3[mask] = "active"
        mask = time_stamps > 300
        sig_3[mask] = "passive"
        df["state"] = sig_3

        df.to_csv("output/file_0000.csv", index=False)


if __name__ == "__main__":
    sg = SignalGenerator()
