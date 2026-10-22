import numpy as np
import pandas as pd
import random
 
N = 2**24
TYPES = np.array(["O+", "A+", "B+", "AB+", "O-", "A-", "B-", "AB-"])

random.seed(42)

bsn = sorted(random.sample(range(100_000_000, 1_000_000_000), N)) #picks from 100 000 00 to 999 999 999 no repeats
blood_code = random.choices(range(8), k = N) #picks from 0 to 7 with repeats (roughly equal distribution)

pd.DataFrame({
    "bsn": bsn,
    "blood_type": TYPES[blood_code],
    "blood_code": blood_code,
}).to_csv("full_table.csv", index=False)