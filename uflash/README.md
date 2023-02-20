# uFlash

uFlash is a distribution testing framework that is desinged to test whether a given Horn-Sampler is epsilon-close to Uniform or it is eta-far from a uniform distribution.


## Getting Started



To run with the parameter values used in the paper, copy a benchmark to codes directory and run ```uflash```:



```

cp benchmarks/Net6_count_91.cnf codes/

cd codes

python uflash.py --eta 1.6 --epsilon 0.1 --delta 0.1 --sampler 1 --seed 42 Net6_count_91.cnf output

```

**IMPORTANT:** Before executing `uflash.py` please ensure that you have copied the `samplers` directory into the `codes` directory. Please refer to the `README.md` of mother directory.    

For the command-



```

python uflash.py --eta ETA --epsilon EPSILON --delta DELTA --sampler SAMPLER-TYPE --seed SEED mycnf.cnf OUTPUT

```



ETA takes values in (0,2),

EPSILON takes values in (0,0.33),

DELTA takes values in (0,0.5),

SEED takes integer values, and



SAMPLER-TYPE takes the following values:



* UniGen3 = 1

* QuickSampler = 2

* STS = 3


OUTPUT takes a filename to store output of uflash


### Samplers used



In the "samplers" directory, you will find 64-bit x86 Linux compiled binaries for:



* UniGen3- an almost-uniform sampler

* Quick Sampler

* STS
