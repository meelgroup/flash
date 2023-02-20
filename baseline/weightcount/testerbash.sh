for file in ../Benchmarks/*
do
	python3 weightregulariser.py  "$file"
done
mv temp/* ../bench/
rm -r temp
