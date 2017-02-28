FROM monroe/base

MAINTAINER smartqoe@gmail.com

RUN  echo "export HOME=/" \
		&& export HOME=/ 

RUN echo "install additional packages" \
        && apt-get update \
        && export DEBIAN_FRONTEND=noninteractive \
        && apt-get update -q \
        && apt-get install -q -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" tshark 


COPY files/* /opt/monroe/

ENTRYPOINT ["dumb-init", "--", "/bin/bash", "-e", "/opt/monroe/setup.sh"]
