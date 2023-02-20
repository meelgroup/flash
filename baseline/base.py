import math
import os
import argparse
import time
import tempfile
import sys
import random
import copy


'''
Define Global identifiers for different samplers
'''

SAMPLER_UNIGEN3 = 1
SAMPLER_QUICKSAMPLER = 2
SAMPLER_STS = 3
SAMPLER_CMS = 4
SAMPLER_SATSOLVER = 5
SAMPLER_APPMC3 = 6
SAMPLER_SPUR = 7


def parseIndSupport(indSupportFile):  # returns List of Independent Variables
    f = open(indSupportFile, "r")
    lines = f.readlines()
    f.close()
    indList = []
    numVars = 0
    for line in lines:
        if line.startswith("p cnf"):
            fields = line.split()
            numVars = int(fields[2])
        if line.startswith("c ind"):
            indList.extend(
                line.strip()
                .replace("c ind", "")
                .replace(" 0", "")
                .strip()
                .replace("v ", "")
                .split()
            )
    if len(indList) == 0:
        indList = [int(x) for x in range(1, numVars + 1)]
    else:
        indList = [int(x) for x in indList]
    return indList


def getSolutionFromSpur(inputFile, numSolutions, indVarList, seed):
    # inputFileSuffix = inputFile.split('/')[-1][:-4]
    tempOutputFile = inputFile + ".txt"
    cmd = './samplers/spur -seed %d -q -s %d -out %s -cnf %s' % (
        seed, numSolutions, tempOutputFile, inputFile)
    # if args.verbose:
    #     print("cmd: ", cmd)
    os.system(cmd)

    with open(tempOutputFile, 'r') as f:
        lines = f.readlines()

    solList = []
    startParse = False
    for line in lines:
        if (line.startswith('#START_SAMPLES')):
            startParse = True
            continue
        if (not(startParse)):
            continue
        if (line.startswith('#END_SAMPLES')):
            startParse = False
            continue
        if (line.startswith('UNSAT')):
            print("UNSAT")
            return -1

        fields = line.strip().split(',')
        solCount = int(fields[0])
        sol = []
        i = 1
        # print(fields)
        for x in list(fields[1]):
            if i in indVarList:
                if (x == '0'):
                    sol.append(-i)
                else:
                    sol.append(i)
            i += 1
        for i in range(solCount):
            solList.append(sol)

    os.unlink(tempOutputFile)
    return solList


def getSolutionFromUniGen3(inputFile, numSolutions, indVarList):
    #inputFilePrefix = inputFile.split("/")[-1][:-4]
    tempOutputFile = inputFile + ".txt"
    f = open(tempOutputFile, "w")
    f.close()

    cmd = './samplers/unigen3  -v 0 --samples ' + str(numSolutions) + ' --multisample 1 --kappa 0.635'
    cmd += ' --sampleout ' + str(tempOutputFile)
    cmd += ' ' + inputFile + ' > /dev/null 2>&1'

    print(cmd)
    os.system(cmd)
    f = open(tempOutputFile, "r")
    lines = f.readlines()
    f.close()
    solList = []
    for line in lines:
        line = line.strip(" 0\n")
        sample = line.split()
        sample = [int(i) for i in sample]
        solList.append(sample)

    solreturnList = solList
    if (len(solList) > numSolutions):
        solreturnList = random.sample(solList, numSolutions)

    os.unlink(str(tempOutputFile))
    return solreturnList


def getSolutionFromQuickSampler(inputFile, numSolutions, indVarList, seed):
    cmd = (
        "./samplers/quicksampler -n "
        + str(numSolutions * 5)
        + " "
        + str(inputFile)
        #+ " > /dev/null 2>&1"
        )
    print(cmd)
    os.system(cmd)
    cmd = "./samplers/z3 " + str(inputFile) #+ " > /dev/null 2>&1"
    os.system(cmd)
    i = 0
    if numSolutions > 1:
        i = 0

    f = open(inputFile + ".samples", "r")
    lines = f.readlines()
    f.close()
    f = open(inputFile + ".samples.valid", "r")
    validLines = f.readlines()
    f.close()
    solList = []
    for j in range(len(lines)):
        if validLines[j].strip() == "0":
            continue
        fields = lines[j].strip().split(":")
        sol = []
        i = 0
        for x in list(fields[1].strip()):
            if x == "0":
                sol.append(-1*indVarList[i])
            else:
                sol.append(indVarList[i])
            i += 1
        solList.append(sol)

    solreturnList = solList
    if len(solList) > numSolutions:
        solreturnList = random.sample(solList, numSolutions)
    elif len(solreturnList) < numSolutions:
        print("Did not find required number of solutions")
        exit(1)

    os.unlink(inputFile+'.samples')
    os.unlink(inputFile+'.samples.valid')

    return solreturnList


