# Uniformly distributed CaMKII in PSD with and without SU.

This data is used in `Figure 4F`.

## How to run

    $ cmake .
    $ make -j4 

It will generate the data and plot them. No sample data is added to this repo
since it is over 1.5GB.

One sample plot.

![Sample plot](./1b14d902e81f42687023f2346473da9c.png)

### Optional

To run a single instance of experiment run

    $ ./run_single_exp.sh 

$ Appendix

Two directories contains two good run.

- ./DATA_CaMKII_SIZE4/
- ./DATA_CaMKII_SIZE6/

Go to any of them and run `./analyze_exp.py` script.
