import argparse
from cv.base import parse_voc_to_table, export_voc_from_table
import glob
import shutil
from tqdm import tqdm
import os


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_ann', help='source annotations directory path, like[/path/to/directory/*.xml]')
    parser.add_argument('--target_ann', help='target annotations directory path, like[/path/to/directory/]')
    parser.add_argument('--mapping', nargs='+', help='label mapping')
    args = parser.parse_args()
    args.mapping = {k: v for k, v in zip(args.mapping[0::2], args.mapping[1::2])}
    print(args.mapping)
    return args


def main():
    args = parse_args()
    # 更换注解
    table = parse_voc_to_table(args.source_ann)
    table['label'] = table['label'].apply(lambda x: args.mapping.get(x))
    # table['label'] = table['label'].apply(lambda x: args.mapping.get(x, x))
    export_voc_from_table(table, args.target_ann)

if __name__ == '__main__':
    main()
