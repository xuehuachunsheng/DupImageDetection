# -*- coding: utf-8 -*-

import cv2
import os
import imagehash
from PIL import Image
import argparse
import sys
import numpy as np
import multiprocessing as mp

counter = mp.Value('i', 0)

def map(samples):
    a = []
    global counter
    for sample in samples:
        c_hash = imagehash.phash(Image.open(sample))
        # c_hash = imagehash.phash(Image.open(sample)).convert('RGB')
        a.append([c_hash, sample])
        with counter.get_lock():
            counter.value += 1
            if counter.value % 10 == 0:
                print(counter.value)
    return a

parser = argparse.ArgumentParser(description='This script generates phash of all the images.')

parser.add_argument('--img_dir', help='The director path stores all the images')

parser.add_argument('--n_thread', default=1, help='The number of threads')

parser.add_argument('--out_path', help='The path stores the pHashs of these images')

FLAGS = parser.parse_args()

img_data_path = FLAGS.img_dir


image_names = os.listdir(img_data_path)
image_names = np.sort(image_names)
all_img_paths = [os.path.join(img_data_path, x) for x in image_names]
#split_names = np.split(all_img_paths, [100, 200, 300, 400, 500, 600, 700, 800, 900])

FLAGS.n_thread = 1 if FLAGS.n_thread < 1 else FLAGS.n_thread

if FLAGS.n_thread == 1:
    split_names = [all_img_paths]
    # p／rint("split_names".split_names)
else:
    n = len(all_img_paths)
    jiange = int(n / FLAGS.n_thread)
    split_point = []
    for i in range(1, FLAGS.n_thread):
        split_point.append(i*jiange)
    split_names = np.split(all_img_paths, split_point)
#动态生成多个进程
processS = mp.Pool(processes=len(split_names))

c_results = [[] for i in range(len(split_names))]

queue = mp.Manager().Queue()
#枚举函数；i表示循环下标；block表示从迭代器获取到的元素
for i, block in enumerate(split_names):
    c_results[i] = processS.apply_async(func=map, args=(block, ))
processS.close()
processS.join()

s = ['pHash imageName']

for i, values in enumerate(c_results):
    values = values.get()
    for value in values:
        s.append('\n{} {}'.format(value[0], value[1]))

f = open(FLAGS.out_path, 'w')
f.writelines(s)
f.close()