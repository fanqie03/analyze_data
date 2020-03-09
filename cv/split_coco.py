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


def add_suffix(path, ann):
    raw_file = Path(path)
    return raw_file.parent / (raw_file.stem+'-'+ann+raw_file.suffix)

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

    train_annotations_part = all_images[:stride[0]]
    val_annotations_part = all_images[stride[0]: stride[0]+stride[1]]
    trainval_annotations_part = all_images[:stride[0]+stride[1]]
    test_annotations_part = all_images[stride[0]+stride[1]:]

    train_dict = dict(info=all_['info'], licenses=all_['licenses'], categories=all_['categories'], images=train_images_part, annotations=train_annotations_part)
    val_dict = dict(base).update({'images': val_images_part, 'annotations': val_annotations_part})
    trainval_dict = dict(base).update({'images': trainval_images_part, 'annotations': trainval_annotations_part})
    test_dict = dict(base).update({'images': test_images_part, 'annotations': test_annotations_part})




    pass

    # train_part = files[:stride[0]]
    # val_part = files[stride[0]: stride[0]+stride[1]]
    # train_val_part = files[:stride[0]+stride[1]]
    # test_part = files[stride[0]+stride[1]:]
    #
    # parts = [train_part, val_part, train_val_part, test_part]
    # texts = ['train.txt', 'val.txt', 'trainval.txt', 'test.txt']
    # for part, txt in zip(parts, texts):
    #     export(part, os.path.join(args.output_dir, txt))


if __name__ == '__main__':
    main()
