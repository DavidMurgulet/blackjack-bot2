import os
import shutil

# Define the path to the 'runs/detect' folder
project_dir = os.path.dirname(os.path.abspath(__file__))  # Get the current directory of the script
detect_folder = os.path.join(project_dir, '..', 'runs', 'detect')  # Path to 'runs/detect' folder

# Check if the 'runs/detect' folder exists
if os.path.exists(detect_folder) and os.path.isdir(detect_folder):
    try:
        # Delete the 'detect' folder and all its contents
        shutil.rmtree(detect_folder)
        print(f"Successfully deleted: {detect_folder}")
    except Exception as e:
        print(f"Error deleting folder {detect_folder}: {e}")
else:
    print(f"The folder {detect_folder} does not exist.")