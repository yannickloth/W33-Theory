import numpy as np
avg=np.array([307.07311444,324.19556571,417.55881076])
y=np.array([0.93875895,0.01828308,0.04295797])
for i in range(3):
    for j in range(i+1,3):
        r=y[i]/y[j]
        k=(avg[j]-r*avg[i])/(1-r)
        print(f'k from {i},{j} =',k)
