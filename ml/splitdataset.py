import os
import shutil
import random

# Your downloaded PlantVillage 15-class training dataset
SOURCE_DIR = r"C:\Users\arit1\Downloads\PlantVillage\train"

# Project dataset folders
TRAIN_DIR = r"data\dataset\train"
TEST_DIR = r"data\dataset\test"

SPLIT_RATIO = 0.8

# Create output directories
os.makedirs(TRAIN_DIR, exist_ok=True)
os.makedirs(TEST_DIR, exist_ok=True)

# Process each disease class
for class_name in os.listdir(SOURCE_DIR):

    class_path = os.path.join(SOURCE_DIR, class_name)

    if not os.path.isdir(class_path):
        continue

    # Get image files
    images = os.listdir(class_path)

    # Randomize
    random.shuffle(images)

    # 80/20 split
    split_index = int(len(images) * SPLIT_RATIO)

    train_images = images[:split_index]
    test_images = images[split_index:]

    # Create class folders
    train_class_dir = os.path.join(TRAIN_DIR, class_name)
    test_class_dir = os.path.join(TEST_DIR, class_name)

    os.makedirs(train_class_dir, exist_ok=True)
    os.makedirs(test_class_dir, exist_ok=True)

    # Copy training images
    for img in train_images:
        shutil.copy(
            os.path.join(class_path, img),
            os.path.join(train_class_dir, img)
        )

    # Copy testing images
    for img in test_images:
        shutil.copy(
            os.path.join(class_path, img),
            os.path.join(test_class_dir, img)
        )

    print(
        f"✔ {class_name}: "
        f"{len(train_images)} train, "
        f"{len(test_images)} test"
    )

print("\nDataset split completed successfully!")