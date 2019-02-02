# Invoke with docker run -p 8000:80 <dockerimageid>
# Then use by browsing http://localhost:8000
FROM debian:9
MAINTAINER bruno.cornec@hpe.com
ENV DEBIAN_FRONTEND noninterative
# Install deps for Redfish mockup
RUN apt-get update
RUN apt-get -y install apache2 unzip sed patch vim wget iproute2 python3 python3-requests
# Do not merge as the previous layer is in common with the Server and this is a temporary hack
RUN apt-get -y install curl
EXPOSE 80
RUN mkdir -p /mockup/redfishtoollib
COPY redfishMockupCreate.py /mockup
COPY redfishtoollib/__init__.py /mockup/redfishtoollib
COPY redfishtoollib/redfishtoolTransport.py /mockup/redfishtoollib
COPY redfishtoollib/ServiceRoot.py /mockup/redfishtoollib
COPY run-mockup.sh /mockup
#ENV MODELIP=$MODELIP
CMD /mockup/run-mockup.sh
