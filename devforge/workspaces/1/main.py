import os

file_path = r"C:\Users\sardo\Desktop\Operatorlarni-Qayta-Yuklash (1).pptx"

try:
    if os.path.exists(file_path):
        os.remove(file_path)
        print("File removed successfully.")
except PermissionError:
    print("Access Denied: You must take ownership of the file first.")
except Exception as e:
    print(f"Error: {e}")
