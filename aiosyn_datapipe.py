import logging
import os
import random
import shutil
import zipfile

random.seed(3407)

logging.basicConfig(level=logging.DEBUG)

"""
TODO:
- Try it out!
- Ratio works but not completely. Leftover patches due to rounding of int().
"""


def curri_unzipper(zip_path: str, output_path: str):
    """
    Unzips a zip file of which the location entered as an argument. Meant to be used for the patches zipfile.

    Args:
        zip_path: Input path to the zip file.
        output_path: Output path for where the contents of the patches zip file are stored.
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    with zipfile.ZipFile(file=zip_path, mode="r") as f:
        f.extractall(output_path)

    # Logging
    logging.info("{zip_path} has been unzipped to {output_path}.".format(zip_path=zip_path, output_path=output_path))


def temp_folder(unzip_path: str, doname: str):
    """
    Transfers all patch png files to a temporary folder, regardless of wsi origin.

    Args:
        unzip_path: Input path for where the unzipped Aiosyn format folder is located.
        doname: Domain of which data should be transferred.
    """
    # Temporary storage folder
    temp_path = os.path.join(unzip_path, doname + "_temp")
    if os.path.exists(temp_path):
        raise OSError("New path already exists")
    else:
        os.makedirs(temp_path)

    # Copy all contents of wsi slide folders to temporary folder.
    wsi_dirs = [dir for dir in os.listdir(unzip_path) if os.path.isdir(os.path.join(unzip_path, dir))]
    for dir in wsi_dirs:
        dir_path = os.path.join(unzip_path, dir)
        shutil.copytree(dir_path, temp_path, copy_function=shutil.move, dirs_exist_ok=True)

    # os.rmdir(unzip_path)
    # logging.debug("Removed unzipped and empty patches folder")

    # Logging
    logging.info("Temporary folder with pngs has been created at {temp}".format(temp=temp_path))


def format_creation(format_path: str, domains: list, subsets: list, img_types: list):
    """
    Creates data folders and subfolders in the Curriculum learning format.

    Args:
        format_path: Path to where the Curriculum learning formatted folders should be created.
        domains: List of domains.
        subsets: Data subsets. train, test partitions for instance.
        img_types: Image types. Standard types are image, mask and visualizations.
    """

    # Can be used for domain separation (e.g. source and target)
    for d in domains:
        d_path = os.path.join(format_path, d)
        if not os.path.exists(d_path):
            os.makedirs(d_path)

        # Set partition separation (e.g. train and test)
        for ss in subsets:
            ss_path = os.path.join(d_path, ss)
            if not os.path.exists(ss_path):
                os.makedirs(ss_path)

            # Image type separation (e.g. image and mask)
            for it in img_types:
                it_path = os.path.join(ss_path, it)
                if not os.path.exists(it_path):
                    os.makedirs(it_path)

    # Logging
    logging.info("Curriculum learning format folders created at {form}".format(form=format_path))


def fill_folders(output_path: str, doname: str, splits: dict, img_types: list):
    """
    Create and fill subgroup folders for the transfer of data from the Aiosyn format to Curriculum learning format.

    Args:
        temp_path: Path of temporary folder created with temp_folder().
        output_path: Output path for where Curriculum learning formatted data should be stored.
        doname: Domain name.
        splits: Data subsets ratios. dict of floats splits (e.g. {"train": 0.7, "val": 0.15, "test": 0.15}).
        img_types: Image types (e.g. ["img", "msk", "vis"]). Standard types are image, mask and visualizations.
    """
    # Make ratios sum up to 1.
    rat_sum = sum(list(splits.values()))
    for value in splits:
        splits[value] /= rat_sum

    # Split imgs into randomized subsets with a ratio.
    temp_path = os.path.join(output_path, doname + "_temp")
    imgs = [f for f in os.listdir(temp_path) if f.endswith("img.png")]

    random.shuffle(imgs)
    n_img = len(imgs)

    for k, v in splits.items():
        k_split = int(v * n_img)
        logging.debug("{key} split consists of {split} images.".format(key=k, split=k_split))

        for img in imgs[:k_split]:
            logging.debug("{i} is currently being processed.".format(i=img))

            for typ in img_types:
                img_old_path = os.path.join(temp_path, img.split(".")[0][:-3] + typ + "." + img.split(".")[1])
                img_new_path = os.path.join(
                    output_path, doname, k, typ, img.split(".")[0][:-4] + "." + img.split(".")[1]
                )
                shutil.move(img_old_path, img_new_path)

        del imgs[: int(v * n_img)]
        logging.debug("Deleted first split from img list.")

    # # Remove temporary folder
    # os.rmdir(temp_path)
    # logging.debug("Removed temporary folder")

    # Logging
    logging.info("Folders are filled according to the following splits: {splits}".format(splits=splits))


def aiocurtransfer(zip_path: str, output_path: str, domain_name: str, splits: dict, img_types: list):
    """
    Simple run function for Aiosyn patch datasets to transform to the curriculum learning dataset format.

    Args:
        zip_path: Input path to the zip file.
        output_path: Output path for where Curriculum learning formatted data should be stored.
        domain_name: Domain name.
        splits: Data subsets ratios. dict of floats splits (e.g. {"train": 0.7, "val": 0.15, "test": 0.15}).
        img_types: Image types (e.g. ["img", "msk", "vis"]). Standard types are image, mask and visualizations.
    """
    curri_unzipper(zip_path=zip_path, output_path=output_path)
    temp_folder(unzip_path=output_path, doname=domain_name)
    format_creation(format_path=output_path, domains=[domain_name], subsets=list(splits.keys()), img_types=img_types)
    fill_folders(output_path=output_path, doname=domain_name, splits=splits, img_types=img_types)
