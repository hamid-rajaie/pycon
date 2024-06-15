import numpy as np
from asammdf import MDF, Signal

if __name__ == "__main__":
    mdf = MDF("output/file_000.mf4", memory="minimum")

    for idx, gp in enumerate(mdf.groups, 1):
        print(f"gp: {gp}")
        addr = gp.data_group.comment_addr
        print(f"add: {addr}")
        cg = gp.channel_group
        print(f"cg: {cg}")

    if False:
        try:
            channel_group_index = 0
            channel_index = 1
            signal = mdf.get("sig_1", group=1, index=channel_index)
            print(signal)
        except Exception as ex:
            print(str(ex))
