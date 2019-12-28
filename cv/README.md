- [ ] Anchor聚类
- [ ] 定时获取摄像头照片

## image information format

```text
table format


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
```

### TODO:

- [ ] combine rename, relabel, rmlabel, robust, split, show 