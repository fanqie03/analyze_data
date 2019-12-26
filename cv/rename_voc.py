import argparse
from cv.base import parse_voc_to_table, export_voc_from_table
import glob
import shutil
from tqdm import tqdm
import os


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_ann', help='source annotations directory path, like[/path/to/directory/*.xml]')
    parser.add_argument('--source_img', help='source images directory path, like[/path/to/directory/*.jpg]')
    parser.add_argument('--target_ann', help='target annotations directory path, like[/path/to/directory/]')
    parser.add_argument('--target_img', help='target images directory path, like[/path/to/directory/]')
    parser.add_argument('--prefix', default='', help='prefix of original filename')
    parser.add_argument('--suffix', default='', help='suffix of original filename')
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
    table['filename'] = table['filename'].apply(lambda x: rename(x, args.prefix, args.suffix))
    export_voc_from_table(table, args.target_ann)
    # 更换文件名
    for src_img in tqdm(glob.glob(args.source_img)):
        target_img = rename(src_img, args.prefix, args.suffix)
        target_img = os.path.join(args.target_img, target_img)
        shutil.copy(src_img, target_img)


if __name__ == '__main__':
    main()
