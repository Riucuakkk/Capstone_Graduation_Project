import kagglehub
import shutil
import os

download_path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")

target_path = "data/raw"

os.makedirs(target_path, exist_ok=True)

for file_name in os.listdir(download_path):
    full_file_name = os.path.join(download_path, file_name)
    if os.path.isfile(full_file_name):
        shutil.copy(full_file_name, target_path)

print("Dataset copied to:", target_path)