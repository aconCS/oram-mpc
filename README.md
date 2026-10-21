## Linear ORAM basic implementation

Just as in project description: "The trivial ORAM construction is “Linear ORAM”: To read position ‘i‘, you
construct a secret unit vector with a one at position ‘i’ and take the inner
product with the array A. To write value ‘v‘, add ‘(v - A[i])’ times that unit
vector. It needs no client state, but every access costs O(n) work, so it only
makes sense for small arrays."

Those unit vectors as well as secure data typec come from mpyc. To install:
```bash
pip install mpyc
```

and to run evetyrhing I would recommend
```bash
pip install -r requrements.txt
```

The initial table consists only of 100 entries of

- BSN: 9 digit Dutch citizen service number 
- blood_type:  as one of 8 types
- blood_code: integer encoding the blood type (secint can't hold strings)

# TODO: 
- check bigger datasets, 
- way to securely input query with bsn, 
- unit tests ?, 
- simulation of real network (termianls with different-I ids) 