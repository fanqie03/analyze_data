import os
import argparse
import random
import json
from pathlib import Path
import collections
import copy


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-file')
    args = parser.parse_args()
    return args


def add_suffix_and_export(content, source_file,  ann):
    raw_file = Path(source_file)
    output_path = raw_file.parent
    output_file = output_path / (raw_file.stem+'-'+ann+raw_file.suffix)
    with open(output_file, 'w') as f:
         json.dump(content, f, indent=2)


def main():
    args = parse_args()
    content = json.load(open(args.source_file))

    for item in content['images']:
        file_name = item['file_name']
        file_name = Path(file_name).name
        item['file_name'] = file_name

    # json.dump(base, open(args.out))
    add_suffix_and_export(content, args.source_file, 'strip')
    pass



if __name__ == '__main__':
    main()
