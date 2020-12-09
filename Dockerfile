FROM ubuntu:18.04 

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get --no-install-recommends install -yq git wget cmake build-essential \
    libgl1-mesa-dev libsdl2-dev \
    libsdl2-image-dev libsdl2-ttf-dev libsdl2-gfx-dev libboost-all-dev \
    libdirectfb-dev libst-dev mesa-utils xvfb x11vnc \
    libsdl-sge-dev python3-pip
RUN apt install -y ffmpeg
RUN apt install -y nodejs npm
# RUN npm install n -get
# RUN n stable
# RUN apt purge -y nodejs npm

# python config
ENV PATH /usr/bin:$PATH
RUN mkdir /work
COPY ./requirements.txt /work
RUN python3 -m pip install --upgrade pip setuptools
RUN pip3 install -r /work/requirements.txt

# GFootball environment
# Make sure that the Branch in git clone and in wget call matches !!
RUN git clone -b v2.5 https://github.com/google-research/football.git
RUN mkdir -p football/third_party/gfootball_engine/lib
RUN wget https://storage.googleapis.com/gfootball/prebuilt_gameplayfootball_v2.5.so -O football/third_party/gfootball_engine/lib/prebuilt_gameplayfootball.so

# Custom files to match builtin-AI
RUN wget https://gist.githubusercontent.com/RaffaeleMorganti/04192739d0a5a518ac253889eb83c6f1/raw/c09f3d602ea89e66daeda96574d966949a2896ce/football_action_set.py -O football/gfootball/env/football_action_set.py
RUN cd football && GFOOTBALL_USE_PREBUILT_SO=1 pip3 install -q .

# copy the local vscode config
# RUN mkdir ~/.vscode
# COPY ~/.vscode/ ~/.vscode/ 

# make for working directry
WORKDIR /work
