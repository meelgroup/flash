import argparse
import random

from wflash import parseIndSupport


def genbench():
    """
    Add weigts to existing cnfFile
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, dest="seed", default=420)
    parser.add_argument("--output", type=str, dest="output", default="None")
    parser.add_argument("--nind", type=int, dest="numInd", default=-1)
    parser.add_argument("input", help="input file")
    args = parser.parse_args()

    inputFile = open(args.input, "r")
    lines = inputFile.readlines()
    inputFile.close()
    nVars = lines[0].strip().split()[2]

    if args.output == "None":
        outputFileName = args.input.split("/")
        outputFileName = outputFileName[-1][:-4] + '_w.cnf'
    else:
        outputFileName = args.output

    indvars = parseIndSupport(args.input)
    indMap = {}
    for var in indvars:
        indMap[var] = 0.5

    if args.numInd > 0:
        selInd = random.sample(indvars, args.numInd)
    else:
        selInd = random.sample(indvars, int(len(indvars) / 3)) #args.numInd
    for var in selInd:
        indMap[var] = random.sample([0.4375, 0.5625], 1)[0]

    outputFile = open(outputFileName, "w")
    outputFile.write(lines[0])

    indvarstr ="c ind "
    count = 0
    for indvar in indvars:
        indvarstr += str(indvar) + ' '
        count += 1
        if indvar % 10 == 0: #count % 10
            indvarstr += "0\nc ind "
    indvarstr += "0\n"
    outputFile.write(indvarstr)

    for line in lines[1:]:
        if line.startswith('c ind'):
            continue
        else:
            toWrite = ''
            vars = line.replace('c ind', '').strip().split()[:-1]
            for var in vars:
                sign = int(int(var)/abs(int(var)))
                toWrite += str(sign * abs(int(var))) + ' '
            toWrite += '0\n'
        outputFile.write(toWrite)


    # Add weights to the independent literal set
    # wgt = [0.4375, 0.5, 0.5625] # set to some k/2^m value (k = 3,4,5 & m = 3, 4)

    for var in indvars:
        # w = random.sample(wgt, 1)[0]
        outputFile.write('w ' + str(var) + ' ' + str(indMap[var]) + "\n") #str(w)
    outputFile.close()

if __name__ == '__main__':
    genbench()
