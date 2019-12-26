import argparse
from cv.base import parse_voc_to_table, export_voc_from_table
import glob
import shutil
from tqdm import tqdm
import os
import cv2


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_ann', help='source annotations directory path, like[/path/to/directory/*.xml]')
    parser.add_argument('--source_img', help='source images directory path, like[/path/to/directory/*.jpg]')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

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
        img = cv2.resize(img, (800, 800))
        cv2.imshow('image_win', img)
        # cv2.waitKey()

    cv2.namedWindow('image_win')
    cv2.namedWindow('tracker_win')
    cv2.createTrackbar('tracker', 'tracker_win', 0, length-1, nothing)

    cv2.waitKey()
    # for src_img in tqdm(glob.glob(args.source_img)):
    #     sub_table = grouped.get_group(os.path.basename(src_img))
    #     img = cv2.imread(src_img)
    #     for index, row in sub_table.iterrows():
    #         cv2.rectangle(img, (row['xmin'], row['ymin']), (row['xmax'], row['ymax']),
    #                       (0, 255, 0))
    #     img = cv2.resize(img, (600, 600))
    #
    #     cv2.imshow('', img)
    #     cv2.waitKey()

if __name__ == '__main__':
    main()
