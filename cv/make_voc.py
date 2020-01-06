import argparse
from cv.base import parse_voc_to_table, export_voc_from_table
import glob
import shutil
from tqdm import tqdm
import os
import cv2
import time
import numpy as np


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

    parser.add_argument('--show_extreme', action='store_true')

    parser.add_argument('--inp_dim', type=int, default=300)

    args = parser.parse_args()
    return args


def check_directory(path):
    if path and not os.path.exists(path):
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


def letterbox_image(img, inp_dim):
    '''resize image with unchanged aspect ratio using padding'''
    img_w, img_h = img.shape[1], img.shape[0]
    w, h = inp_dim
    new_w = int(img_w * min(w / img_w, h / img_h))
    new_h = int(img_h * min(w / img_w, h / img_h))
    resized_image = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

    canvas = np.full((inp_dim[1], inp_dim[0], 3), 128, dtype=np.uint8)

    canvas[(h - new_h) // 2:(h - new_h) // 2 + new_h, (w - new_w) // 2:(w - new_w) // 2 + new_w, :] = resized_image

    return canvas


def main():
    args = parse_args()
    check_directory(args.target_ann)
    check_directory(args.target_img)
    if args.source_img:
        args.source_img = list(glob.glob(args.source_img))
    # 更换注解
    table = parse_voc_to_table(args.source_ann)

    if args.test:
        table = table.sample(int(0.1 * len(table)))

    if args.show_extreme:
        img_root = os.path.dirname(args.source_img[0])
        table_ = table[(table['bbox_width'] / table['img_width'] < args.filter_bbox_width) | (
                table['bbox_height'] / table['img_height'] < args.filter_bbox_height)]
        print(f'bbox num has {len(table_)}')
        grouped = table_.groupby('filename')
        print(f'img num has {len(grouped)}')

        for filename in table_['filename'].unique():
            img_path = os.path.join(img_root, filename)
            sub_table = grouped.get_group(filename)
            img = cv2.imread(img_path)
            for index, row in sub_table.iterrows():
                cv2.rectangle(img, (row['xmin'], row['ymin']), (row['xmax'], row['ymax']),
                              (0, 255, 0))

            if args.inp_dim:
                img = letterbox_image(img, (args.inp_dim, args.inp_dim))
            cv2.imshow('image_win', img)

            cv2.waitKey()

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
        for src_img in tqdm(args.source_img):
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

    if args.target_ann:
        export_voc_from_table(table, args.target_ann)


if __name__ == '__main__':
    main()
