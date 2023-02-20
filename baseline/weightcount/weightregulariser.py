# @author Kuldeep S Meel
# Copyright (c) 2016 Kuldeep S Meel
# Please see attached License file for licensing information
# If you use this code for experiments, please cite the following paper:
# "From Weighted to UnWeighted Model Counting", Supratik Chakraborty,
# Dror Fried, Kuldeep S. Meel, Moshe Y. Vardi
# Proc. of IJCAI 2016

import os
import argparse
import random
#  The code is straightforward chain formula implementation
#


def Transform(inputFile, outputFile, precision):
    f = open(inputFile, "r")
    lines = f.readlines()
    f.close()
    writeLines = ""
    totalVars = 0
    weightVars = []
    totalClaus = 0
    precision = int(2 ** precision)  # precision is in bits
    for line in lines:
        if line.strip()[:2] == "p ":
            fields = line.strip().split()
            totalVars = int(fields[2])
            totalClaus = int(fields[3])
            continue
        if line.strip()[:5] == "c ind":
            indVarLine = [int(i) for i in line.strip()[5:-2].split()]
            (indVarLine)
            weightVars += [int(i) for i in indVarLine]
        if (
            line.strip()[0].isdigit()
            or line.strip()[0] == "c"
            or line.strip()[0] == "-"
        ):
            writeLines += str(line)
    for var in weightVars:
        cnfWeight = random.randint(1, precision-1)*1.0/precision
        writeLines += "w " + str(var) + " " + str(cnfWeight) + " \n"
    f = open(outputFile, "w")
    f.write("p cnf " + str(totalVars) + " " + str(totalClaus) + " \n")
    f.write(writeLines)
    f.close()


def ensureDirectory(path):
    d = os.path.dirname(path)
    if not os.path.exists(d):
        os.makedirs(d)
    return


####################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-precision", help="Precision (value of m)", type=int, default=4
    )
    parser.add_argument("inputFile", help="input File(in Weighted CNF format)")
    args = parser.parse_args()
    precision = args.precision
    inputFile = args.inputFile
    tmpDir = os.getenv("TMPDIR", "temp")

    # initialization
    ensureDirectory(tmpDir + "/")

    initialFileSuffix = inputFile.split("/")[-1][:-4]
    outCNFFile = tmpDir + "/" + str(initialFileSuffix) + ".cnf"

    Transform(inputFile, outCNFFile, precision)
