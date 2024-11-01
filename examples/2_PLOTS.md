--- 
title: Plots
---

## Plots 


```bash
for N in $(seq -s" " 10);
do
   pytest -k test_python_too_fast -q
done
```

:::plot
```csv
run,usecs
1,202.7160
2,199.1040
3,254.6150
4,246.1540
5,221.9280
6,425.5660
7,212.9930
8,219.2340
9,250.9560
10,216.3560
```
:::


<!---
| Name      | Value       |
|--------------------------|-----------|
| test_python_too_fast     | 202.7160  |
| test_python_too_fast     | 199.1040  |
| test_python_too_fast     | 254.6150  |
| test_python_too_fast     | 246.1540  |
| test_python_too_fast     | 221.9280  |
| test_python_too_fast     | 425.5660  |
| test_python_too_fast     | 212.9930  |
| test_python_too_fast     | 219.2340  |
| test_python_too_fast     | 250.9560  |
| test_python_too_fast     | 216.3560  |
-->