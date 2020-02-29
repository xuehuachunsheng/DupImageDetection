#-*- coding:utf-8 -*-
from itertools import combinations
import argparse
import os
parser = argparse.ArgumentParser(description='Query if an image or an image directory is duplicated in the image phash index base.')

parser.add_argument('--input_path', help='The file path of an image or an image directory.')

parser.add_argument('--img_base_path', help='The file path stores the phash index of image base')

parser.add_argument('--sim_thres', type=int, default=1, help='If the number of different digits of two images is less or equal than sim_thres, they are duplicated.')

parser.add_argument('--output_path', default='', help='The output result is a json file in which stores the duplicated images of input_path in img_base_path. '
                                                      'It is a dict. The key is an input image absolute path, and the corresponding value is the list of duplicated images.'
                                                      'Default is {input_base_path}/queried_result.json')

FLAGS = parser.parse_args()

FLAGS.sim_thres = 0 if FLAGS.sim_thres < 0 else FLAGS.sim_thres

if FLAGS.output_path == '':
    FLAGS.output_path = os.path.join(os.path.split(FLAGS.input_path)[0], 'queried_result.json')

import json
base = json.load(open(FLAGS.img_base_path))

queried_imgs = None
if os.path.isfile(FLAGS.input_path):
    queried_imgs = [FLAGS.input_path]
else:
    queried_imgs = [os.path.join(FLAGS.input_path, x) for x in os.listdir(FLAGS.input_path)]

assert queried_imgs is not None, 'Error. The input is not an image or image directory'

import imagehash
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
re_json = {}
n_split = 4
for image in queried_imgs:
    re_json[image] = set()
    print('Query {}'.format(image))
    c_hash = imagehash.phash(Image.open(image))
    c_hash = str(c_hash)
    c_hash_bin = '{:064d}'.format(int(bin(int(c_hash, 16))[2:]))
    for i in range(n_split):
        c_part = c_hash[i*int(16/n_split):(i+1)*int(16/n_split)]
        if c_part in base[i]:
            for may_dup_img in base[i][c_part]:
                if may_dup_img in re_json[image]: continue
                ano_hash = imagehash.phash(Image.open(may_dup_img))
                ano_hash = str(ano_hash)
                ano_hash_bin = '{:064d}'.format(int(bin(int(ano_hash, 16))[2:]))
                num_diff = sum([c_hash_bin[i] != ano_hash_bin[i] for i in range(64)])
                if num_diff <= int(FLAGS.sim_thres):
                    re_json[image].add(may_dup_img)

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

json.dump(re_json, open(FLAGS.output_path, 'w'), cls=SetEncoder)