def getSolutionFromSTS(seed, inputFile, numSolutions, indVarList):
    kValue = 50
    samplingRounds = numSolutions/kValue + 1
    inputFileSuffix = inputFile.split('/')[-1][:-4]
    outputFile = tempfile.gettempdir()+'/'+inputFileSuffix+"sts.out"
    cmd = './samplers/STS -k='+str(kValue)+' -nsamples='+str(samplingRounds)+' '+str(inputFile)
    cmd += ' > '+str(outputFile)
    #if args.verbose:
    #    print("cmd: ", cmd)
    os.system(cmd)

    with open(outputFile, 'r') as f:
        lines = f.readlines()

    solList = []
    shouldStart = False
    for j in range(len(lines)):
        if(lines[j].strip() == 'Outputting samples:' or lines[j].strip() == 'start'):
            shouldStart = True
            continue
        if (lines[j].strip().startswith('Log') or lines[j].strip() == 'end'):
            shouldStart = False
        if (shouldStart):
            i = 0
            sol = []
            # valutions are 0 and 1 and in the same order as c ind.
            for x in list(lines[j].strip()):
                if (x == '0'):
                    sol.append(-1*indVarList[i])
                else:
                    sol.append(indVarList[i])
                i += 1
            solList.append(sol)

    solreturnList = solList
    if len(solList) > numSolutions:
        solreturnList = random.sample(solList, numSolutions)
    elif len(solList) < numSolutions:
        print(len(solList))
        print("STS Did not find required number of solutions")
        sys.exit(1)

    os.unlink(outputFile)
    return solreturnList


# @CHANGE_HERE : please make changes in the below block of code
""" this is the method where you could run your sampler for testing
Arguments : input file, number of solutions to be returned, list of independent variables
output : list of solutions """


def getSolutionFromCustomSampler(inputFile, numSolutions, indVarList):
    solreturnList = []
    """ write your code here """

    return solreturnList


def getSolutionFromSampler(inputFile, numSolutions, samplerType, indVarList, seed):

    if samplerType == SAMPLER_UNIGEN3:
        return getSolutionFromUniGen3(inputFile, numSolutions, indVarList)
    if samplerType == SAMPLER_QUICKSAMPLER:
        return getSolutionFromQuickSampler(inputFile, numSolutions, indVarList, seed)
    if samplerType == SAMPLER_STS:
        return getSolutionFromSTS(seed, inputFile, numSolutions, indVarList)
    if samplerType == SAMPLER_CMS:
        return getSolutionFromCMSsampler(inputFile, numSolutions, indVarList, seed)
    if samplerType == SAMPLER_APPMC3:
        return getSolutionFromAppmc3(inputFile, numSolutions, indVarList)
    if samplerType == SAMPLER_CUSTOM:
        return getSolutionFromCustomSampler(inputFile, numSolutions, indVarList)
    else:
        print("Error")
        return None


def baseline():
    """
    main
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sampler",
        type=int,
        help=str(SAMPLER_UNIGEN3)
        + " for UniGen3;\n"
        + str(SAMPLER_QUICKSAMPLER)
        + " for QuickSampler;\n"
        + str(SAMPLER_STS)
        + " for STS;\n",
        default=SAMPLER_STS,
        dest="samplertype",
    )
    parser.add_argument(
        "--eta", type=float, help="default = 1.6", default=1.6, dest="eta"
    )
    parser.add_argument(
        "--epsilon", type=float, help="default = 0.1", default=0.1, dest="epsilon"
    )
    parser.add_argument(
        "--delta", type=float, help="default = 0.1", default=0.1, dest="delta"
    )
    parser.add_argument(
        "--seed", type=int, help="default = 42", default=42, dest="seed"
    )
    parser.add_argument("input", help="input file")

    args = parser.parse_args()
    samplerType = args.samplertype
    eta, epsilon, delta = args.eta, args.epsilon, args.delta
    seed = args.seed
    inputFile = args.input
    outputFile = "/tmp/" + inputFile.split("/")[-1][:-4] + ".mc"

    samplerString = ""

    if samplerType == SAMPLER_UNIGEN3:
        samplerString = "UniGen3"
    if samplerType == SAMPLER_QUICKSAMPLER:
        samplerString = "QuickSampler"
    if samplerType == SAMPLER_STS:
        samplerString = "STS"

    # cmd = "mkdir tmpdir"
    # os.system(cmd)

    cmd = "./sharpSAT -decot 10 -decow 100 -tmpdir . -cs 3500 " + inputFile + "> " + outputFile
    os.system(cmd)
    # os.system("rm tmpdir/instance*")

    f = open(outputFile, "r")
    lines = f.readlines()
    f.close()

    if lines[-1].split()[2] == "exact":
        mc = int(lines[-1].split()[-1])
    else:
        raise(valueError)
    # print(mc)

    indVarList = parseIndSupport(inputFile)
    startsec = time.time()
    getSolutionFromSampler(inputFile = inputFile,
                            numSolutions = 100,
                            samplerType = samplerType,
                            indVarList = indVarList,
                            seed = seed)
    sample_time = time.time() - startsec
    # #sec = float(input("seconds: "))
    # qsec = float(input("qsec: "))
    # stssec = float(input("stssec: "))

    sample = (math.pow(mc, (2/3))) * (math.pow((eta - epsilon), (-8/3))) * (math.log(mc / delta, 2))
    print("input benchmark: ", inputFile.split("/")[-1])
    print("sampler under test: ", samplerString)
    print("#samples:", sample)
    print("time(s):", sample_time)
    print("total-time(s):", sample_time/100 * sample)
    # print("qtime(s):", qsec/100 * sample)
    # print("ststime(s):", stssec/100 * sample)


if __name__ == '__main__':
    baseline()
