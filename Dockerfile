FROM python:3.10.8-slim-buster

# Update and install necessary packages
RUN apt-get update --no-cache && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends git dos2unix supervisor && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip3 install -U pip && pip3 install -U -r /requirements.txt

# Create working directory and set it
RUN mkdir /NewAuto
WORKDIR /NewAuto

# Copy the start script and convert line endings
COPY start.sh /start.sh
RUN dos2unix /start.sh && chmod +x /start.sh

# Copy the supervisord configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Set the command to run supervisord
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
