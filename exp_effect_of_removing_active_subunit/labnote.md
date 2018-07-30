---
title: Effect of removing fixed fraction of active subunits from a CaMKII/PP1 Switch
author: Dilawar Singh
date : \today 
header-includes:
    - \usepackage[]{ebgaramond}
    - \usepackage[]{chemfig}
    - \usepackage[]{pgfplots}
    - \usepackage[]{tikz}
    - \usepackage[]{siunitx}
---

Previously ( in experiment of  `../exp_MANY_VOXELS_COUPLED_WITH_DIFFUSION/`), we
saw that CaMKII/PP1 switch's **ON** state is sensitive to removal of active
subunits $x$ (due to diffusion of $x$ out of voxel/compartment ). In this
labnote, we quantify the effect of removing a fraction of active subunits $x$
from the system at rate comparable to diffusion of $x$.  ^[In a previous version
of this experiment, we removed all $x$ at different rate. See [this
labnote](https://labnotes.ncbs.res.in/bhalla/removing-active-subunit-x-camkiipp1-increases-state-residence-time-1).
Needless to say the effect of removing subunits was rather drastic. This labnote
creates more realistic situation by removing a certain fraction of $x$. The
diffusion process which is bi-directional is unlikely to remove all $x$ from one 
system without replacing many of them with other $x$s from neighbouring system. ]

In this experiment, we quantify this effect. 

# Summary of this labnote

Contrary to previous experiment (see footnote), we found that removal of active
subunit does not have very strong impact on switch unless all of active subunits
have been removed.

\begin{tikzpicture}[scale=1]
    \begin{axis}[
    xlabel=Fraction of $x$ removed,ylabel=Time spent in OFF state
    , grid style={draw=gray!20}, grid = both
    ]
    \addplot+ [color=blue] gnuplot [ raw gnuplot ] {
        plot "./summary.dat" using 1:2 with p;
    };
    \end{axis}
\end{tikzpicture}


# Experiment design

We setup additional reaction which converts $x$ into a dummy molecule $xs$.
Molecules $xs$ does not play any role in system. The forward rate is fixed to 1
and the backward rate is changed in each run.

$$\schemestart x \arrow{<=>[$k_f$][$k_b$]} xs \schemestop \label{reac:1} $$

Above reaction removes a certain fraction of $x$ by converting it into $xs$.
This fraction is given by $\frac{k_f}{k_f+k_b}$. This 'approximates' the effect
of removing active subunits from the CaMKII-PP1 switch by diffusion. 

For a diffusion coefficient of $D$ in a 1-D compartment of length $l$, the rate
constant $k_f = \frac{D}{l^2}$. For a typical value of $D=\SI{1}{\micro \meter^2
\per \second}$ in a 1-D compartment of length \SI{1}{\micro \meter}, $k_f = 1$.

## Model script

Since this model have non-trivial modifications, the script is maintained in
this directory itself. If the reference model _../camkii_pp1_scheme.py_ is changed 
significantly, then model file in this directory should be changed accordingly.

# Results

Following the plot of some runs.

\begin{@empty}
\newcommand{\fn}[1]{CaMKII-6+PP1-26+L-125e-9+N-1+diff-0_removal_kf1kb#1.dat_processed.dat}
\foreach \kb in {1000,10,1,0.1,0.005}
{
    Rate of reaction (see reaction \ref{reac:1} ) $k_f = 1$ and $k_b = \kb$.
    Fraction of $x$ removed \pgfmathsetmacro\rat{1/(\kb+1)} \rat.

    \edef\fileN{\fn{\kb}}

    \begin{tikzpicture}[scale=1]
    \begin{axis}[ xlabel=Time (days),ylabel=Active CaMKII
            , grid style={draw=gray!20}, grid = both, 
            , width = 0.6\linewidth, height = 4cm, scale only axis
            , ymax = 8, legend style={fill=none,draw=none}
        ]
        \addplot+ [no marks,thick] gnuplot [ raw gnuplot ] {
            plot "\fileN" using (column("time")/86400):"CaMKII*" every 50 with lines
        };
        \addplot+ gnuplot [ raw gnuplot ] {
            plot "\fileN" using (column("time")/86400):"x" every 50 with lines
        };
        \legend{CaMKII*, x}
    \end{axis}
    \end{tikzpicture} %
    \begin{tikzpicture}[scale=1]
    \begin{axis}[ xlabel=Active CaMKII
            , grid style={draw=gray!20}, grid = both, 
            , width = 0.4\linewidth, height = 4cm, scale only axis
            , ymax = 1.0
        ]
        \addplot+[no marks,fill=blue!20,hist={density,bins=7}] gnuplot [ raw gnuplot ] {
            plot "\fileN" using "CaMKII*" every 50;
        };
    \end{axis}
    \end{tikzpicture}
} 


\end{@empty}
