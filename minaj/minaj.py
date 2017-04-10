#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ._version import get_versions
__version__      = get_versions()['version'][:5]
__long_version__ = get_versions()['version']
del get_versions

def main():
    import sys
    pyver = sys.version[:6]
    
    import os
    
    def cmd_exists(cmd):
        return any(
                os.access(os.path.join(path, cmd), os.X_OK) 
                for path in os.environ["PATH"].split(os.pathsep))

    print('''
               _             _ 
              (_)           (_)                      .-=-.          .--.
     _ __ ___  _ _ __   __ _ _           __        .'     '.       /  " )
    | '_ ` _ \| | '_ \ / _` | |  _     .'  '.     /   .-.   \     /  .-'\\
    | | | | | | | | | | (_| | | ( \   / .-.  \   /   /   \   \   /  /    ^
    |_| |_| |_|_|_| |_|\__,_| |  \ `-` /   \  `-'   /     \   `-`  /
                           _/ |   `-.-`     '.____.'       `.____.'
                          |__/ 
    minaj version  {}
    minaj is running on Python {}
    
    conda           is available: {}
    anaconda-client is available: {}
    
    This script helps you to build, convert and upload a conda package.
    This script should be run in the same folder as the meta.yaml file.
    
    You will have the following options:
    
    - build or process already built packages
    - set python version to use for build
    - convert or not to other platforms
    - upload to your conda channel
    
    for uploading packages, you need to have anaconda-client installed.
    it can be installed like this:
    
    conda install anaconda-client
    
    '''.format(__version__, 
               pyver, 
               cmd_exists("conda"), 
               cmd_exists("anaconda")))
         
    import subprocess
    
    if sys.version_info[0] < 3:
        get_input = raw_input
    else:
        get_input = input

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
    
    ver = get_input("Which python version do you want to build with (hit return for default {}) ? ".format(pyver))
    if not ver: 
        ver=pyver  
    
    bashCommand = "conda build . --output --python={ver}".format(ver=ver) 
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, universal_newlines=True)
    
    pkgpth   = pathlib.Path(process.communicate()[0].strip())
    pkgname  = pkgpth.name
    builddir = pkgpth.parent.parent
    
    print(bashCommand)
    
    #print(colored("Build dir: ","magenta") + colored( builddir, "blue"))
    print(colored("Package  : ","magenta") + colored( pkgpth  , "blue"))

    response = get_input("build this package (y/n) ? ")
    
    if response.lower().startswith("y"):       
        bashCommand = "conda build . --no-anaconda-upload --python={ver}".format(ver=ver) 
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, universal_newlines=True)
        output = process.communicate()[0]
        print(colored(output, "blue"))
        if not pkgpth.exists():
            sys.exit(colored("package was not built.\n","red"))
    else:
        print(colored("build skipped.", "red"))
        if not pkgpth.exists():
            sys.exit(colored("package does not exist.\n", "red"))

    if "/noarch/" in str(pkgpth): # no convert
        print(colored("no convert, since package is NOARCH", "red"))
        pkgdirs = ["noarch"]
    else: # ask to convert
        for platform in ["win-64", "osx-64", "win-32", "linux-32", "linux-64"]:
            response = get_input("convert to {} (y/n) ?".format(platform))
            if response.lower().startswith("y"):           
                bashCommand = "conda convert {} -p {} -o {}".format(str(pkgpth), platform, str(builddir))
                print(colored(bashCommand, "cyan"))
                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE, universal_newlines=True)
                output = process.communicate()[0]
                print(colored(output, "blue"))
            else:
                print(colored("convert skipped.", "red"))
                
    pts=[]
    
    print()
    print("The following packages have been created:")
    print()
    
    for dir_ in ["win-64", "osx-64", "win-32", "linux-32", "linux-64"]:
        upload_pth = builddir.joinpath(dir_, pkgname)
        if upload_pth.exists():
            print(colored(upload_pth, "blue"))
            pts.append(upload_pth)
        
    response = get_input("upload these package(s) (y/n) ? ")
    
    if response.lower().startswith("y"):
        response = get_input("label (hit return for default 'main')?")
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