import os
import sys
import subprocess
from pathlib import Path

def create_executable():
    # Verify .spec file exists
    spec_file = "main.spec"
    if not os.path.exists(spec_file):
        print(f"File {spec_file} not found!")
        return False

    # Command to create the executable
    cmd = [
        sys.executable,
        "-m", 
        "PyInstaller",
        "--noconfirm",
        spec_file
    ]
    
    try:
        print("Creating executable...")
        print(f"Command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Executable created successfully!")
            print(f"Executable available in: dist/")
            return True
        else:
            print("Error creating executable:")
            print(result.stderr)
            return False
        
    except Exception as e:
        print(f"Error running PyInstaller: {e}")
        return False

def clean_build():
    """Removes temporary files from previous builds"""
    folders_to_remove = ["build", "dist", "__pycache__"]
    files_to_remove = [f for f in os.listdir(".") if f.endswith(".spec") and f != "main.spec"]
    
    for folder in folders_to_remove:
        if os.path.exists(folder):
            try:
                import shutil
                shutil.rmtree(folder)
                print(f"Folder {folder} removed")
            except Exception as e:
                print(f"Could not remove {folder}: {e}")

    # Remove extra .spec files
    for file in files_to_remove:
        try:
            os.remove(file)
            print(f"File {file} removed")
        except Exception as e:
            print(f"Could not remove {file}: {e}")

def main():
    print("Executable Build Script")
    print("=" * 40)
    
    # Ask if user wants to clean before building
    clean = input("Clean previous builds? (y/n): ").lower().strip()
    if clean in ['s', 'sim', 'y', 'yes']:
        clean_build()
    
    # Create the executable
    success = create_executable()
    
    if success:
        print("\nProcess completed!")
        print("The executable is in the 'dist/' folder")
    else:
        print("\nAn error occurred during the process.")
        sys.exit(1)

if __name__ == "__main__":
    main()