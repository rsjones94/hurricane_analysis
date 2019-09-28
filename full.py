import os


wd = os.path.dirname(os.path.realpath(__file__))
os.system(f'cd {wd}')
os.system('processing.py')
os.system('analysis.py')
os.system('resolve.py')
