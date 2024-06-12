import numpy as np
from asammdf import MDF, Signal

if __name__ == "__main__":
    mdf = MDF("output/file_0002.mf4", memory="minimum")
    try:
        channel_group_index = 0
        channel_index = 1
        signal = mdf.get("sig_1", group=1, index=channel_index)
        print(signal)
    except Exception as ex:
        print(str(ex))
