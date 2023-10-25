# from aiosyn_datapipe import aiocurtransfer
# aiocurtransfer()

import torch
from torchvision import transforms
from PIL import Image

img = Image.open("/mnt/c/Users/Michael/Documents/Aiosyn/datasets/Curriset/curri_data/Domain1/test/msk/115_117504_38400.png")
convert_tensor = transforms.ToTensor()
print(convert_tensor(img))