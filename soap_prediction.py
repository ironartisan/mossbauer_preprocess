from ase.build import bulk
from ase import Atom, Atoms
from dscribe.descriptors import SOAP
import random
import numpy as np

seed = 1234
random.seed(seed)
np.random.seed(seed)

train_ratio = 0.8
vali_ratio = 0.1

rcut = 6.0
nmax = 8
lmax = 6

from ase.db import connect
predict_item = 'eta'
db_name = 'mossbauer.db'
db = connect(db_name)

import torch
torch.manual_seed(seed)
torch.cuda.manual_seed(seed)
torch.set_default_tensor_type(torch.DoubleTensor)

import torch.nn as nn
import torch.nn.functional as F

class Model(nn.Module):
    def __init__(self, input_node):
        super(Model, self).__init__()
        self.fc1 = nn.Linear(input_node, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, 32)
        self.fc5 = nn.Linear(32, 1)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = F.relu(self.fc4(x))
        x = self.fc5(x)
        return x


def extract_descriptor(rows):
    soaps, targets = [], []
    for row in rows:
        atoms_Au_Fe = row.toatoms()
        atoms_all_Fe = Atoms()
        atoms_all_Fe.set_cell(atoms_Au_Fe.get_cell())
        atoms_all_Fe.set_pbc(atoms_Au_Fe.get_pbc())
        Au_idx_lst = []
        for idx, at in enumerate(atoms_Au_Fe):
            if at.symbol == 'Fe':
                atoms_all_Fe.append(Atom(at.symbol, at.position))
            elif at.symbol == 'Au':
                atoms_all_Fe.append(Atom('Fe', at.position))
                Au_idx_lst.append(idx)
            else:
                atoms_all_Fe.append(Atom(at.symbol, at.position))
        species = []
        for at in atoms_all_Fe:
            species.append(at.symbol)
        species = list(set(species))
        periodic_soap = SOAP(
            species=species,
            rcut=rcut,
            nmax=nmax,
            lmax=nmax,
            periodic=True,
            sparse=False)
        # print(Au_idx_lst, atoms_all_Fe.get_pbc(), species)
        soap_crystal = periodic_soap.create(atoms_all_Fe, positions=Au_idx_lst)
        # print(soap_crystal.shape, periodic_soap.get_number_of_features())
        soaps.append(np.mean(soap_crystal, axis=0))
        targets.append(([(row.data[predict_item])]))
        # print(soaps[-1].shape[0], targets[-1])
        # print('-' * 100)
    return soaps, targets

if __name__ == '__main__':
    rows = list(db.select())
    random.shuffle(rows)
    # training dataset
    soap_lst, tgt_lst = extract_descriptor(rows[:int(train_ratio * len(rows))])
    # vali dataset 
    vali_soap_lst, vali_tgt_lst = extract_descriptor(rows[int(train_ratio * len(rows)):int((train_ratio + vali_ratio) * len(rows))])
    # train
    model = Model(soap_lst[0].shape[0])

    criterion = torch.nn.MSELoss() # Defined loss function
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001) # Defined optimizer
    
    x_data = torch.from_numpy(np.array(soap_lst)).to('cpu')
    y_data = torch.from_numpy(np.array(tgt_lst)).to('cpu')
    x_data_vali = torch.from_numpy(np.array(vali_soap_lst)).to('cpu')
    y_data_vali = torch.from_numpy(np.array(vali_tgt_lst)).to('cpu')

    min_loss = 999
    # Training: forward, loss, backward, step
    # Training loop
    for epoch in range(1000):
        # Forward pass
        y_pred = model(x_data.double())
    
        # Compute loss
        loss = criterion(y_pred, y_data)

        # Forward pass vali
        y_pred_vali = model(x_data_vali.double())
    
        # Compute loss vali
        loss_vali = criterion(y_pred_vali, y_data_vali)

        print(epoch, loss.item(), loss_vali.item())

        if loss_vali.item() < min_loss:
            min_loss = loss_vali.item()
            torch.save(model.state_dict(), 'best_model.dict')
            print('model saved')
        # Zero gradients
        optimizer.zero_grad()
        # perform backward pass
        loss.backward()
        # update weights
        optimizer.step()
    model.load_state_dict(torch.load('best_model.dict'))
    # inference dataset
    soap_lst, tgt_lst = extract_descriptor(rows[int((train_ratio+vali_ratio) * len(rows)):])
    # inference
    x_data = torch.from_numpy(np.array(soap_lst)).to('cpu')
    y_data = torch.from_numpy(np.array(tgt_lst)).to('cpu')

    y_pred = model(x_data.double())
    print(y_data.shape, y_pred.shape)
    # check error
    err_sum = 0
    for i in range(y_data.shape[0]):
        err_sum += abs(y_data.detach().numpy()[i][0] - y_pred.detach().numpy()[i][0])
        print(y_data.shape[0], y_data.detach().numpy()[i][0], y_pred.detach().numpy()[i][0])
    print(err_sum/y_data.shape[0])

