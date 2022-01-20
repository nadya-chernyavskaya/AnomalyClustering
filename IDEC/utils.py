# -*- coding: utf-8 -*-
#
# Copyright © dawnranger.
#
# 2018-05-08 10:15 <dawnranger123@gmail.com>
#
# Distributed under terms of the MIT license.
from __future__ import division, print_function
import numpy as np
import torch
from torch.utils.data import Dataset
from  torch_geometric.data import Dataset as PyGDataset

#from linear_assignment_ import linear_assignment
from scipy.optimize import linear_sum_assignment


#def load_mnist(path='./IDEC_pytorch/data/mnist.npz'):
def load_mnist(path='./data/mnist.npz'):

    f = np.load(path)

    x_train, y_train, x_test, y_test = f['x_train'], f['y_train'], f[
        'x_test'], f['y_test']
    f.close()
    x = np.concatenate((x_train, x_test))
    y = np.concatenate((y_train, y_test)).astype(np.int32)
    x = x.reshape((x.shape[0], -1)).astype(np.float32)
    x = np.divide(x, 255.)
    print('MNIST samples', x.shape)
    return x, y


class MnistDataset(Dataset):

    def __init__(self):
        self.x, self.y = load_mnist()

    def __len__(self):
        return self.x.shape[0]

    def __getitem__(self, idx):
        return torch.from_numpy(np.array(self.x[idx])), torch.from_numpy(
            np.array(self.y[idx])), torch.from_numpy(np.array(idx))


class GraphDataset(PyGDataset):
    def __init__(self, datas, transform=None, pre_transform=None):
        super().__init__(transform=None, pre_transform=None)

        self.datas=datas 

    def len(self):
        return len(self.datas)

    def get_data(self):
        self.x = torch.from_numpy(np.stack([self.datas[i].x for i in range(len(self.datas))],axis=0)) 
        self.y = torch.from_numpy(np.stack([self.datas[i].y for i in range(len(self.datas))],axis=0))
        self.y = torch.squeeze(self.y,dim=-1)
        self.edge_index = torch.from_numpy(np.stack([self.datas[i].edge_index for i in range(len(self.datas))],axis=0))
        return self.x, self.y, self.edge_index

    def get(self, idx):
        return self.datas[idx]



#######################################################
# Evaluate Critiron
#######################################################


def cluster_acc(y_true, y_pred):
    """
    Calculate clustering accuracy. Require scikit-learn installed

    # Arguments
        y: true labels, numpy.array with shape `(n_samples,)`
        y_pred: predicted labels, numpy.array with shape `(n_samples,)`

    # Return
        accuracy, in [0,1]
        reassignment dictionary 
    """
    y_true = y_true.astype(np.int64)
    assert y_pred.size == y_true.size
    D = max(y_pred.max(), y_true.max()) + 1
    w = np.zeros((D, D), dtype=np.int64)
    for i in range(y_pred.size):
        w[y_pred[i], y_true[i]] += 1
#    ind = linear_assignment(w.max() - w)
#    return sum([w[i, j] for i, j in ind]) * 1.0 / y_pred.size

    row_ind, col_ind = linear_sum_assignment(w.max() - w) #difference because we want to maximise the matching, e.g. minimize the cost (orginal problem)
    reassignment = dict(zip(row_ind, col_ind))
    accuracy = w[row_ind, col_ind].sum() / y_pred.size
    return accuracy, reassignment 