import pandas_profiling
from pathlib import Path
import glob
import argparse
import matplotlib.pyplot as plt

import pandas as pd
import cv2

import os.path as osp
import xml.etree.ElementTree as ET

import numpy as np
from collections import Counter

title =['filename',
        'img_width',
        'img_height',
        'img_depth',
        'bbox_width',
        'bbox_height',
        'label',
        'xmin',
        'ymin',
        'xmax',
        'ymax',
        'ratio',
        'bbox_scale_width',
        'bbox_scale_height',
        'scale(area)',
        'ignore',
        'difficult']


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('--output')
    parser.add_argument('--show', action='store_true')
    args = parser.parse_args()
    return args


def parse_single_voc(ann_file, root=None, min_size=None):
    if root is not None:
        ann_file = osp.join(root, ann_file)

    tree = ET.parse(ann_file)
    root = tree.getroot()

    filename = root.find('filename').text
    size = root.find('size')
    width = int(size.find('width').text)
    height = int(size.find('height').text)
    depth = int(size.find('depth').text)

    table = []

    for obj in root.findall('object'):
        name = obj.find('name').text
        difficult = int(obj.find('difficult').text) \
                if obj.find('difficult') is not None else 0

        bnd_box = obj.find('bndbox')
        bbox = [
            int(float(bnd_box.find('xmin').text)),
            int(float(bnd_box.find('ymin').text)),
            int(float(bnd_box.find('xmax').text)),
            int(float(bnd_box.find('ymax').text))
        ]
        ignore = False

        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if min_size and (w < min_size or h < min_size):
            ignore = True

        row = {
            'filename': filename,
            'img_width': width,
            'img_height': height,
            'img_depth': depth,
            'bbox_width': w,
            'bbox_height': h,
            'label': name,
            'xmin': bbox[0],
            'ymin': bbox[1],
            'xmax': bbox[2],
            'ymax': bbox[3],
            'ratio': (w+1e-6)/(h+1e-6),
            'bbox_scale_width': w / width,
            'bbox_scale_height': h / height,
            'scale(area)': (w*h)/(width*height),
            'ignore': ignore,
            'difficult': difficult
        }
        table.append(list(row.values()))
    return table


def analyze(table: pd.DataFrame, export):
    # table.plot.scatter(x='img_width', y='img_height', alpha=0.25)
    # table.plot.scatter(x='bbox_width', y='bbox_height', alpha=0.25)
    #
    # table.plot.scatter(x='xmin', y='ymin', alpha=0.25)
    # table.plot.scatter(x='xmax', y='ymax', alpha=0.25)
    # plt.show()

    pfr = pandas_profiling.ProfileReport(table)
    pfr.to_file(export)


# def draw(rows):
#     img = cv2.imread(rows[0]['filename'])
#     for row in rows:
#         cv2.putText()


def main():
    args = parse_args()

    table = []
    # build the dataloader
    output = str(Path(args.input).parent.parent / 'analyze.csv')
    output_html = str(Path(args.input).parent.parent / 'analyze.html')
    for ann_folder in glob.glob(args.input):
        rows = parse_single_voc(str(ann_folder))
        table.extend(rows)

        # if args.show and len(rows) > 0:
        #     img = cv2.imread(rows[0]['filename'])
        #     for row in rows:
        #         cv2.putText()


    table = np.asarray(table)
    table = pd.DataFrame(table, columns=title)
    # print(table.head())
    table.to_csv(output, index=False)
    table = pd.read_csv(output)
    analyze(table, output_html)


if __name__ == '__main__':
    main()
