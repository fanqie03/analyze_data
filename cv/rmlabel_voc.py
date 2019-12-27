import argparse
from cv.base import parse_voc_to_table, export_voc_from_table
import glob
import shutil
from tqdm import tqdm
import os


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_ann', help='source annotations directory path, like[/path/to/directory/*.xml]')
    parser.add_argument('--target_ann', help='target annotations directory path, like[/path/to/directory/*.xml]')
    parser.add_argument('--labels', nargs='+', help='labels to be removed')
    args = parser.parse_args()
    return args


def rename(filename, prefix, suffix):
    """
    提取出文件名，在文件名前缀加prefix,文件名后缀加suffix
    :param filename:
    :param prefix:
    :param suffix:
    :return:
    """
    filename = filename.split('/')[-1]
    file_prefix = ''.join(filename.split('.')[:-1])
    file_suffix = filename.split('.')[1]
    filename = prefix + file_prefix + suffix + '.' +file_suffix
    return filename


def main():
    args = parse_args()
    # 更换注解
    table = parse_voc_to_table(args.source_ann)
    table = table[~table['label'].isin(args.labels)]
    export_voc_from_table(table, args.target_ann)


if __name__ == '__main__':
    main()
