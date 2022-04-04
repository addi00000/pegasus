import os

def inject():
    path = r"C:\Users\{}\AppData\Local\Discord".format(os.getlogin())
    
    for path, sub_dirs, files in os.walk(path):
        if not files:
            print("no files at this level")
        
    print(path)
    
inject()