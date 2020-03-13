import argparse
import glob
import os
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, ElementTree
import cv2
import shutil
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_ann', help='source annotations directory path, like[/path/to/directory/*.xml]')
    parser.add_argument('--source_img', help='source images directory path, like[/path/to/directory/*.jpg]')
    parser.add_argument('--show', action='store_true')
    parser.add_argument('--fix', action='store_true')
    args = parser.parse_args()
    return args


def check_img_format(img_dir, fix=False):
    """
    检查每张图片是否是jpg格式，不是则进行转换
    :param img_dir:
    :return:
    """
    print('check image format')
    dirname = os.path.dirname(img_dir)
    imgs = [os.path.basename(x) for x in glob.glob(img_dir)]
    imgs = [os.path.join(dirname, x) for x in imgs]

    for img in imgs:
        preffix = img.split('.')[0]
        suffix = img.split('.')[-1]
        if img.split('.')[-1] != 'jpg':
            print(img, 'format illegal')
            if fix:
                i = cv2.imread(img)

                cv2.imwrite(preffix + '.jpg', i)
                os.remove(img)


def check_img(ann_dir, img_dir):
    """
    检查每张图片是否有对应的xml文件注释
    :param ann_dir:
    :param img_dir:
    :return:
    """
    print('check image and annotation')
    anns = [os.path.basename(x).split('.')[0] for x in glob.glob(ann_dir)]
    imgs = [os.path.basename(x).split('.')[0] for x in glob.glob(img_dir)]
    for img in imgs:
        if not img in anns:
            print(img)
            raise Exception()
    return


def node_content(node, key, astype=None):
    if node is None:
        return None
    content = node.find(key)
    if content is None:
        return content
    content = content.text
    if astype is not None:
        content = astype(content)
    return content
def node_set_text(node_manager:ET.Element, node_child, text):
    node = node_manager.find(node_child)
    if node is None:
        node = SubElement(node_manager, node_child)
    if text is not None:
        node.text = text
    return node


def check_bndbox(ann_dir, img_dir):
    """
    检查每张图片的shape是否和xml中的size一致
    :param ann_dir:
    :param img_dir:
    :return:
    """
    print('check shape')
    anns = glob.glob(ann_dir)
    imgs = os.path.dirname(img_dir)
    for ann in anns:
        tree = ET.parse(ann)
        ann = Path(ann)
        root = tree.getroot()
        # size = root.find('size')
        size = node_set_text(root, 'size', None)

        # width = int(size.find('width').text)
        # height = int(size.find('height').text)
        # depth = int(size.find('depth').text)

        width = node_content(size, 'width', int)
        height = node_content(size, 'height', int)
        depth = node_content(size, 'depth', int)

        # filename = root.find('filename').text
        filename = node_content(root, 'filename', ) or ann.stem
        file_path = os.path.join(imgs, filename)
        try:
            img = cv2.imread(file_path)
            h, w, d = img.shape
            if width != w or height != h or depth != d:
                print(ann, 'shape Inconsistent')
                node_set_text(size, 'width', str(w))
                node_set_text(size, 'height', str(h))
                node_set_text(size, 'depth', str(d))
                tree.write(ann)
        except Exception as e:
            print(e, ann, file_path)

def check_redundent(ann_dir, img_dir):
    """

    :param ann_dir:
    :param img_dir:
    :return:
    """
    print('check redundent')
    anns = glob.glob(ann_dir)
    imgs = os.path.dirname(img_dir)
    for ann in anns:
        tree = ET.parse(ann)
        ann = Path(ann)
        root = tree.getroot()
        size = node_set_text(root, 'size', None)

        tree.write(ann)


def check_ann(ann_dir, fix=False):
    """
    检查xml文件名和文件里面的filename是否一致,filename字段后缀是否是.jpg
    :param ann_dir:
    :param table:
    :return:
    """
    print('check annotation')
    anns = glob.glob(ann_dir)

    for ann in anns:
        tree = ET.parse(ann)

        root = tree.getroot()
        ann = Path(ann)

        filename = node_content(root, 'filename', ) or ann.name
        file_prefix = filename.split('.')[0]
        file_suffix = filename.split('.')[-1]
        ann_prefix = os.path.basename(ann).split('.')[0]
        if file_prefix != ann_prefix or file_suffix != 'jpg':
            if file_prefix != ann_prefix:
                print(ann, file_prefix, 'Inconsistent')
            if file_suffix != 'jpg':
                print(ann, filename, 'suffix is not jpg')
            # shutil.copy(ann, ann+'.bak')
            if fix:
                new_filename = ann_prefix + '.jpg'
                # root.set('filename', new_filename)
                # root.find('filename').text = new_filename
                # root.find('filename').text = new_filename
                node_set_text(root, 'filename', new_filename)
                tree.write(ann)


def main():
    args = parse_args()
    check_img_format(args.source_img, args.fix)
    check_img(args.source_ann, args.source_img)
    check_ann(args.source_ann, args.fix)
    check_shape(args.source_ann, args.source_img)


if __name__ == '__main__':
    main()
