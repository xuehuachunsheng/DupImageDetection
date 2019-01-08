#-*- coding:utf-8 -*-
from itertools import combinations
import argparse
import os
parser = argparse.ArgumentParser(description='These is a duplicated images detection program. You need to provide pHashs of all images.')

parser.add_argument('--pHashs_path', default='/data/public/liangtan/bangdan/phashs_taobao.txt', help='The file path of pHashs for all images, where the first line is "pHash imageName"')

parser.add_argument('--sim_thres', default=2, help='If the number of different digits of two images is less or equal than sim_thres, they are duplicated.')

parser.add_argument('--output_path', default='', help='The output path stores repeated images list, each of which is a list that stores a group of duplicated images. Default it will be current_path/duplicated_images.json')

FLAGS = parser.parse_args()

FLAGS.sim_thres = 0 if FLAGS.sim_thres < 0 else FLAGS.sim_thres

if FLAGS.output_path == '':
    FLAGS.output_path = os.path.join(os.path.split(FLAGS.pHashs_path)[0], 'duplicated_images.json')

with open(FLAGS.pHashs_path, 'r') as f:
    s = []
    f.readline()
    for x in f:
        s.append(x.strip().split(' '))

name_phash_mapping = {}
for x in s:
    name_phash_mapping[x[1]] = '{:064d}'.format(int(bin(int(x[0], 16))[2:]))

n_split = 4
#Error
#dicts = [{}] * n_split
dicts = [{} for i in range(n_split)]

for i in range(n_split):
    for x in s:
        c_part = x[0][i*int(16/n_split):(i+1)*int(16/n_split)]
        if c_part not in dicts[i]:
            dicts[i][c_part] = []
        assert x[1] not in dicts[i][c_part], x[1]
        dicts[i][c_part].append(x[1])
print(dicts)
# a = []
# for dict in dicts:
#     a.append(max([len(v) for v in dict.values()]))
# max_v = max(a)
# print(max_v)
# import sys
# sys.exit(0)

# 重复图片存储
# key: an img url, value: a set stored repeated images wrt. the key
repeated_img_urls = {}

count = 0
for i in range(n_split):
    for img_list in dicts[i].values():
        count += 1
        if count % 100 == 0:
            print(count)

        if len(img_list) < 2: continue

        for img1, img2 in combinations(img_list, 2):
            assert img1 != img2, '{}\n{}'.format(img1, img2)
            img1_finger = name_phash_mapping[img1]
            img2_finger = name_phash_mapping[img2]
            num_diff = sum([img1_finger[i] != img2_finger[i] for i in range(64)])
            if num_diff <= int(FLAGS.sim_thres): # The number of different finger digits
                if img1 not in repeated_img_urls and img2 not in repeated_img_urls:
                    t_img_set = set([img1, img2])
                    repeated_img_urls[img1] = t_img_set
                    repeated_img_urls[img2] = t_img_set # The same reference
                elif img1 not in repeated_img_urls:
                    repeated_img_urls[img2].add(img1)
                    repeated_img_urls[img1] = repeated_img_urls[img2]
                elif img2 not in repeated_img_urls:
                    repeated_img_urls[img1].add(img2)
                    repeated_img_urls[img2] = repeated_img_urls[img1]
                else:
                    repeated_img_urls[img1].add(img2)
                    repeated_img_urls[img2].add(img1)
                    repeated_img_urls[img1] = repeated_img_urls[img1] | repeated_img_urls[img2]

                    # Any other keys will change to this set.
                    # Broadcast to other imgs
                    for img in repeated_img_urls[img1]:
                        repeated_img_urls[img] = repeated_img_urls[img1]

for x in repeated_img_urls.values():
    listx = list(x)
    assert len(listx) == len(x)
    c = repeated_img_urls[listx[0]]
    for y in listx:
        assert repeated_img_urls[y] == c

repeated_img_urls_set = []
for x in repeated_img_urls:
    assert len(repeated_img_urls[x]) >= 2
    if repeated_img_urls[x] not in repeated_img_urls_set:
        repeated_img_urls_set.append(repeated_img_urls[x])

repeated_img_urls_list = []
for x in repeated_img_urls_set:
    repeated_img_urls_list.append(list(x))

sum1 = sum([len(x) for x in repeated_img_urls_list])

a = set()
for x in repeated_img_urls_list:
    for y in x:
        a.add(y)

assert len(a) == sum1, 'Unknown error.'
#repeated_img_urls_list = sorted(repeated_img_urls_list, key=lambda x: len(x))[-1]

# import matplotlib.pyplot as plt
# from PIL import Image
# plt.figure()
# for i, x in enumerate(repeated_img_urls_list):
#     if i >= 10: break
#     plt.subplot(5, 2, i+1)
#     plt.imshow(Image.open(x))
#
# plt.show()

import json
json.dump(repeated_img_urls_list, open(FLAGS.output_path, 'w'))
