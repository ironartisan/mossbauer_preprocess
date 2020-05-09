import os

# TODO: using re to replace scf parser
import extracted_data as extct_mh

root_folder = './example'
max_iron_cnt = 10000
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
    iron_idx = extct_mh.get_Fe_atoms(file_name)
    return iron_idx, iron_idx # fe_au_atoms

def parse_scf_file(file_name, iron_idx):
    print('scf func:', file_name)
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
                pass
            print('-' * 100)
            # for d in dirs:
            #     print(os.path.join(root, d))


if __name__ == '__main__':
    main()
