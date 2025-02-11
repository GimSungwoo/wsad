import torch
import torch.utils.data as data_utl
from torch.utils.data.dataloader import default_collate

import numpy as np
import json
import random
import os
import os.path

def make_dataset(split_file, split, root, mode, num_classes=157):
    dataset = []
    with open(split_file, 'r') as f:
        data = json.load(f)
    with open('num_frames_' + mode + '.json', 'r') as infile:
        dict_num_frames = json.load(infile)
        
    i = 0
    for vid in data.keys():
        if data[vid]['subset'] != split:
            continue
        
        if not os.path.exists(os.path.join(root, vid)+'.npy'):
            continue
        num_frames = 25
        
        label = np.zeros((num_classes,num_frames), np.float32)
        
        fps = num_frames/data[vid]['duration']
        for ann in data[vid]['actions']: # label every frame by binary code for all classes
            for fr in range(0,num_frames,1):
                if fr/fps >= ann[1] and fr/fps <= ann[2]:
                    label[ann[0], fr] = 1 # binary classification
        dataset.append((vid, label, data[vid]['duration'], dict_num_frames[vid]))
        i += 1
    return dataset


class Charades(data_utl.Dataset):

    def __init__(self, split_file, split, root, mode, transforms=None):
        
        self.data = make_dataset(split_file, split, root, mode)
        self.split_file = split_file
        self.transforms = transforms
        self.mode = mode
        self.root = root

    def __getitem__(self, index):
        """
        Args:
            index (int): Index

        Returns:
            tuple: (image, target) where target is class_index of the target class.
        """
        vid, label, dur, nf = self.data[index]
        start_f = 0
        feature = np.load(os.path.join(self.root, vid) + '.npy')
        return torch.from_numpy(feature[:, np.round(np.linspace(start_f, nf-1, 64)).astype(int), :]), torch.from_numpy(label), vid

    def __len__(self):
        return len(self.data)
