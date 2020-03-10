import os
import argparse
import random
import json
from pathlib import Path
import collections
import copy


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-files', nargs='+')
    parser.add_argument('--output-file')
    args = parser.parse_args()
    return args


def add_suffix_and_export(content, source_file,  ann):
    raw_file = Path(source_file)
    output_path = raw_file.parent
    output_file = output_path / (raw_file.stem+'-'+ann+raw_file.suffix)
    with open(output_file, 'w') as f:
         json.dump(content, f, indent=2)


def id_add_suffix(array, id_name, suffix_num):
    for item in array:
        id = item.get(id_name) * 10 + suffix_num
        item[id_name] = id


def main():
    args = parse_args()
    contents = [json.load(open(x)) for x in args.source_files]

    [id_add_suffix(x['images'], 'id', y) for x, y in zip(contents, range(len(contents)))]
    [id_add_suffix(x['annotations'], 'image_id', y) for x, y in zip(contents, range(len(contents)))]

    base = copy.deepcopy(contents[0])
    contents = contents[1:]

    for content in contents:
        base['images'].extend(content['images'])
        base['annotations'].extend(content['annotations'])

    # json.dump(base, open(args.out))
    add_suffix_and_export(base, args.source_files[0], 'merge')
    pass



if __name__ == '__main__':
    main()
