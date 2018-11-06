FROM ubuntu:18.04
MAINTAINER Dilawar Singh <dilawar.s.rajput@gmail.com>

ENV PATH=/usr/local/bin:$PATH

RUN apt update && apt install wget git cmake -yy
RUN apt install texlive-full
RUN apt install python3-numpy python3-matplotlib python3-networkx python3-pandas python3-scipy -yy
RUN apt install graphviz python3-pip -yy
RUN python3 -m pip install pymoose --pre --user --upgrade 
RUN python -c 'import moose;print(moose.__file__);print(moose.__version__)'
RUN git clone https://github.com/dilawar/SinghAndBhalla_CaMKII_SubunitExchange_2018.git
RUN git clone https://bitbucket.org/dilawar/camkii-pp1-system 
CMD xterm
