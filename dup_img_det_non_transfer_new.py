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

name_phash_mapping_hex = {}
for x in s:
    c_hash = x[0]
    assert len(c_hash) <= 16
    if len(c_hash) < 16:
        supp = ['0'] * (16 - len(c_hash))
        c_hash = ''.join(supp) + c_hash
    assert len(c_hash) == 16

    name_phash_mapping_hex[x[1]] = c_hash


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

def rm_duplicated_imgs(dup_images):

    for x in dup_images:
        c_hash = name_phash_mapping_hex[x]
        assert len(c_hash) == 16
        for m in range(n_split):
            c_part = c_hash[m * int(16 / n_split):(m + 1) * int(16 / n_split)]
            assert x in dicts[m][c_part]
            dicts[m][c_part].remove(x)

repeated_img_urls = {}

repeated_img_urls_set = set()

count = 0
import time
c_time = time.clock()
for count, img_url in enumerate(name_phash_mapping):

    if count % 100 == 0:
        print(count)

    if img_url in repeated_img_urls_set: continue

    c_hash_bin = name_phash_mapping[img_url]
    c_hash = name_phash_mapping_hex[img_url]

    assert len(c_hash) == 16

    for m in range(n_split):
        c_part = c_hash[m * int(16 / n_split):(m + 1) * int(16 / n_split)]
        assert img_url in dicts[m][c_part]
        for ano_img_url in dicts[m][c_part]:
            if ano_img_url == img_url: continue
            ano_hash_bin = name_phash_mapping[ano_img_url]
            num_diff = sum([c_hash_bin[x] != ano_hash_bin[x] for x in range(64)])
            if num_diff <= FLAGS.sim_thres:
                if img_url not in repeated_img_urls:
                    repeated_img_urls[img_url] = set()
                repeated_img_urls[img_url].add(ano_img_url)

    if img_url in repeated_img_urls:
        repeated_img_urls[img_url].add(img_url) # Add itself
        repeated_img_urls_set = repeated_img_urls_set | repeated_img_urls[img_url]
        rm_duplicated_imgs(repeated_img_urls[img_url])

for x, y in combinations(list(repeated_img_urls.values())[:min(len(repeated_img_urls.values()), 1000)], 2):
    assert len(x) >= 2
    assert len(y) >= 2
    assert len(x & y) == 0

repeated_img_urls_list = []
for x in repeated_img_urls:
    repeated_img_urls_list.append(list(repeated_img_urls[x]))

import json
json.dump(repeated_img_urls_list, open(FLAGS.output_path, 'w'))

