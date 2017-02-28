#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from _version import get_versions as _get_versions
__version__      = _get_versions()['version'][:5]
__long_version__ = _get_versions()['version']
del _get_versions

def main():

    print('''
               _             _ 
              (_)           (_)                      .-=-.          .--.
     _ __ ___  _ _ __   __ _ _           __        .'     '.       /  " )
    | '_ ` _ \| | '_ \ / _` | |  _     .'  '.     /   .-.   \     /  .-'\\
    | | | | | | | | | | (_| | | ( \   / .-.  \   /   /   \   \   /  /    ^
    |_| |_| |_|_|_| |_|\__,_| |  \ `-` /   \  `-'   /     \   `-`  /
                           _/ |   `-.-`     '.____.'       `.____.'
                          |__/ 
    version {}
    
    This script helps you to build, convert and upload a conda package.
    This script should be run  in the same folder as the meta.yaml file.
    
    You have the follwing options:
    
    - build or process already built packages
    - set python build version
    - convert or not to other platforms
    - upload to your conda channel    
    
    '''.format(__version__))
         
    import subprocess
    import sys
    
    if sys.version_info[:2] <= (2, 7):
        input = raw_input
         
    try:
        from termcolor import colored
    except ImportError:
        def colored(text, color): return text

    try: 
        import pathlib
    except ImportError:
        import pathlib2 as pathlib
    
    if not pathlib.Path("meta.yaml").exists():
        sys.exit(colored("No meta.yaml file found in this directory.\n", "red"))
    
    bashCommand = "conda build . --output"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, universal_newlines=True)
    
    pkgpth   = pathlib.Path(process.communicate()[0].strip())
    pkgname  = pkgpth.name
    builddir = pkgpth.parent.parent
    
    print(bashCommand)
    print("Build dir: ",colored( builddir, "blue"))
    print("Package  : ",colored( pkgpth, "blue"))

    
    response = input("build (y/n) ? ")
    
    if response.lower().startswith("y"):
        response = input("python version (3.5) ? ")
        if not response: response="3.5"        
        bashCommand = "conda build . --no-anaconda-upload --python={ver}".format(ver=ver) 
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, universal_newlines=True)
        output = process.communicate()[0]
        print(colored(output, "blue"))
        if not pkgpth.exists():
            sys.exit(colored("package was not built.\n"),"red")
    else:
        print(colored("build skipped.", "red"))
        if not pkgpth.exists():
            sys.exit(colored("package does not exist.\n", "red"))

    
    if "/noarch/" in str(pkgpth): # no convert
        print(colored("no convert, since package is NOARCH", "red"))
        pkgdirs = ["noarch"]
    else: # ask to convert
        response = input("convert (y/n) ? ")
        if response.lower().startswith("y"):
            bashCommand = "conda convert {} -p all -o {}".format(str(pkgpth), str(builddir))
            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, universal_newlines=True)
            output = process.communicate()[0]
            print(colored(output, "blue"))
            pkgdirs = ["win-64", "osx-64", "win-32", "linux-64", "linux-32"]
        else:
            print(colored("convert skipped.", "red"))
            pkgdirs = ["linux-64"]
    
    
    pts=[]
    
    print()
    print("The following packages have been created:")
    print()
    
    for dir_ in pkgdirs:
        upload_pth = builddir.joinpath(dir_, pkgname)
        print(colored(upload_pth, "blue"))
        pts.append(upload_pth)
        
    response = input("upload (y/n) ? ")
    
    if response.lower().startswith("y"):
        response = input("label (hit return for default 'main')?")
        label = response or "main"
        for p in pts:
            bashCommand = "anaconda upload --label {} {}".format(label, p)
            process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, universal_newlines=True)
            output = process.communicate()[0]
            print(colored(output, "blue"))
    else:
        print(colored("upload skipped.", "red"))
        
    process = subprocess.Popen("conda build purge".split(), stdout=subprocess.PIPE, universal_newlines=True) 
    output = process.communicate()[0]
    print(output)
    print('''                  
                               ____
      ________________________/ O  \___/
     <_/_\_/_\_/_\_/_\_/_\_/_______/   \   zzzzz done!''')
    
    
if __name__=="__main__":
    main()