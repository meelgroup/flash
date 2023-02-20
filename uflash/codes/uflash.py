from __future__ import print_function
import sys
import os
import math
import random
import argparse
import tempfile
import copy
import time


SAMPLER_UNIGEN3 = 1
SAMPLER_QUICKSAMPLER = 2
SAMPLER_STS = 3
SAMPLER_CMS = 4
SAMPLER_APPMC3 = 5
SAMPLER_CUSTOM = 6
SAMPLER_SPUR = 7
SAMPLER_WAPS = 8


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
        line = line.strip() #" 0\n"
        sample = line.split()
        sample = [int(i) for i in sample]
        solList.append(sample)

    solreturnList = solList
    if (len(solList) > numSolutions):
        solreturnList = random.sample(solList, numSolutions)

    os.unlink(str(tempOutputFile))
    return solreturnList


def getSolutionFromCMSsampler(inputFile, numSolutions, indVarList, newSeed):
    # inputFileSuffix = inputFile.split('/')[-1][:-4]
    # outputFile = tempfile.gettempdir()+'/'+inputFileSuffix+".out"
    tempOutputFile = inputFile + ".txt"

    cmd = "./samplers/cryptominisat5 --restart fixed --maple 0 --verb 0 --nobansol"
    cmd += " --scc 1 -n 1 --presimp 0 --polar rnd --freq 0.9999 --fixedconfl 100"
    cmd += " --random " + str(newSeed) + " --maxsol " + str(numSolutions)
    cmd += " --dumpresult " + tempOutputFile
    cmd += " " + inputFile + " > /dev/null 2>&1"

    # if args.verbose:
    #     print("cmd: ", cmd)
    os.system(cmd)

    with open(tempOutputFile, 'r') as f:
        lines = f.readlines()

    solList = []
    for line in lines:
        if line.strip() == 'SAT':
            continue

        sol = []
        lits = line.split(" ")
        for y in indVarList:
            if str(y) in lits:
                sol.append(y)

            if "-" + str(y) in lits:
                sol.append(-y)
        solList.append(sol)

    solreturnList = solList
    print('-'*50, solList)
    if len(solList) > numSolutions:
        solreturnList = random.sample(solList, numSolutions)
    if len(solList) < numSolutions:
        print("cryptominisat5 Did not find required number of solutions")
        sys.exit(1)
    os.unlink(tempOutputFile)
    return solreturnList


def getSolutionFromAppmc3(inputFile, numSolutions, indVarList):
    #inputFilePrefix = inputFile.split("/")[-1][:-4]
    tempOutputFile = inputFile + ".txt"
    f = open(tempOutputFile, "w")
    f.close()
    cmd = (
        "./samplers/approxmc3 "
        + inputFile
        + " --samples "
        + str(numSolutions)
        + " --sampleout "
        + str(tempOutputFile)
        #+ " > /dev/null 2>&1"
    )
    print(cmd)
    os.system(cmd)
    f = open(tempOutputFile, "r")
    lines = f.readlines()
    f.close()
    solList = []
    for line in lines:
        line = line.strip()
        freq = int(line.split(":")[0].strip())
        for _ in range(freq):
            sample = line.split(":")[1].strip()[:-2]
            sample = sample.split()
            sample = [int(i) for i in sample]
            solList.append(sample)

    solreturnList = solList
    if (len(solList) > numSolutions):
        solreturnList = random.sample(solList, numSolutions)

    os.unlink(str(tempOutputFile))
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


