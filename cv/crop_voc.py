import argparse
import glob
import os
import time

import cv2
from tqdm import tqdm

from cv.base import parse_voc_to_table


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_ann', help='source annotations directory path, like[/path/to/directory/*.xml]')
    parser.add_argument('--source_img', help='source images directory path, like[/path/to/directory/*.jpg]')
    parser.add_argument('--crop_save', help='crop bbox from image and save to target directory', default='tmp')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    if not os.path.exists(args.crop_save):
        os.makedirs(args.crop_save)

    table = parse_voc_to_table(args.source_ann)
    # table['filename'] = table['filename'].apply(lambda x: rename(x, args.prefix, args.suffix))
    # export_voc_from_table(table, args.target_ann)
    grouped = table.groupby('filename')

    args.source_img = list(glob.glob(args.source_img))
    length = len(args.source_img)

    def nothing(x):
        src_img = args.source_img[x]
        sub_table = grouped.get_group(os.path.basename(src_img))
        img = cv2.imread(src_img)
        for index, row in sub_table.iterrows():
            cv2.rectangle(img, (row['xmin'], row['ymin']), (row['xmax'], row['ymax']),
                          (0, 255, 0))
            si = img[row['xmin']: row['ymin'], row['xmax']: row['ymax']]
            filename = os.path.join(args.crop_save, str(time.time()) + '.jpg')
            cv2.imwrite(filename, si)

    for i in tqdm(range(length)):
        nothing(i)


if __name__ == '__main__':
    main()
