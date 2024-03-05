from utils import copy_directory, rename_images

source = "./download"
dest = "./download_copy"

copy_directory(source, dest)
rename_images(dest)