def getSolutionFromQuickSampler(inputFile, numSolutions, indVarList, seed):
    cmd = (
        "./samplers/quicksampler -n "
        + str(numSolutions * 10)
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

    print(len(solList))
    solreturnList = solList
    if len(solList) > numSolutions:
        solreturnList = random.sample(solList, numSolutions)
    elif len(solreturnList) < numSolutions:
        print("Did not find required number of solutions")
        exit(1)

    os.unlink(inputFile+'.samples')
    os.unlink(inputFile+'.samples.valid')

    return solreturnList


def getSolutionFromWAPS(inputFile, numSolutions):
    sampler = samp(cnfFile=inputFile)
    sampler.compile()
    sampler.parse()
    sampler.annotate()
    samples = sampler.sample(totalSamples=numSolutions)
    solList = list(samples)
    solList = [i.strip().split() for i in solList]
    solList = [[int(x) for x in i] for i in solList]
    return solList


def getSolutionFromIdeal(inputFile, numSolutions, samplerString, indVarList, seed):
    topass = (inputFile, numSolutions, indVarList, seed)
    if samplerString == "waps":
        return getSolutionFromWAPS(inputFile, numSolutions)
    if samplerString == "spur":
        return getSolutionFromSpur(*topass)



def project(sample, VarList):
    '''
    project sample on the VarList
    '''
    projectedSample = []
    for s in sample:
        if abs(s) in VarList:
            projectedSample.append(s)
    return projectedSample


def check_cnf(fname):
    """
    validating structure of .cnf
    """

    with open(fname, 'r') as f:
        lines = f.readlines()

    given_vars = None
    given_cls = None
    cls = 0
    max_var = 0
    for line in lines:
        line = line.strip()

        if len(line) == 0:
            print("ERROR: CNF is incorrectly formatted, empty line!")
            return False

        line = line.split()
        line = [l.strip() for l in line]

        if line[0] == "p":
            assert len(line) == 4
            assert line[1] == "cnf"
            given_vars = int(line[2])
            given_cls = int(line[3])
            continue

        if line[0] == "c" or line[0] == "w":
            continue

        cls +=1
        n_pos_lit = 0
        for l in line:
            var = abs(int(l))
            max_var = max(var, max_var)
            if (var == int(l) and var != 0):
                n_pos_lit += 1

        if n_pos_lit > 1:
            # number of positive literal is atmost 1 in Horn caluses
            print("ERROR: Not a valid Horn formula")
            return False

    if max_var > given_vars:
        print("ERROR: Number of variables given is LESS than the number of variables ued")
        print("ERROR: Vars in header: %d   max var: %d" % (given_vars, max_var))
        return False

    if cls != given_cls:
        print("ERROR: Number of clauses in header is DIFFERENT than the number of clauses in the CNF")
        print("ERROR: Claues in header: %d   clauses: %d" % (given_cls, cls))
        return False

    return True


def findWeightsForVariables(sampleSol, idealSol, numSolutions):
    """
    Finds rExtList
    """
    countList = []
    newVarList = []
    lenSol = len(sampleSol)
    # print("sampleSol:", sampleSol)
    tau = min(3,len(sampleSol))

    for _ in range(tau):
        countList.append(5)
        newVarList.append(4)
    rExtList = []
    oldVarList = []

    indexes = random.sample(range(len(sampleSol)), len(countList))

    idealVarList = [idealSol[i] for i in indexes]
    sampleVarList = [sampleSol[i] for i in indexes]

    print("idealVarList:", idealSol)
    print("sampleVarList:", sampleSol)
    print("idealVarList:", idealVarList)
    print("sampleVarList:", sampleVarList)

    assert len(idealVarList) == len(sampleVarList)
    for a, b in zip(idealVarList, sampleVarList):
        assert abs(int(a)) == abs(int(b))

    oldVarList.append(sampleVarList)
    oldVarList.append(idealVarList)
    rExtList.append(countList)
    rExtList.append(newVarList)
    rExtList.append(oldVarList)

    return rExtList


def pushVar(variable, cnfClauses):
    cnfLen = len(cnfClauses)
    for i in range(cnfLen):
        cnfClauses[i].append(variable)
    return cnfClauses


def getCNF(variable, binStr, sign, origTotalVars):
    cnfClauses = []
    binLen = len(binStr)
    if sign:
        cnfClauses.append([-(binLen + 1 + origTotalVars)])
    else:
        cnfClauses.append([binLen + 1 + origTotalVars])
    for i in range(binLen):
        newVar = int(binLen - i + origTotalVars)
        if sign == False:
            newVar = -1 * (binLen - i + origTotalVars)
        if binStr[binLen - i - 1] == "0":
            cnfClauses.append([int(-1 * newVar)])
        else:
            cnfClauses = pushVar(int(-1 * newVar), cnfClauses)
    pushVar(variable, cnfClauses)
    return cnfClauses


def constructChainFormula(originalVar, solCount, newVars, origTotalVars, invert):
    writeLines = ""
    binStr = str(bin(int(solCount)))[2:-1]
    binLen = len(binStr)
    for i in range(newVars - binLen - 1):
        binStr = "0" + binStr

    firstCNFClauses = getCNF(-int(originalVar), binStr, invert, origTotalVars)
    addedClauseNum = 0
    for i in range(len(firstCNFClauses)):
        addedClauseNum += 1
        for j in range(len(firstCNFClauses[i])):
            writeLines += str(firstCNFClauses[i][j]) + " "
        writeLines += "0\n"
    CNFClauses = []
    for i in range(len(CNFClauses)):
        if CNFClauses[i] in firstCNFClauses:
            continue
        addedClauseNum += 1
        for j in range(len(CNFClauses[i])):
            writeLines += str(CNFClauses[i][j]) + " "
        writeLines += "0\n"
    return (writeLines, addedClauseNum)


def newVars(numSolutions, Vars):
    """
    Returns relevant information for Chain formula blowup
    """

    n = len(Vars)
    N = numSolutions

    tau = min(4, n)

    N_ = int(math.ceil(N**(1/tau)))

    # for each commonVar we need to add one chain formula with x variables
    x = int(math.ceil(math.log(N_,2)))
    extendedList = []
    countList = []
    numVarList = []

    for _ in range(tau):
        countList.append(int(2**(x+1) - 1))
        numVarList.append(x+1)

    varsForchain = random.sample(Vars, len(countList))

    extendedList.append(countList)      # K list
    extendedList.append(numVarList)     # m list
    extendedList.append(varsForchain)
    return extendedList


# @returns whether new file was created and the list of independent variables
def constructNewFile(inputFile, tempFile, sampleSol, unifSol, origIndVarList, numSolutions):
    sampleMap = {}
    unifMap = {}
    diffIndex1 = -1
    diffIndex2 = -1
    commonVars = [] # common True literals
    diffVars = []   # literals - common True literals
    for i in sampleSol:
        if (not(abs(int(i)) in origIndVarList)):
            continue
        if (int(i) != 0):
            sampleMap[abs(int(i))]=int(int(i)/abs(int(i)))
    for j in unifSol:
        if (not(abs(int(j)) in origIndVarList)):
            continue
        if (int(j) != 0):
            unifMap[abs(int(j))] = int(int(j)/abs(int(j)))
            if (abs(int(j)) in sampleMap):
                if (sampleMap[abs(int(j))] != unifMap[abs(int(j))]):
                    diffVars.append(int(j))
                    if(unifMap[abs(int(j))]==1 and diffIndex2 == -1):
                        diffIndex2 = abs(int(j))
                    elif(unifMap[abs(int(j))]==-1 and diffIndex1 == -1) :
                        diffIndex1 = abs(int(j))
                else:
                    commonVars.append(int(j))
    print("DIFFVARS:",diffVars)

    if (diffIndex1 == -1 and diffIndex2==-1):
        print("both samples are the same, error condition")
        print(sampleSol, unifSol)
        exit(-1)

    solClause = ""
    f = open(inputFile, "r")
    lines = f.readlines()
    f.close()

    #---------------------------Old formula--------------------------#
    oldClauseStr = ""
    for line in lines:
        if line.strip().startswith("p cnf"):
            numVar = int(line.strip().split()[2])
            numClause = int(line.strip().split()[3])
        else:
            if line.strip().startswith("w"):
                oldClauseStr += line.strip()+"\n"
            elif not (line.strip().startswith("c")):
                oldClauseStr += line.strip()+"\n"


    #----------------Adding constraints to ensure only two clauses-----------#
    cmmTrueLits, cmmFalseLits, uncmmLits = [], [], []
    for i in origIndVarList:
        if (sampleMap[int(i)] == unifMap[int(i)]):
            if (sampleMap[int(i)] == 1):
                cmmTrueLits.append(int(i))
            elif (sampleMap[int(i)] == -1):
                cmmFalseLits.append(int(i))
        else:
            uncmmLits.append(int(i))

    if cmmTrueLits != []:
        for lit in cmmTrueLits[1:]:
            numClause += 2
            solClause += str(-1 * cmmTrueLits[0])+' '+str(lit)+' 0\n'
            solClause += str(cmmTrueLits[0])+' '+str(-1 * lit)+' 0\n'
        numClause += 1
        solClause += str(cmmTrueLits[0])+' 0\n'

    if cmmFalseLits != []:
        for lit in cmmFalseLits[1:]:
            numClause += 2
            solClause += str(-1 * cmmFalseLits[0])+' '+str(lit)+' 0\n'
            solClause += str(cmmFalseLits[0])+' '+str(-1 * lit)+' 0\n'
        numClause += 1
        solClause += str(-1 * cmmFalseLits[0])+' 0\n'

    diff0 = diff1 = -1
    for lit in uncmmLits:
        if sampleMap[lit] == -1:
            diff0 = lit
        else:
            diff1 = lit
        if diff0 != -1 and diff1 != -1:
            break

    for lit in uncmmLits:
        if diff0 != -1 and lit != diff0 and sampleMap[lit] == sampleMap[diff0]:
            numClause += 2
            solClause += str(-1 * diff0)+' '+str(lit)+' 0\n'
            solClause += str(diff0)+' '+str(-1 * lit)+' 0\n'

        elif diff1 != -1 and lit != diff1 and sampleMap[lit] == sampleMap[diff1]:
            numClause += 2
            solClause += str(-1 * diff1)+' '+str(lit)+' 0\n'
            solClause += str(diff1)+' '+str(-1 * lit)+' 0\n'

    if diff0 != -1 and diff1 != -1:
        numClause += 1
        solClause += str(-1 * diff1) +' '+str(-1 * diff0)+' 0\n'


    #---------------------construct Chain blowup-----------------------#
    extendedList = newVars(numSolutions, diffVars)
    countList = extendedList[0]
    newVarList = extendedList[1]
    print("Extended List:", extendedList)

    # blowup = int(math.log(2*math.log(numSolutions,2),2))
    # diffVars = random.sample(diffVars,min(int(len(diffVars)/2**3),blowup)) # blowup
    # print("DIFFVARS after sampling:",diffVars)
    # print(countList)
    # print(newVarList)

    invert = True
    seenVars = []
    currentNumVar = numVar

    index = 0
    for i in extendedList[2]:
        addedClause = ''
        addedClauseNum = 0
        if(not(i in seenVars)):
            seenVars.append(i)
            sign = int(abs(i)/i)
            (addedClause,addedClauseNum) = constructChainFormula(
                    int(sign * abs(i)),int(countList[index]),\
                    int(newVarList[index]), currentNumVar,invert)
            currentNumVar += int(newVarList[index])
            numClause += addedClauseNum
            solClause += addedClause
            print("addedClause", addedClause)
            (addedClause,addedClauseNum) = constructChainFormula(
                    int(-sign * abs(i)),int(countList[index]),\
                    int(newVarList[index]), currentNumVar,invert)
            currentNumVar += int(newVarList[index])
            numClause += addedClauseNum
            solClause += addedClause
            print("addedClause", addedClause)
            index += 1

    #----------------------construct formula-----------------------------#
    tempIndVarList =[]
    indStr = "c ind "
    indIter = 1
    for i in origIndVarList:
        if indIter % 10 == 0:
            indStr += " 0\nc ind "
        indStr += str(i) + " "
        indIter += 1
        tempIndVarList.append(i)
    for i in range(numVar, currentNumVar + 1):
        if indIter % 10 == 0:
            indStr += " 0\nc ind "
        indStr += str(i) + " "
        indIter += 1
        tempIndVarList.append(i)


    indStr += " 0\n"
    headStr = "p cnf " + str(currentNumVar) + " " + str(numClause) + "\n"
    writeStr = headStr + indStr
    writeStr += solClause
    writeStr += oldClauseStr

    f = open(tempFile, "w")
    f.write(writeStr)
    f.close()
    return tempIndVarList


def constructKernel(inputFile, tempFile, samplerSample, idealSample, numSolutions, origIndVarList):
    # rExtList = findWeightsForVariables(samplerSample, idealSample, numSolutions)
    # print("rExtList:", rExtList)
    tempIndVarList = constructNewFile(inputFile, tempFile, samplerSample, idealSample, origIndVarList, numSolutions)
    return tempIndVarList

# Returns 1 if Ideal and 0 otherwise
def biasFind(sample1, sample2, solList, indVarList, file):
    solMap = {}
    numSolutions = len(solList)
    for sol in solList:
        solution = ""
        solFields = sol
        solFields.sort(key=abs)
        for entry in solFields:
            if (abs(entry)) in indVarList:
                solution += str(entry) + " "
        if solution in solMap.keys():
            solMap[solution] += 1
        else:
            solMap[solution] = 1

    if not (bool(solMap)):
        print("No Solutions were given to the test")
        exit(1)
    print("c Printing solMap")
    print(solMap)

    print("solList[0]", solList[0])
    print("sigma1 ", sample1)
    print("sigma2 ", sample2)

    indx1, indx2, indx3 = -1, -1, -1
    for i in range(len(solList)):
        if len(set(solList[i]).intersection(set(sample1))) == len(sample1):
            indx1 = i
        elif len(set(solList[i]).intersection(set(sample2))) == len(sample2):
            indx2 = i
        else:
            indx3 = i
        if indx1 != -1 and indx2 != -1 and indx3 != -1:
            break
    print("indexes", indx1, indx2, indx3)

    solution1 = ""
    if indx1 != -1:
        for i in solList[indx1]:
            if abs(i) in indVarList:
                solution1 += str(i) + " "

    solution2 = ""
    if indx2 != -1:
        for i in solList[indx2]:
            if abs(i) in indVarList:
                solution2 += str(i) + " "

    solution3 = ""
    if indx3 != -1:
        for i in solList[indx3]:
            if abs(i) in indVarList:
                solution3 += str(i) + " "
    print("sigma1:", solMap.get(solution1, 0),
          "sigma2:", solMap.get(solution2, 0),
          "zer0:", solMap.get(solution3, 0))
    file.write("sigma1: {0}, sigma2: {1}, zer0: {2}\n".format(
                solMap.get(solution1, 0),
                solMap.get(solution2, 0),
                solMap.get(solution3, 0)))

    return solMap.get(solution1, 0)*1.0/(solMap.get(solution1, 0) + solMap.get(solution2, 0)), solMap.get(solution3, 0)


def flash():

    start_time = time.time()

    parser = argparse.ArgumentParser()
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
        "--sampler",
        type=int,
        help=str(SAMPLER_UNIGEN3)
        + " for UniGen3;\n"
        + str(SAMPLER_QUICKSAMPLER)
        + " for QuickSampler;\n"
        + str(SAMPLER_STS)
        + " for STS;\n",
        default=SAMPLER_QUICKSAMPLER,
        dest="samplertype",
    )
    parser.add_argument(
        "--nnf", type=int, default=0, help="set to 1 to keep the compiled nnf and other logs", dest="nnf")

    parser.add_argument("--seed", type=int, dest="seed", default=420)
    parser.add_argument("input", help="input file")
    parser.add_argument("output", help="output file")

    args = parser.parse_args()

    samplerType = args.samplertype
    UserInputFile = args.input

    print("This is the user input:--", UserInputFile)
    isHorn = check_cnf(UserInputFile)
    print("isHorn : ", isHorn)
    if not isHorn:
        raise("inputError: inputFile is not Horn")
        exit(-1)

    inputFilePrefix = "sampler_" + str(samplerType) + "_" + UserInputFile.split("/")[-1][:-4]
    cmd = "cp " + UserInputFile + " " +  inputFilePrefix + ".cnf"
    os.system(cmd)
    inputFile = inputFilePrefix + ".cnf"

    indVarList = parseIndSupport(UserInputFile)

    eta = args.eta
    epsilon = args.epsilon
    delta = args.delta
    outputFile = args.output
    nnf = args.nnf
    seed = args.seed
    random.seed(seed)
    hop = 1000

    f = open(outputFile, "w")
    f.close()

    samplerString = ""

    if samplerType == SAMPLER_UNIGEN3:
        samplerString = "UniGen3"
    if samplerType == SAMPLER_QUICKSAMPLER:
        samplerString = "QuickSampler"
    if samplerType == SAMPLER_STS:
        samplerString = "STS"
    if samplerType == SAMPLER_CUSTOM:
        samplerString = "CustomSampler"
    if samplerType == SAMPLER_APPMC3:
        samplerString = "AppMC3"
    if samplerType == SAMPLER_CMS:
        samplerString = "CMSGen"

    breakExperiment = False
    totalSolutionsGenerated = 0
    totalIdealSamples = 0

    # t = int(math.ceil(math.log(1/delta)/math.log(10.0/(10 - (eta - 10*epsilon)*eta))))
    t = int(math.ceil(math.log(1/delta) * 10.0/((eta - 9*epsilon)*eta)))
    pre_numSolutions = int(math.log(2 * t/delta))

    print("# of times the test will run", t)
    print("#vars after Unweighted= ",len(indVarList))
    print("#sample pairs we need to check :"+str(t))
    print('#pre_numSolutions : ' + str(pre_numSolutions))

    L = (1+epsilon)/2
    H = (1 + (eta+9*epsilon)/4) / (2 + (eta+9*epsilon)/4)
    T = (L + H)/2
    numSolutions = int(8 * pre_numSolutions*H/(H-L)**2)
    X = 2 * (1 - epsilon) / (3 - epsilon)
    MaxSolutions = int((math.sqrt(pre_numSolutions) + math.sqrt(pre_numSolutions + 4 * numSolutions * X)) / (2 * X))**2

    print("H: {0}, L:{1}, Threshold T : {2}".format(H,L,T))

    print("numSol", numSolutions)
    print("Maxsol (contains numSol many [sigma1 + sigma2] with high prob):", MaxSolutions)


    f_out = open(outputFile, "a")
    f_out.write(""" t: {0} delta: {1:.3}\n eta: {1:.3}\n epsilon: {1:.3}\n""".format(
            t, delta, eta, epsilon,))
    f_out.write("L: {0}\t H: {1}\t Threshold T : {2}\n".format(L, H, T))
    f_out.write("numSolutions : {0}\t MaxSolutions : {1}\n".format(numSolutions, MaxSolutions))
    f_out.write("\n")
    f_out.close()

    tempFile = inputFile[:-4] + "_t.cnf"    # contains Kernel-output formula

    i = 0

    while i < t:

        f = open(outputFile, "a")
        f.write("-"*10 + "\nLoop " + str(i) + " of " + inputFile + ":\n" + "-"*10 + "\n")
        print("-"*10 + "\n\nLoop " + str(i) + ":\n" + "-"*10 + "\n")
        seed += 1

        idealSample = getSolutionFromIdeal(inputFile = inputFile,
                                        numSolutions = 1,
                                        samplerString = "spur",
                                        indVarList = indVarList,
                                        seed = seed)[0]
        samplerSample = getSolutionFromSampler(inputFile = inputFile,
                                            numSolutions = 1,
                                            samplerType = samplerType,
                                            indVarList = indVarList,
                                            seed = seed)[0]

        print("indVarList: {0}, [len: {1}]".format(indVarList, len(indVarList)))

        print("sampler-sample (sigma1):", samplerSample)
        print("uniform-sample (sigma2):", idealSample)

        # loop out?
        if set(samplerSample) == set(idealSample):
            print("no two different witnesses found")
            continue

        totalIdealSamples += 1
        totalSolutionsGenerated += 1 #t

        # print("projectedsamplersample", len(projectedsamplerSample))
        # print("idealsample", len(projectedidealSample))

        tempIndVarList = constructKernel(inputFile = inputFile,
                                         tempFile = tempFile,
                                         samplerSample = samplerSample,
                                         idealSample = idealSample,
                                         numSolutions = MaxSolutions,
                                         origIndVarList = indVarList)
        print("isHorn:",check_cnf(tempFile))
        samplinglist = tempIndVarList
        print("file was constructed with these", samplerSample, idealSample)
        print("tempIndVarList:", tempIndVarList, "\nsamplinglist:", samplinglist)
        f.write("file was constructed with these {0}, {1} \n".format(str(samplerSample), str(idealSample)))

        if(MaxSolutions > 10**6):
            print("Looking for more than 10**8 solutions", MaxSolutions)
            print("too many to ask ,so quitting here")
            continue

        # solList = getSolutionFromSampler(inputFile = tempFile,
        #                                  numSolutions = MaxSolutions,
        #                                  samplerType = samplerType,
        #                                  indVarList = samplinglist,
        #                                  seed = seed)
        # seed += 1
        sampled = 0
        solList = []
        for iter in range(int(MaxSolutions / hop) + 1):
            solList += getSolutionFromSampler(inputFile = tempFile,
                                             numSolutions = min(hop, MaxSolutions - sampled),
                                             samplerType = samplerType,
                                             indVarList = samplinglist,
                                             seed = seed)
            sampled += hop
            seed += 1
        bias, n0 = biasFind(samplerSample, idealSample, solList, indVarList, f)
        totalSolutionsGenerated += MaxSolutions
        print("loThresh:", T)
        print("bias", bias)
        f.write("Bias calculated: {0}\n".format (bias))
        f.close()

        if bias > T or n0 > MaxSolutions - numSolutions:
            f = open(outputFile, "a")
            f.write(
                """Sampler: {0} RejectIteration:{1} TotalSolutionsGenerated:{2} TotalIdealSamples:{3}\n""".format(
                    samplerString, i, totalSolutionsGenerated, totalIdealSamples
                )
            )
            f.write( "\n\n time taken : {0}\n".format(time.time() - start_time) )
            f.close()
            breakExperiment = True
            print("Rejected at iteration:", i)
            print("NumSol:", totalSolutionsGenerated)
            cmd = "mv " + tempFile + " " + tempFile[:-4] + "_" + str(samplerType) + "_rejectionWitness.cnf"
            os.system(cmd)
            break

        cmd = "rm " + tempFile
        os.system(cmd)

        print("Accepted")
        if (i >= t-1):
            print("All rounds passed")
            print("NumSol", totalSolutionsGenerated)
        i+= 1

    if not (breakExperiment):
        f = open(outputFile, "a")
        f.write(
            """Sampler: {0} Accept:1 TotalSolutionsGenerated: {1} TotalIdealSamples: {2}\n""".format(
               samplerString, totalSolutionsGenerated, totalIdealSamples
            )
        )
        f.write( "\n\n time taken : {0}\n".format(time.time() - start_time) )
        f.close()
    if (nnf == 0):
        os.system("rm *cnf.*  > /dev/null 2>&1 ")

    cmd = "rm " + inputFile
    os.system(cmd)

if __name__ == "__main__":
    flash()
