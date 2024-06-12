import numpy as np
from asammdf import MDF, Signal


class SignalGenerator:
    def __init__(self):
        start_time = 0.0
        d_time = 0.01
        end_time = 3.0 + d_time

        time = np.array(np.arange(start_time, end_time, d_time), dtype=np.float32)

        # ======================================================================
        self.velocity = Signal(
            samples=np.sin(2 * np.pi * 2 * time),
            timestamps=time,
            name="velocity",
            unit="u1",
        )
        self.acceleration = Signal(
            samples=np.sin(2 * np.pi * 2 * time),
            timestamps=time,
            name="acceleration",
            unit="u1",
        )
        # ======================================================================
        self.torque = Signal(
            samples=np.sin(2 * np.pi * 2 * time),
            timestamps=time,
            name="torque",
            unit="u1",
        )
        # ======================================================================

    def func_1(self):
        with MDF(version="4.10") as mdf4:
            # append the 3 signals to the new file
            channel_0 = [self.velocity, self.acceleration]
            channel_1 = [self.torque]

            mdf4.append(channel_0, comment="grp_0")
            mdf4.append(channel_1, comment="grp_1")

            mdf4.save("output/file_000.mf4", overwrite=True)


if __name__ == "__main__":
    sg = SignalGenerator()
    sg.func_1()
