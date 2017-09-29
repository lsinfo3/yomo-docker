FROM monroe/base

MAINTAINER smartqoe@gmail.com

RUN  echo "export HOME=/" \
		&& export HOME=/ 

RUN echo "install dstat" \
        && apt-get update -q \
        && apt-get install -q -y dstat

RUN echo "install pciutils" \
        && export DEBIAN_FRONTEND=noninteractive \
		&& apt-get install -q -y pciutils

RUN echo "install numpy and psutil"
RUN apt-get update -q
RUN apt-get install -y libblas-dev liblapack-dev liblapacke-dev gfortran
RUN apt-get install -y python-pip 
RUN pip install numpy
RUN pip install psutil
		 

COPY files/* /opt/monroe/

ENTRYPOINT ["dumb-init", "--", "/bin/bash", "-e", "/opt/monroe/setup.sh"]
