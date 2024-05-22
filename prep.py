import os
import shutil

def create_folders():
    # Create folders if they don't exist
    try:
        os.makedirs('forged', exist_ok=True)
        os.makedirs('authentic', exist_ok=True)
    except OSError as e:
        print("Error:", e)

def move_images(folder):
    try:
        # Change directory to the specified folder
        os.chdir(folder)
        
        # Get a list of all files in the specified directory
        files = os.listdir()

        # Loop through each file
        for file in files:
            # Check if the file is an image
            if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png'):
                # Check if the letter 'F' is in the filename
                if 'F' in file:
                    # Move the file to the forged folder
                    shutil.move(file, os.path.join('forged', file))
                else:
                    # Move the file to the authentic folder
                    shutil.move(file, os.path.join('authentic', file))
    except Exception as e:
        print("Error:", e)

def main():
    # Provide the folder location containing the images
    folder = '/content/images'
    create_folders()
    move_images(folder)

if __name__ == "__main__":
    main()
