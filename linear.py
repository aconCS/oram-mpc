import pandas as pd
from mpyc.runtime import mpc

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

def lookup_by_key(K, V, key):
    # assume unique keys - like BSN
    e = [key == k for k in K]            # n secure equality tests
    return mpc.in_prod(e, V), mpc.sum(e)  # 0 if key absent

def write_by_key(K, V, key, new_val):
    e = [key == k for k in K]
    old = mpc.in_prod(e, V)
    delta = new_val - old
    return [v + delta * ej for v, ej in zip(V, e)]

async def main():
    await mpc.start()

    K, V = await load_private('table.xlsx', 'bsn', 'blood_code', owner=0) #table owned by party 0

    #input the BSN here
    q = mpc.input(secint(192692124), senders=0) # query from party 0

    val, found = lookup_by_key(K, V, q)
    print('value:', await mpc.output(val), 'found:', await mpc.output(found))

    V = write_by_key(K, V, q, secint(123))
    print('table:', await mpc.output(V))
    await mpc.shutdown()

mpc.run(main())