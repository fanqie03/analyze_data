# analyze_data

- cv/strip_coco.py - 去掉coco json注释中的images.file_name中的路径
```bash
python cv/strip_coco.py --source-file /datasets/pikachu-coco-val.json
```
- cv/split_coco.py - 分割coco json注释
```bash
python cv/split_coco.py --source-file /datasets/pikachu-coco.json --output-dir /datasets
```
- cv/merge_coco.py - 合并coco json注释，会把对应的id * 10并加上个位数
```bash
python cv/merge_coco.py --source-files /datasets/instances_val2017-small.json /datasets/instances_val2017-small.json
```
- cv/show_cov.py - 浏览voc注释
```bash
python cv/show_voc.py --source_ann "/home/cmf/share/GDUT-HWD/Annotations/*.xml" --source_img "/home/cmf/share/GDUT-HWD/JPEGImages/*.jpg"
```
- cv/robust_voc.py - 检查和修复voc异常
    - 检查每张图片是否是jpg格式，不是则进行转换
    - 检查每张图片是否有对应的xml文件注释
    - 检查每张图片的shape是否和xml中的size一致
    - 检查xml文件名和文件里面的filename是否一致,filename字段后缀是否是.jpg
```bash
python cv/robust_voc.py \
--source_ann xxx \
--source_img xxx \
--fix
```
- cv/split_voc.py - 切割voc数据集
```bash
python cv/split_voc.py --source-file /datasets/pikachu-coco.json --output-dir /datasets
```
- cv/extract_file_by_id.py - 从img_dir目录中提取ann_dir目录下的存在的stem，提取到target_dir下
```bash
python cv/extract_file_by_id.py --img_dir xxx --ann_dir xxx --target_dir xxx
```
- cv/voc2coco.py - Pascal VOC数据格式转COCO数据格式脚本
```bash
--xml-dir /datasets/PikachuVOC/Annotations --target-dir /datasets/PikachuVOC/coco
```