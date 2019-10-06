import os
from time import time

wd = os.path.dirname(os.path.realpath(__file__))
os.system(f'cd {wd}')

start = time()

# print(f'\n\n ---- Run PROCESSING ---- \n\n')
# os.system('processing.py')
# print(f'\n\n ---- Run ANALYSIS ---- \n\n')
# os.system('analysis.py')
print(f'\n\n ---- Run GET_EFFECT_PERIOD ---- \n\n')
os.system('get_effect_period.py')
print(f'\n\n ---- Run RESOLVE ---- \n\n')
os.system('resolve.py')

end = time()

elapsed = end-start

print(f'Elapsed time: {round(elapsed/60, 2)} minutes')

