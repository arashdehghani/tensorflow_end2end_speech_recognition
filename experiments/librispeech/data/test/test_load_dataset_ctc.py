#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re
import sys
import unittest

sys.path.append('../../../../')
from experiments.librispeech.data.load_dataset_ctc import Dataset
from experiments.utils.data.labels.character import num2char
from experiments.utils.data.labels.word import num2word
from experiments.utils.measure_time_func import measure_time


class TestLoadDatasetCTC(unittest.TestCase):

    def test(self):
        # label_type
        self.check_loading(label_type='character', num_gpu=1, sort_utt=False)
        self.check_loading(label_type='character_capital_divide', num_gpu=1,
                           sort_utt=False)
        self.check_loading(label_type='word', num_gpu=1, sort_utt=False)

        # sort
        self.check_loading(label_type='character', num_gpu=1, sort_utt=True)
        self.check_loading(label_type='character', num_gpu=1,
                           sort_utt=False, sort_stop_epoch=True)

        # multi-GPU
        self.check_loading(label_type='character', num_gpu=2, sort_utt=False)
        self.check_loading(label_type='character', num_gpu=8, sort_utt=False)

    @measure_time
    def check_loading(self, label_type, num_gpu, sort_utt, sort_stop_epoch=None):
        print('----- label_type: %s, num_gpu: %d, sort_utt: %s, sort_stop_epoch: %s -----' %
              (label_type, num_gpu, str(sort_utt), str(sort_stop_epoch)))

        dataset = Dataset(data_type='dev_clean',
                          train_data_size='train_clean100',
                          label_type=label_type, batch_size=64,
                          num_stack=3, num_skip=3,
                          sort_utt=sort_utt, sort_stop_epoch=sort_stop_epoch,
                          progressbar=True, num_gpu=num_gpu, is_gpu=False)

        print('=> Loading mini-batch...')
        if label_type == 'character':
            map_file_path = '../../metrics/mapping_files/ctc/character2num.txt'
            map_fn = num2char
        elif label_type == 'character_capital_divide':
            map_file_path = '../../metrics/mapping_files/ctc/character2num_capital.txt'
            map_fn = num2char
        elif label_type == 'word':
            map_file_path = '../../metrics/mapping_files/ctc/word2num_train_other500.txt'
            map_fn = num2word

        for data, next_epoch_flag in dataset():
            inputs, labels, inputs_seq_len, input_names = data

            for inputs_gpu in inputs:
                print(inputs_gpu.shape)

            if label_type == 'word':
                word_list = num2word(labels[0][0], map_file_path)
                str_true = ' '.join(word_list)
            else:
                str_true = map_fn(labels[0][0], map_file_path)
                str_true = re.sub(r'_', ' ', str_true)
            print('----- %s -----' % input_names[0][0])
            print(str_true)

            if next_epoch_flag:
                break


if __name__ == '__main__':
    unittest.main()