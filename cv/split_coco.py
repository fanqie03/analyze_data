import os
import argparse
import random
import json
from pathlib import Path
import collections


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-file')
    parser.add_argument('--output-dir')
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('--ratio', type=float, nargs='+', default=[0.8, 0.1, 0.1],
                        help='[train, val, test] ratio')
    args = parser.parse_args()
    return args


def add_suffix_and_export(content, source_file, output_path, ann):
    raw_file = Path(source_file)
    output_path = Path(output_path)
    output_file = output_path / (raw_file.stem+'-'+ann+raw_file.suffix)
    with open(output_file, 'w') as f:
         json.dump(content, f, indent=2)

# def export(dic, args):
#     with open('')
#     arr_len = len(array)
#     with open(file, 'w') as f:
#         for i, ele in enumerate(array):
#             f.write(ele)
#             if arr_len != i+1:
#                 f.write('\n')

def create_index(content, id_name):
    ret = {}
    for item in content:
        id = item.get(id_name)
        if ret.get(id) is None:
            ret[id] = []
        ret[id].append(item)
    ret = collections.OrderedDict(ret)
    return ret


def part_merge(part):
    ret = []
    [ret.extend(x[1]) for x in part]
    return ret


def main():
    args = parse_args()
    assert(len(args.ratio) == 3)
    random.seed(args.seed)
    all_ = json.load(open(args.source_file))
    all_images_ = all_['images']
    all_annotations_ = all_['annotations']
    all_images_index = create_index(all_images_, 'id')
    all_annotations_index = create_index(all_annotations_, 'image_id')
    all_images = list(all_images_index.items())
    all_annotations = list(all_annotations_index.items())

    base = dict(info=all_['info'], licenses=all_['licenses'], categories=all_['categories'], images=None, annotations=None)

    for i, j in zip(all_images, all_annotations):
        assert(i[0] == j[0])


    length = len(all_images)
    stride = [int(x * length) for x in args.ratio]

    train_images_part = all_images[:stride[0]]
    val_images_part = all_images[stride[0]: stride[0]+stride[1]]
    trainval_images_part = all_images[:stride[0]+stride[1]]
    test_images_part = all_images[stride[0]+stride[1]:]

    train_images_part = part_merge(train_images_part)
    val_images_part = part_merge(val_images_part)
    trainval_images_part = part_merge(trainval_images_part)
    test_images_part = part_merge(test_images_part)

    train_annotations_part = all_annotations[:stride[0]]
    val_annotations_part = all_annotations[stride[0]: stride[0]+stride[1]]
    trainval_annotations_part = all_annotations[:stride[0]+stride[1]]
    test_annotations_part = all_annotations[stride[0]+stride[1]:]

    train_annotations_part = part_merge(train_annotations_part)
    val_annotations_part = part_merge(val_annotations_part)
    trainval_annotations_part = part_merge(trainval_annotations_part)
    test_annotations_part = part_merge(test_annotations_part)

    train_dict = dict(info=all_['info'], licenses=all_['licenses'], categories=all_['categories'], images=train_images_part, annotations=train_annotations_part)
    val_dict = dict(info=all_['info'], licenses=all_['licenses'], categories=all_['categories'], images=val_images_part, annotations=val_annotations_part)
    trainval_dict = dict(info=all_['info'], licenses=all_['licenses'], categories=all_['categories'], images=trainval_images_part, annotations=trainval_annotations_part)
    test_dict = dict(info=all_['info'], licenses=all_['licenses'], categories=all_['categories'], images=test_images_part, annotations=test_annotations_part)

    add_suffix_and_export(train_dict, args.source_file, args.output_dir, 'train')
    add_suffix_and_export(val_dict, args.source_file, args.output_dir, 'val')
    add_suffix_and_export(trainval_dict, args.source_file, args.output_dir, 'trainval')
    add_suffix_and_export(test_dict, args.source_file, args.output_dir, 'test')
    add_suffix_and_export(all_, args.source_file, args.output_dir, 'raw')

    pass

if __name__ == '__main__':
    main()
