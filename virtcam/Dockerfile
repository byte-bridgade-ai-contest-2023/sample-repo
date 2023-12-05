FROM python:3-buster

# ensure pip is up to date
RUN pip install --upgrade pip

# install opencv dependencies
RUN apt-get update && \
    apt-get install -y \
      `# opencv requirements` \
      libsm6 libxext6 libxrender-dev \
      `# opencv video opening requirements` \
      libv4l-dev \
      libgl1-mesa-glx \
      v4l2loopback-utils

# install our requirements
WORKDIR /src
COPY requirements.txt /src/
RUN pip install --no-cache-dir -r /src/requirements.txt

# copy in the virtual backgrounds
COPY data/background*.jpg /src/data/
# run our fake camera script (with unbuffered output for easier debug)
COPY fake.py /src/
COPY bodypix.json /src/
COPY videocaptureasync.py /src/
ENTRYPOINT python fake.py
#ENTRYPOINT /bin/bash