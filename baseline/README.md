# baseline approach

we wrote this code to compare our results to baseline approach introduced by [Batu et.al](https://arxiv.org/abs/1009.5397).


## Getting Started



To run with the parameter values used in the paper, copy a benchmark from ```flash``` directory to this directory and run:



```

cp ../uflash/benchmarks/Net6_count_91.cnf ./

python base.py --eta 1.6 --epsilon 0.1 --delta 0.1 --sampler 1 --seed 42 Net6_count_91.cnf

```

**IMPORTANT:** Before executing `base.py` and `base_w.py` please ensure that you have copied the `samplers` directory into this directory. Please refer to the `README.md` of mother directory.    

For the command-



```

python base.py --eta ETA --epsilon EPSILON --delta DELTA --sampler SAMPLER-TYPE --seed SEED mycnf.cnf

```



ETA takes values in (0,2),

EPSILON takes values in (0,0.33),

DELTA takes values in (0,0.5),

SEED takes integer values, and



SAMPLER-TYPE takes the following values:



* UniGen3 = 1

* QuickSampler = 2

* STS = 3


### Samplers used



In the "samplers" directory, you will find 64-bit x86 Linux compiled binaries for:



* UniGen3- an almost-uniform sampler

* Quick Sampler

* STS
