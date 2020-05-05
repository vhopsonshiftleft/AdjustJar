#!/usr/bin/python
##########
#
#       Remove Frameworks
#
# This script is designed to remove frameworks specified by the configuration file.
# Once the frameworks are eliminated, the resulting JAR file is ready for analysis.
#
# Copyright (C) 2020 Shift Left, Inc.  All Rights Reserved
#
##########

import argparse
from yaml import load
from yaml import CLoader
from zipfile import ZipFile
import re

##### collectJarList
#
# Collect the list of jars that should be eliminated from the given jarfile in our
# configuration file.  The list is maintained in a dictionary for easy search.
#
def collectJarList(cfg) :
    retval = cfg["rm_objects"]
    return retval

#####
#
# Create the new jar by copying over all of the files that do not match any of
# the filenames in our exclusion list
def createNewJar(e_jars, zin, zout) :
    
    # pull the contents of each item into memory, then check to see if the
    # filename portion matches any of our exclusionary list.  If it does not,
    # simply write memory into the output file
    for item in zin.infolist() :
        
        # iterate the incoming regular expressions against the filename.  Any match signals that
        # we should eliminate it.
        flag = True
        for res in e_jars :
            if re.search(res, item.filename) :
                flag = False
                break

        # ok, if the flag is True, we write the contents of the input file to the output jar
        if flag :
            buffer = zin.read(item.filename)
            zout.writestr(item, buffer)
        else :
            print("|-- Excluding \"%s\"" % item.filename)


##### Main Entry Point
#
def main(args) :
    
    # collect our configuration parameters into a dictionary
    with open(args.config, "r") as config_file :
        cfg = load(config_file, Loader=CLoader)

    # if the command line flags override config file settings, adjust them here
    if None != args.input_jar :
        cfg["in_jar"] = args.input_jar
    if None != args.output_jar :
        cfg["out_jar"] = args.output_jar

    # using our configuration parameters, get the list of jars to eliminate
    e_jars = collectJarList(cfg)

    # create a temporary jar file for moving the jar data into to prevent modification
    # of the original jar.
    zin = ZipFile(cfg["in_jar"], "r")
    zout = ZipFile(cfg["out_jar"], "w")

    # process the files between the jars.  
    createNewJar(e_jars, zin, zout)

    # close the jarfiles
    zin.close()
    zout.close()


##### Environment Entry Point
#
desc = '''
Remove designated frameworks from JAR and submit for analysis.
'''
parser = argparse.ArgumentParser(description=desc)
parser.add_argument("--config", "-c", required=True, help="Configuration file for parameters.")
parser.add_argument("--input_jar", "-i", required=False, default=None, help="Input JAR file for component removal (this overrides the config file)")
parser.add_argument("--output_jar", "-o", required=False, default=None, help="Output JAR file for allowed component storage (this overrides the config file)")
args = parser.parse_args()

if "__main__" == __name__ :
    main(args)
    print("|- Done.")

