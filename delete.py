import os
import glob

folder_path = ""

files = glob.glob(os.path.join(folder_path, "data*.csv"))

for f in files:
    try:
        os.remove(f)
        print(f"Deleted: {f}")
    except Exception as e:
        print(f"Error when trying to delete {f}: {e}")


