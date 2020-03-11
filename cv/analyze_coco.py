import os
import argparse
import random
import json
from pathlib import Path
import collections
import copy
import pandas as pd
from pandas_profiling import ProfileReport


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-file')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    content = json.load(open(args.source_file))
    source_file = Path(args.source_file)

    image_df = pd.DataFrame(content['images'])
    print(len(image_df), len(image_df.id.unique()))
    profile = ProfileReport(image_df)
    profile.to_file(source_file.parent / 'images.html')
    annotation_df = pd.DataFrame(content['annotations'])
    profile = ProfileReport(annotation_df)
    profile.to_file(source_file.parent / 'annotations.html')
    print(len(annotation_df))


if __name__ == '__main__':
    main()
