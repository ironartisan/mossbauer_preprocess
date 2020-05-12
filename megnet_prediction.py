from ase.db import connect
from ase.visualize import view
import pymatgen.io.ase as pymatgen_io_ase
import random

seed = 1234
train_ratio = 0.5

predict_item = 'mm'
db_name = 'mossbauer.db'

db = connect(db_name)

###### megnet example hyper-parameters
from megnet.models import MEGNetModel
from megnet.data.graph import GaussianDistance
from megnet.data.crystal import CrystalGraph
import numpy as np

nfeat_bond = 10
nfeat_global = 2
r_cutoff = 5
gaussian_centers = np.linspace(0, r_cutoff + 1, nfeat_bond)
gaussian_width = 0.5
distance_converter = GaussianDistance(gaussian_centers, gaussian_width)
graph_converter = CrystalGraph(bond_converter=distance_converter, cutoff=r_cutoff)
model = MEGNetModel(nfeat_bond, nfeat_global, 
                            graph_converter=graph_converter)

#########################################

def cvt_fmt_graph(rows):
    structures = []
    props = []
    for row in rows:
        structures.append(pymatgen_io_ase.AseAtomsAdaptor.get_structure(row.toatoms()))
        
        ########### this line should be modified for different item
        props.append(row.data[predict_item])
        # props.append(abs(row.data[predict_item]))
        # props.append(row.data[predict_item]/10000)
        # props.append(row.data[predict_item]/10)
    graphs_valid = []
    targets_valid = []
    structures_invalid = []
    for s, p in zip(structures, props):
        try:
            graph = model.graph_converter.convert(s)
            graphs_valid.append(graph)
            targets_valid.append(p)
        except:
            structures_invalid.append(s)
    return graphs_valid, targets_valid

if __name__ == '__main__':
    rows = list(db.select())
    random.shuffle(rows)
    
    # training
    graphs_valid, targets_valid = cvt_fmt_graph(rows[:int(train_ratio * len(rows))])
    # train the model using valid graphs and targets
    model.train_from_graphs(graphs_valid, targets_valid, epochs=100)

    # inference
    graphs_valid, targets_valid = cvt_fmt_graph(rows[int(train_ratio * len(rows)):])

    err_sum = 0
    for i in range(len(graphs_valid)):
        pred_target = model.predict_graph(graphs_valid[i])
        print(i, '/', len(graphs_valid), 'predict: ', pred_target, 'actual:', targets_valid[i])
        err_sum += abs(pred_target-targets_valid[i])

    print(err_sum/len(graphs_valid))
