set table "figure_exchange_rate.pgf-plot.table"; set format "%.5f"
set format "%.7e";; set datafile separator ","; plot "< cat ./CM1e-3_rg0.5541*_rl0.4832*.csv" using "time":"colocalization_perc" every 20; 
