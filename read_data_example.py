from ase.db import connect
from ase.visualize import view

db_name = 'mossbauer.db'

db = connect(db_name)

for row in db.select():
    print('row.id: ', row.id)
    print('REGRESSION INPUT: ')
    print('cell of crystall: ', row.toatoms().get_cell())
    print('enviroment atoms: ')
    for at in row.toatoms():
        if at.symbol != 'Au':
            print(at.position, at.symbol)
    print('Contributed Fe atoms: ')
    for at in row.toatoms():
        if at.symbol == 'Au':
            print(at.position, 'Fe')
    print('REGRESSION OUTPUT: ')
    print('data need to regress: ', row.data)
    print('-' * 100)

    if row.id == 1:
        view(row.toatoms())
