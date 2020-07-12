import os
import ase
from ase.db import connect
# TODO: use re to replace scf parser
import util as extct_mh

root_folder = './example'
# root_folder = '../'
max_iron_cnt = 10000

db_name = 'mossbauer.db'
# os.system('rm -rf ' + db_name)
if os.path.exists(db_name):
    os.remove(db_name)
db = connect(db_name)
# parse workflow:
# 1. traverse every folder under root
# 2. check 2 files, same name but diff extension (scf and struct)
# 3. read struct file
# 3.1 copy struct file, replace some Fe to Au
# 3.2 read new struct file
# 4. parse scf find 5 value. (MaHuang contribute the code)
# 5. write into db

def parse_struc_file(file_name):
    print('stuc func:', file_name)
    fe_au_atoms = []
    # iron_idx: Atom Fe[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    iron_idx = extct_mh.get_Fe_atoms(file_name)
    with open(file_name, 'r') as orig_fd:
        orig_str = orig_fd.readlines() # very small file

    for line_idx in range(len(orig_str)):
        if 'Fe' in orig_str[line_idx]:
            orig_str[line_idx] = orig_str[line_idx].replace('Fe', 'Au', 1)
            tmp_file_name = 'tmp.struct'
            with open(tmp_file_name, 'w') as tmp_fd:
                tmp_fd.writelines(orig_str)
            at = ase.io.read(tmp_file_name)
            fe_au_atoms.append(at)
            orig_str[line_idx] = orig_str[line_idx].replace('Au', 'Fe', 1)

    return iron_idx, fe_au_atoms

def parse_scf_file(file_name, iron_idx):
    print('scf func:', file_name, iron_idx)
    mm = extct_mh.get_MM(file_name, iron_idx)
    hff = extct_mh.get_HFF(file_name, iron_idx)
    eta = extct_mh.get_ETA(file_name, iron_idx)
    efg = extct_mh.get_EFG(file_name, iron_idx)
    rto = extct_mh.get_RTO(file_name, iron_idx)
    ret = []
    for i in range(len(iron_idx)):
        ret.append((mm[i], hff[i], eta[i], efg[i], rto[i]))
    return ret

def main():
    print('parse start: ')
    for root, dirs, files in os.walk(root_folder):
        print('Folder: ', root)
        if len(files) != 2:
            print('file count != 2, pass')
            print('-' * 100)
            continue
        struct_name, scf_name = '', ''
        for f in files:
            file_name = os.path.join(root, f)
            if f.endswith('.struct') and struct_name == '':
                struct_name = file_name
            elif f.endswith('.scf') and scf_name == '':
                scf_name = file_name
            else:
                print('file format error.')
                print('-' * 100)
                break
        else:
            iron_idx, at_lst = parse_struc_file(struct_name)
            props_lst = parse_scf_file(scf_name, iron_idx)

            print(at_lst, props_lst)
            if len(at_lst) != len(props_lst):
                print('struct file and scf file is not a pair? diff length...')
                print('-' * 100)
                continue
            else:
                for i in range(len(at_lst)):
                    if '' not in props_lst[i]:
                        db.write(at_lst[i], data={'mm': float(props_lst[i][0]),
                            'hff': float(props_lst[i][1]),
                            'eta': float(props_lst[i][2]),
                            'efg': float(props_lst[i][3]),
                            'rto': float(props_lst[i][4])
                            })


if __name__ == '__main__':
    main()
