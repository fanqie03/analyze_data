import argparse
from cv.base import parse_voc_to_table, export_voc_from_table
import glob
import shutil
from tqdm import tqdm
import os
import cv2
import time


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_ann', help='source annotations directory path, like[/path/to/directory/*.xml]')
    parser.add_argument('--target_ann', help='target annotations directory path, like[/path/to/directory/]')
    parser.add_argument('--remove_labels', nargs='+', help='labels to be removed')

    parser.add_argument('--rename_prefix')
    parser.add_argument('--rename_suffix')
    parser.add_argument('--source_img', help='source images directory path, like[/path/to/directory/*.jpg]')
    parser.add_argument('--target_img', help='target images directory path, like[/path/to/directory/]')

    parser.add_argument('--mapping', nargs='+', help='label mapping')

    parser.add_argument('--crop_save', help='crop bbox from image and save to target directory')

    parser.add_argument('--filter_bbox_width', type=float, default=0, help='can be [0-1] or >1')
    parser.add_argument('--filter_bbox_height', type=float, default=0, help='can be [0-1] or >1')

    parser.add_argument('--test', action='store_true')

    args = parser.parse_args()
    return args


def check_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


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
    filename = prefix + file_prefix + suffix + '.' + file_suffix
    return filename


def crop_and_save(x, grouped, args):
    src_img = args.source_img[x]
    sub_table = grouped.get_group(os.path.basename(src_img))
    img = cv2.imread(src_img)
    for index, row in sub_table.iterrows():
        si = img[row['ymin']: row['ymax'], row['xmin']: row['xmax']]
        filename = os.path.join(args.crop_save, str(time.time()) + '.jpg')
        cv2.imwrite(filename, si)


def main():
    args = parse_args()
    # 更换注解
    table = parse_voc_to_table(args.source_ann)

    if args.test:
        table = table.sample(int(0.1 * len(table)))

    if args.remove_labels:
        print('rename labels')
        table = table[~table['label'].isin(args.remove_labels)]

    if args.rename_prefix or args.rename_suffix:
        print('renmae filename')
        # 更换注解
        table = parse_voc_to_table(args.source_ann)
        table['filename'] = table['filename'].apply(lambda x: rename(x, args.prefix, args.suffix))
        export_voc_from_table(table, args.target_ann)
        # 更换文件名
        for src_img in tqdm(glob.glob(args.source_img)):
            target_img = rename(src_img, args.prefix, args.suffix)
            target_img = os.path.join(args.target_img, target_img)
            shutil.copy(src_img, target_img)

    if args.mapping:
        print('rename label')
        args.mapping = {k: v for k, v in zip(args.mapping[0::2], args.mapping[1::2])}
        table['label'] = table['label'].apply(lambda x: args.mapping.get(x))

    if args.crop_save:
        print('crop and save')
        grouped = table.groupby('filename')
        args.source_img = list(glob.glob(args.source_img))
        length = len(args.source_img)
        for i in tqdm(range(length)):
            crop_and_save(i, grouped, args)

    if args.filter_bbox_width or args.filter_bbox_height:
        print('filter width and height')
        if args.filter_bbox_width > 1:
            table = table[table['bbox_width'] > args.filter_bbox_width]
        else:
            table = table[table['bbox_width'] / table['img_width'] > args.filter_bbox_width]
        if args.filter_bbox_height > 1:
            table = table[table['bbox_height'] > args.filter_bbox_height]
        else:
            table = table[table['bbox_height'] / table['img_height'] > args.filter_bbox_height]

    export_voc_from_table(table, args.target_ann)


if __name__ == '__main__':
    main()
