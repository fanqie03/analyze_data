import os
from pathlib import Path
import numpy as np
import pandas as pd
import shutil as sh
import argparse


def parse_args():
    parser = argparse.ArgumentParser("""
    从img_dir目录中提取ann_dir目录下的存在的stem，提取到target_dir下
    """)
    parser.add_argument('--ann_dir')
    parser.add_argument('--img_dir')
    parser.add_argument('--target_dir')
    args = parser.parse_args()
    return args


def read_dir(file_root):
    file_root = Path(file_root)
    files = list(file_root.glob('*'))
    df = pd.DataFrame()
    df['file'] = files
    df['stem'] = [x.stem for x in files]
    return df


def main():
    args = parse_args()
    if not os.path.exists(args.target_dir):
        os.makedirs(args.target_dir)

    imgs_df = read_dir(args.img_dir)
    anns_df = read_dir(args.ann_dir)
    target_df = imgs_df[imgs_df.stem.isin(anns_df.stem)]

    target_df.file.map(lambda x: sh.copy(x, os.path.join(args.target_dir, x.name)))


if __name__ == '__main__':
    main()