#-*- coding:utf-8 -*-
from itertools import combinations
import argparse
import os
parser = argparse.ArgumentParser(description='These is a duplicated images detection program. You need to provide pHashs of all images.')

parser.add_argument('--pHashs_path', default='/data/public/liangtan/bangdan/pHashs_jd.txt', help='The file path of pHashs for all images, where the first line is "pHash imageName"')

parser.add_argument('--sim_thres', default=3, help='If the number of different digits of two images is less or equal than sim_thres, they are duplicated.')

parser.add_argument('--output_path', default='', help='The output path stores repeated images list, each of which is a list that stores a group of duplicated images. Default it will be current_path/duplicated_images.json')

FLAGS = parser.parse_args()

FLAGS.sim_thres = 0 if FLAGS.sim_thres < 0 else FLAGS.sim_thres

if FLAGS.output_path == '':
    FLAGS.output_path = os.path.join(os.path.split(FLAGS.pHashs_path)[0], 'duplicated_images_jd.json')

with open(FLAGS.pHashs_path, 'r') as f:
    s = []
    f.readline()
    for x in f:
        s.append(x.strip().split(' '))

name_phash_mapping = {}
for x in s:
    name_phash_mapping[x[1]] = '{:064d}'.format(int(bin(int(x[0], 16))[2:]))

n_split = 4

def gen_dicts(s):

    dicts = [{} for i in range(n_split)]

    for i in range(n_split):
        for x in s:
            c_part = x[0][i*int(16/n_split):(i+1)*int(16/n_split)]
            if c_part not in dicts[i]:
                dicts[i][c_part] = set()
            assert x[1] not in dicts[i][c_part], x[1]
            dicts[i][c_part].add(x[1])
    return dicts

dicts = gen_dicts(s)

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

def dup_det(img_list):
    marked_repeated_imgs = set()

    for img1, img2 in combinations(img_list, 2):
        # core judgement
        if img2 in marked_repeated_imgs: continue

        assert img1 != img2, '{}\n{}'.format(img1, img2)
        img1_finger = name_phash_mapping[img1]
        img2_finger = name_phash_mapping[img2]
        num_diff = sum([img1_finger[x] != img2_finger[x] for x in range(64)])
        if num_diff <= int(FLAGS.sim_thres):  # The number of different finger digits
            if img1 not in repeated_img_urls:
                repeated_img_urls[img1] = set()
            repeated_img_urls[img1].add(img2)
            marked_repeated_imgs.add(img1)  # Mark the j-th location image duplicated
            marked_repeated_imgs.add(img2)

    return marked_repeated_imgs

def rm_repeated_ref(repeated_imgs):

    for c_img in repeated_imgs:
        c_hash = name_phash_mapping[c_img]  # 2进制

        c_hash = hex(int(c_hash, 2))[2:]  # 16进制
        assert len(c_hash) <= 16
        if len(c_hash) < 16:
            supp = ['0'] * (16 - len(c_hash))
            c_hash = ''.join(supp) + c_hash
        assert len(c_hash) == 16
        for m in range(n_split):
            c_part = c_hash[m * int(16 / n_split):(m + 1) * int(16 / n_split)]
            # print(m)
            # print(dicts[m][c_part])
            assert c_img in dicts[m][c_part]
            dicts[m][c_part].remove(c_img)

count = 0
for n in range(n_split):
    for img_list in dicts[n].values():
        count += 1
        if count % 100 == 0:
            print(count)

        marked_repeated_imgs = dup_det(img_list)

        # Remove other references of the repeated images
        rm_repeated_ref(marked_repeated_imgs)

for k, v in repeated_img_urls.items():
    v.add(k)

for x in repeated_img_urls:
    c_values = repeated_img_urls[x]
    for y in c_values:
        if y != x: assert y not in repeated_img_urls

for x, y in combinations(list(repeated_img_urls.values())[:min(len(repeated_img_urls.values()), 1000)], 2):
    assert len(x) >= 2
    assert len(y) >= 2
    assert len(x & y) == 0

repeated_img_urls_list = []
for x in repeated_img_urls:
    repeated_img_urls_list.append(list(repeated_img_urls[x]))

# sum1 = sum([len(x) for x in repeated_img_urls_list])
#
# a = set()
# for x in repeated_img_urls_list:
#     for y in x:
#         a.add(y)
#
# assert len(a) == sum1, 'Unknown error.'
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
