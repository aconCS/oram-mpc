# Linear ORAM basic implementation

Just as in project description: "The trivial ORAM construction is “Linear ORAM”: To read position ‘i‘, you
construct a secret unit vector with a one at position ‘i’ and take the inner
product with the array A. To write value ‘v‘, add ‘(v - A[i])’ times that unit
vector. It needs no client state, but every access costs O(n) work, so it only
makes sense for small arrays."

## Installating the libraries

Those unit vectors as well as secure data typec come from mpyc. To install:
```bash
pip install mpyc
```

and to run evetyrhing I would recommend
```bash
pip install -r requirements.txt
```

The initial table consists only of 100 entries of

- BSN: 9 digit Dutch citizen service number 
- blood_type:  as one of 8 types
- blood_code: integer encoding the blood type (secint can't hold strings)

## Running the simulation
To run linear.py, open three separate terminals from the project root & paste these three separate commands:

Terminal 1
```bash
python linear.py -M3 -I0
```

Terminal 2
```bash
python linear.py -M3 -I1
```

Terminal 3
``` bash
python linear.py -M3 -I2
```

## TODOs 
- check bigger datasets (and write down size + time), 
- unit tests ?, 
- simulation of real network (termianls with different-I ids) check here [https://mpyc.readthedocs.io/en/latest/cli.html]