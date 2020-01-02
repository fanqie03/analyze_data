import glob
import os
import os.path as osp
import xml.etree.ElementTree as ET

import pandas as pd
from pascal_voc_writer import Writer
from tqdm import tqdm

"""
image information json format, like mmdetection
{
    'filename': 'a.jpg',
    'filepath': '../a.jpg',
    'width': 1280,
    'height': 720,
    'depth': 3, (optional field)
    'ann': {
        'bboxes': <np.ndarray, float32> (n, 4),
        # 'labels': <np.ndarray, int64> (n, ),
        'labels': <list, string> (n, ),
        'bboxes_ignore': <np.ndarray, float32> (k, 4),
        # 'labels_ignore': <np.ndarray, int64> (k, ) (optional field),
        'labels_ignore': <list, string> (k, ) (optional field)
    }
},
"""


def export_voc_from_table(table, target_dir):
    # table -> pd.DataFrame -> group by filename -> for each export
    if not isinstance(table, pd.DataFrame):
        table = pd.DataFrame(table)
    grouped = table.groupby('filename')
    for key, index in tqdm(grouped.groups.items()):
        sub_table = grouped.get_group(key)
        head = sub_table.iloc[0]
        path = head['filename']
        width = head['img_width']
        height = head['img_height']
        depth = head.get('img_depth', 3)

        writer = Writer(path, width, height, depth)

        for index, row in sub_table.iterrows():
            writer.addObject(row['label'], row['xmin'], row['ymin'], row['xmax'], row['ymax'], difficult=row['difficult'])

        ann_path = os.path.join(target_dir, os.path.basename(path).split('.')[0]+'.xml')
        writer.save(ann_path)


# def export_single_voc_from_table(table, save_root):
#     # table -> pd.DataFrame -> group by filename -> for each export
#     if not isinstance(table, pd.DataFrame):
#         table = pd.DataFrame(table)
#     grouped = table.groupby('filename')
#     for key, index in grouped.groups:
#         sub_table = table[index]
#         head = sub_table[0]
#         path = key
#         writer = Writer()


def export_single_voc_from_json(ann_file, img_info):
    """
    TODO
    :param ann_file: file name for export
    :param img_info: image information for export
    :return:
    """

    writer = Writer(img_info['filepath'], img_info['width'], img_info['height'], img_info.get('depth', 3))
    ann_info = img_info['ann']

    def addObject(bboxes, labels, difficult=0):
        for bbox, label in zip(bboxes, labels):
            writer.addObject(label, bbox[0], bbox[1], bbox[2], bbox[3], difficult=difficult)

    addObject(ann_info['bboxes'], ann_info['labels'])

    if ann_info.get('bboxes_ignore') is not None:
        addObject(ann_info['bboxes_ignore'], ann_info['labels_ignore'], 1)

    writer.save(ann_file)


def parse_single_voc_to_table(ann_file, root=None, min_size=None):
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
        difficult = int(obj.find('difficult').text)

        bnd_box = obj.find('bndbox')
        bbox = [
            int(float(bnd_box.find('xmin').text)),
            int(float(bnd_box.find('ymin').text)),
            int(float(bnd_box.find('xmax').text)),
            int(float(bnd_box.find('ymax').text))
        ]
        ignore = 0

        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if min_size and (w < min_size or h < min_size):
            ignore = 1

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
            'ignore': ignore,
            'difficult': difficult
        }
        table.append(list(row.values()))

    return table


def parse_voc_to_table(ann_dir):
    table = []
    for ann_folder in tqdm(glob.glob(ann_dir)):
        rows = parse_single_voc_to_table(str(ann_folder))
        table.extend(rows)
    table = pd.DataFrame(
        table, columns=['filename', 'img_width', 'img_height', 'img_depth',
                        'bbox_width', 'bbox_height', 'label',
                        'xmin', 'ymin', 'xmax', 'ymax', 'ignore', 'difficult'])
    return table
