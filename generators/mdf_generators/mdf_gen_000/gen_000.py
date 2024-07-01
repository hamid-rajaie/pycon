import numpy as np
from asammdf import MDF, Signal


class SignalGenerator:
    def __init__(self):
        start_time = 0.0
        d_time = 0.01
        end_time = 3.0 + d_time

        time = np.array(np.arange(start_time, end_time, d_time), dtype=np.float32)

        # ======================================================================
        self.velocity_0 = Signal(
            samples=np.sin(2 * np.pi * 2 * time),
            timestamps=time,
            name="runnable_0.velocity",
            unit="u1",
        )
        self.acceleration_0 = Signal(
            samples=np.sin(2 * np.pi * 2 * time),
            timestamps=time,
            name="runnable_0.acceleration",
            unit="u1",
        )
        self.torque_0 = Signal(
            samples=np.sin(2 * np.pi * 2 * time),
            timestamps=time,
            name="runnable_0.torque",
            unit="u1",
        )

        # ======================================================================
        self.velocity_1 = Signal(
            samples=np.sin(2 * np.pi * 2 * time),
            timestamps=time,
            name="runnable_1.velocity",
            unit="u1",
        )
        self.acceleration_1 = Signal(
            samples=np.sin(2 * np.pi * 2 * time),
            timestamps=time,
            name="runnable_1.acceleration",
            unit="u1",
        )
        self.torque_1 = Signal(
            samples=np.sin(2 * np.pi * 2 * time),
            timestamps=time,
            name="runnable_1.torque",
            unit="u1",
        )
        # ======================================================================
        self.videoLines_left_dy = Signal(
            samples=np.sin(2 * np.pi * 2 * time),
            timestamps=time,
            name="runnable_2.m_videoLines.videoLines.i0.dy",
            unit="u1",
        )
        self.videoLines_right_dy = Signal(
            samples=np.sin(2 * np.pi * 2 * time),
            timestamps=time,
            name="runnable_2.m_videoLines.videoLines.i1.dy",
            unit="u1",
        )

        self.videoLines_left_curv = Signal(
            samples=np.sin(2 * np.pi * 2 * time),
            timestamps=time,
            name="runnable_2.m_videoLines.videoLines.i0.curv",
            unit="u1",
        )
        self.videoLines_right_curv = Signal(
            samples=np.sin(2 * np.pi * 2 * time),
            timestamps=time,
            name="runnable_2.m_videoLines.videoLines.i1.curv",
            unit="u1",
        )
        # ======================================================================

    def func_1(self):
        with MDF(version="4.10") as mdf4:
            # append the 3 signals to the new file
            channel_0 = [self.velocity_0, self.acceleration_0, self.torque_0]
            channel_1 = [self.velocity_1, self.acceleration_1, self.torque_1]
            channel_2 = [
                self.videoLines_left_dy,
                self.videoLines_left_curv,
                self.videoLines_right_dy,
                self.videoLines_right_curv,
            ]

            mdf4.append(channel_0, comment="runnable_0")
            mdf4.append(channel_1, comment="runnable_1")
            mdf4.append(channel_2, comment="runnable_2")

            mdf4.save("output/file_000.mf4", overwrite=True)


if __name__ == "__main__":
    sg = SignalGenerator()
    sg.func_1()
