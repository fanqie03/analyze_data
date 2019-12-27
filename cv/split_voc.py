import os
import argparse
import random


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_dir')
    parser.add_argument('--output_dir')
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('--ratio', type=float, nargs='+', default=[0.8, 0.1, 0.1],
                        help='[train, val, test] ratio')
    args = parser.parse_args()
    return args


def export(array, file):
    arr_len = len(array)
    with open(file, 'w') as f:
        for i, ele in enumerate(array):
            f.write(ele)
            if arr_len != i+1:
                f.write('\n')


def main():
    args = parse_args()
    random.seed(args.seed)
    files = os.listdir(args.source_dir)
    files = [x.split('.')[0] for x in files]
    random.shuffle(files)
    length = len(files)
    stride = [int(x * length) for x in args.ratio]

    train_part = files[:stride[0]]
    val_part = files[stride[0]: stride[0]+stride[1]]
    train_val_part = files[:stride[0]+stride[1]]
    test_part = files[stride[0]+stride[1]:]

    parts = [train_part, val_part, train_val_part, test_part]
    texts = ['train.txt', 'val.txt', 'trainval.txt', 'test.txt']
    for part, txt in zip(parts, texts):
        export(part, os.path.join(args.output_dir, txt))


if __name__ == '__main__':
    main()
