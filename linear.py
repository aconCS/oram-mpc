import pandas as pd
from mpyc.runtime import mpc

BLOOD = ['O+', 'A+', 'B+', 'AB+', 'O-', 'A-', 'B-', 'AB-']

secint = mpc.SecInt(32)

def read_columns(path, key_col, val_col):
    df = pd.read_excel(path)
    return df[key_col].astype(int).tolist(), df[val_col].astype(int).tolist()

async def load_private(path, key_col, val_col, owner=0):
    # table owned by one party, everyone gets secret shared columns
    if mpc.pid == owner:
        keys, vals = read_columns(path, key_col, val_col)
        n = len(keys)
    else:
        keys = vals = None
        n = None
    n = await mpc.transfer(n, senders=owner)          
    if mpc.pid != owner:
        keys = vals = [0] * n                   # placeholders, ignored
    K = mpc.input([secint(k) for k in keys], senders=owner)
    V = mpc.input([secint(v) for v in vals], senders=owner)
    return K, V

def lookup_by_index(V, i):
    return mpc.in_prod(mpc.unit_vector(i, len(V)), V)

def write_by_index(V,i,new_val):
    e = mpc.unit_vector(i, len(V))
    old = mpc.in_prod(e, V)
    delta = new_val - old
    return [v + delta * ej for v, ej in zip(V, e)]

def lookup_by_key(K, V, key):
    # assume unique keys - like BSN
    e = [key == k for k in K]         # n secure equality tests
    corrector = mpc.sum(e) - 1        #will correct outpu to -1 if bns not found
    return mpc.in_prod(e, V) + corrector, mpc.sum(e)  

def write_by_key(K, V, key, new_val):
    e = [key == k for k in K]
    old = mpc.in_prod(e, V)
    delta = new_val - old
    return [v + delta * ej for v, ej in zip(V, e)], mpc.sum(e)

def resolve_blood(blood_num):
    if blood_num == -1:
        return 'not found' 
    return BLOOD[blood_num]

async def main():
    await mpc.start()

    q_party = 0 #the one that makes queries - changed during testing

    K, V = await load_private('table.xlsx', 'bsn', 'blood_code', owner=0) #table owned by party 0

    print("1# Testing look up by key (BSN)...")
    bsn_look = int(input('BSN of requested patient: ')) if mpc.pid == q_party else None
    q = mpc.input(secint(bsn_look), senders=q_party)
    val, found = lookup_by_key(K, V, q)
    print('value:', resolve_blood(await mpc.output(val)), 'found:', await mpc.output(found))

    print("2# Testing look up by index...")
    user_i_look = int(input('Row index of requested patient: ')) if mpc.pid == q_party else None
    #q_party can check if real i out of range & propagates it to other parties so they keep up
    valid_i = await mpc.transfer((0 <= user_i_look < len(V)) if mpc.pid == q_party else None, senders=q_party)
    if valid_i:
        i_look = mpc.input(secint(user_i_look), senders=q_party)
        val2 = lookup_by_index(V, i_look) 
        print('value:', resolve_blood(await mpc.output(val2)))
    else:
        print("Index out of range")

    print("3# Testing write by key (BSN)...")
    bsn_write = int(input('BSN of requested patient: ')) if mpc.pid == q_party else None
    q2 = mpc.input(secint(bsn_write), senders=q_party)
    user_new_blood = int(input('New blood type number (0-7): ')) if mpc.pid == q_party else None
    valid_blood = await mpc.transfer((0 <= user_new_blood < len(BLOOD)) if mpc.pid == q_party else None, senders=q_party)
    if valid_blood:
        new_v_key = mpc.input(secint(user_new_blood), senders=q_party) 
        V, found = write_by_key(K, V, q2, new_v_key) 
        if await mpc.output(found):
            print('table:', [resolve_blood(blood_num) for blood_num in await mpc.output(V)])
        else:
            print("BSN not found")
    else:
        print("Incorrect blood index.")

    print("4# Testing write by index...")
    user_i_write = int(input('Row index of requested patient: ')) if mpc.pid == q_party else None
    valid_i = await mpc.transfer((0 <= user_i_write < len(V)) if mpc.pid == q_party else None, senders=q_party)
    if valid_i:
        i_write = mpc.input(secint(user_i_write), senders=q_party)
        user_new_blood2 = int(input('New blood type number (0-7): ')) if mpc.pid == q_party else None
        valid_blood = await mpc.transfer((0 <= user_new_blood2 < len(BLOOD)) if mpc.pid == q_party else None, senders=q_party)
        if valid_blood:
            new_v_i = mpc.input(secint(user_new_blood2), senders=q_party)
            V = write_by_index(V, i_write, new_v_i) 
            print('table:', [resolve_blood(blood_num) for blood_num in await mpc.output(V)])
        else:
            print("Incorrect blood index.")
    else:
        print("Index out of range.")
    await mpc.shutdown()

mpc.run(main())