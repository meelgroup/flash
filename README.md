# Flash



`Flash` is a framework developed to test whether a Horn-sampler is epsilon-close or eta-far from a given distribution with confidence greater than 1-delta.



The full paper has six Appendices(A-F).



Appendices A-E contain the theoretical justification for the theorems and lemmas mentioned in the paper.

Appendix F has the results for the entire set of benchmarks and all the tested samplers along with the comparisons of the performance of our testers with the baseline testers.

The results presented in the extended tables of Appendix F can be verified with the code and benchmarks presented in this folder.



## Requirements to run the code



* Python 3.6



To install the required libraries, run:



```

pip install -r requirements.txt

```



## Getting Started


The directory is subdivided into 3 parts: uflash, flash, baseline.

* The uflash directory contains codes and benchmarks to run `uFlash`. Also, one complete set of logs is already been given inside. To run `uFlash` you need to copy the sampler binaries inside the "codes" directory of uflash:

	```
	cp -r samplers/ uflash/codes/
	```


* The flash directory contains codes and benchmarks to run `Flash`. Also, One complete set of logs is already been given inside. To run `Flash` you need to copy the sampler binaries inside the "codes" directory of flash:

	```
	cp -r samplers/ flash/codes/
	```

* The baseine directory contains codes to obtain necessary information regarding baseline approach. To run the baseline codes again you need to copy the sampler binaries inside the directory:

	```
	cp -r samplers/ baseline/
	```
