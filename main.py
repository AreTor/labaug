import os.path as osp
import random
import numpy as np
import torch

import config as cfg
from splitter import Splitter
from extractor import Extractor
from augmenter import Augmenter
from trainer import Trainer


class Experiment(object):
    def __init__(self, dset_name, net_names, hard_labels, device, exp=None):
        if exp is None:
            exp = 0
            while osp.exists(osp.join(cfg.DATA_DIR, 'exp_' + str(exp))):
                exp += 1

        self.exp_dir = osp.join(cfg.DATA_DIR, 'exp_' + str(exp))
        self.num_exp = exp

        dset_dir = osp.join(self.exp_dir, dset_name)
        self.splitting_dir = osp.join(dset_dir, cfg.SPLITTING_DIR)
        self.feat_dir = osp.join(dset_dir, cfg.FEATURE_DIR)
        self.label_dir = osp.join(dset_dir, cfg.LABEL_DIR, 'hard' if hard_labels else 'soft')
        self.net_dir = osp.join(dset_dir, cfg.NET_DIR, 'hard' if hard_labels else 'soft')
        self.res_dir = osp.join(dset_dir, cfg.RESULT_DIR, 'hard' if hard_labels else 'soft')

        self.dset = cfg.DSETS[dset_name]

        self.splitter = Splitter(self.dset, self.splitting_dir)
        self.extractor = Extractor(self.dset, self.splitting_dir, self.feat_dir, net_names, device)
        self.augmenter = Augmenter(self.dset, self.splitting_dir, self.feat_dir, self.label_dir, net_names, hard_labels)
        self.trainer = Trainer(self.dset, self.label_dir, self.net_dir, self.res_dir, net_names, hard_labels, device)

    def _set_seeds(self, seed=None):
        random.seed(seed)
        np.random.seed(seed)
        torch.random.manual_seed(seed)
        torch.cuda.random.manual_seed(seed)

    def run(self, steps=None, seed=None, **kwargs):
        """
        perform the label augmentation algorithm

        Inputs:
        steps: the step of the experiment to be perfomed. It accept a list
         containing one or more of these four options:
         'splitter': to generate a splitting of a dataset in train and test
          files
         'extractor': to extract the features of the dataset
         'augmenter': to propagate the label to the unlabeled observations with
          GTG and other algorithms.
         'trainer': to train the network with the propagated labels and check
          the accuracy
         If not set, all the steps are performed.
        seed: the seed to reproduce the experiments
        """
        if steps is None:
            steps = ['splitter', 'extractor', 'augmenter', 'trainer']

        for step in steps:
            self._set_seeds(seed)
            part = getattr(self, step)
            print('running: ' + step)
            part(**kwargs)


if __name__ == '__main__':
    dset_name = 'caltech'
    steps = [
             'splitter',
             'extractor',
             'augmenter',
             'trainer'
    ]

    exp = Experiment(dset_name, net_names=['resnet18'], hard_labels=False, exp=4, device='cuda:0')
    exp.run(steps=steps, seed=314, tr_frac=0.8, exts=['.jpg', 'jpeg', '.png'],
            tr_percs=[0.05], algs=['gtg'], epochs=10, batch_size_tr=64, soft_labels=True)
    # exp = Experiment(dset_name, net_names=['resnet18'], hard_labels=True, device='cuda:0', exp=1)
    # exp.run(steps=steps, seed=314, tr_frac=0.8, exts=['.jpg', 'jpeg', '.png'],
    #         tr_percs=[0.05], algs=['gtg', 'svm', 'labels_only'], epochs=10, batch_size_tr=64,)
