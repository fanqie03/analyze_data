# -*- coding=utf-8 -*-
#!/usr/bin/python
# reference from https://blog.csdn.net/m_buddy/article/details/90348194
import sys
import os
import shutil
import numpy as np
import json
import xml.etree.ElementTree as ET
import argparse
import time
import copy

# 检测框的ID起始值
START_BOUNDING_BOX_ID = 1
# 类别列表无必要预先创建，程序中会根据所有图像中包含的ID来创建并更新
PRE_DEFINE_CATEGORIES = {}
# If necessary, pre-define category and its id
#  PRE_DEFINE_CATEGORIES = {"aeroplane": 1, "bicycle": 2, "bird": 3, "boat": 4,
                         #  "bottle":5, "bus": 6, "car": 7, "cat": 8, "chair": 9,
                         #  "cow": 10, "diningtable": 11, "dog": 12, "horse": 13,
                         #  "motorbike": 14, "person": 15, "pottedplant": 16,
                         #  "sheep": 17, "sofa": 18, "train": 19, "tvmonitor": 20}

ID_MAP = dict()
IMAGE_ID = 0

# 标注基本结构
BASE = {
    "info": {
        "contributor": "",
        "date_created": time.strftime("%Y-%m-%d", time.localtime()),
        "description": "voc2coco",
        "url": "",
        "version": 1,
        "year": time.strftime("%Y", time.localtime())
    },
    "licenses": [
        {
            "name": "",
            "id": 0,
            "url": ""
        }
    ],
    "images": [],
     "type": "instances",
     "annotations": [],
     "categories": []
}

def get_args():
    args = argparse.ArgumentParser()
    args.add_argument('--xml-dir')
    args.add_argument('--target-dir')
    args.add_argument('--ratio', nargs='+', default=[0.8, 0.1, 0.1])
    return args.parse_args()


def get(root, name):
    vars = root.findall(name)
    return vars


def get_and_check(root, name, length):
    vars = root.findall(name)
    if len(vars) == 0:
        raise NotImplementedError('Can not find %s in %s.'%(name, root.tag))
    if length > 0 and len(vars) != length:
        raise NotImplementedError('The size of %s is supposed to be %d, but is %d.'%(name, length, len(vars)))
    if length == 1:
        vars = vars[0]
    return vars




# 得到图片唯一标识号
def get_filename_as_int(filename):
    global IMAGE_ID
    id = ID_MAP.get(filename)
    if id is None:
        id = IMAGE_ID
        ID_MAP[filename] = id
        IMAGE_ID += 1
    return id


def convert(xml_list, xml_dir, json_file):
    '''
    :param xml_list: 需要转换的XML文件列表
    :param xml_dir: XML的存储文件夹
    :param json_file: 导出json文件的路径
    :return: None
    '''
    list_fp = xml_list
    # 标注基本结构
    json_dict = copy.deepcopy(BASE)
    categories = PRE_DEFINE_CATEGORIES
    bnd_id = START_BOUNDING_BOX_ID
    for line in list_fp:
        line = line.strip()
        print("buddy~ Processing {}".format(line))
        # 解析XML
        xml_f = os.path.join(xml_dir, line)
        tree = ET.parse(xml_f)
        root = tree.getroot()
        path = get(root, 'path')
        # 取出图片名字
        if len(path) == 1:
            filename = os.path.basename(path[0].text)
        elif len(path) == 0:
            filename = get_and_check(root, 'filename', 1).text
        else:
            raise NotImplementedError('%d paths found in %s'%(len(path), line))
        ## The filename must be a number
        image_id = get_filename_as_int(filename)  # 图片ID
        size = get_and_check(root, 'size', 1)
        # 图片的基本信息
        width = int(get_and_check(size, 'width', 1).text)
        height = int(get_and_check(size, 'height', 1).text)
        image = {'file_name': filename,
                 'height': height,
                 'width': width,
                 'id':image_id}
        json_dict['images'].append(image)
        ## Cruuently we do not support segmentation
        #  segmented = get_and_check(root, 'segmented', 1).text
        #  assert segmented == '0'
        # 处理每个标注的检测框
        for obj in get(root, 'object'):
            # 取出检测框类别名称
            category = get_and_check(obj, 'name', 1).text
            # 更新类别ID字典
            if category not in categories:
                new_id = len(categories)
                categories[category] = new_id
            category_id = categories[category]
            bndbox = get_and_check(obj, 'bndbox', 1)
            xmin = int(float(get_and_check(bndbox, 'xmin', 1).text)) - 1
            ymin = int(float(get_and_check(bndbox, 'ymin', 1).text)) - 1
            xmax = int(float(get_and_check(bndbox, 'xmax', 1).text))
            ymax = int(float(get_and_check(bndbox, 'ymax', 1).text))
            assert(xmax > xmin)
            assert(ymax > ymin)
            o_width = abs(xmax - xmin)
            o_height = abs(ymax - ymin)
            annotation = dict()
            annotation['area'] = o_width*o_height
            annotation['iscrowd'] = 0
            annotation['image_id'] = image_id
            annotation['bbox'] = [xmin, ymin, o_width, o_height]
            annotation['category_id'] = category_id
            annotation['id'] = bnd_id
            annotation['ignore'] = 0
            # 设置分割数据，点的顺序为逆时针方向
            annotation['segmentation'] = [[xmin,ymin,xmin,ymax,xmax,ymax,xmax,ymin]]

            json_dict['annotations'].append(annotation)
            bnd_id = bnd_id + 1

    # 写入类别ID字典
    for cate, cid in categories.items():
        cat = {'supercategory': 'none', 'id': cid, 'name': cate}
        json_dict['categories'].append(cat)
    # 导出到json
    json_fp = open(json_file, 'w')
    json_str = json.dumps(json_dict, indent=2)
    json_fp.write(json_str)
    json_fp.close()


if __name__ == '__main__':
    args = get_args()
    xml_dir = args.xml_dir

    xml_labels = os.listdir(xml_dir)
    xml_labels = [x for x in xml_labels if x.find('.xml') != -1]
    length = len(xml_labels)
    stride = [int(x * length) for x in args.ratio]
    np.random.shuffle(xml_labels)
    split_point = int(len(xml_labels)/10)

    # validation data
    xml_list = xml_labels[:stride[0]]
    json_file = os.path.join(args.target_dir, './train.json')
    convert(xml_list, xml_dir, json_file)
    # train data
    xml_list = xml_labels[stride[0]: stride[0]+stride[1]]
    json_file = os.path.join(args.target_dir, './val.json')
    convert(xml_list, xml_dir, json_file)

    # train data
    xml_list = xml_labels[:stride[0]+stride[1]]
    json_file = os.path.join(args.target_dir, './trainval.json')
    convert(xml_list, xml_dir, json_file)

    # train data
    xml_list = xml_labels[stride[0]+stride[1]:]
    json_file = os.path.join(args.target_dir, './test.json')
    convert(xml_list, xml_dir, json_file)

    map_file = os.path.join(args.target_dir, './map.json')
    json.dump(ID_MAP, open(map_file, 'wt'), indent=2)
