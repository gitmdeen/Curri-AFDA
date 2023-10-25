from pathlib import Path

data_path_root = Path('/mnt/c/Users/Michael/Documents/Aiosyn/datasets/Curriset/curri_data')

def get_data_paths_list(domain='Domain1', split='train', type='img'):
    paths_list = list((data_path_root / domain / split / type).glob('*'))
    return paths_list
