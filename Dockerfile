FROM python:3-slim

# Install python requirements
COPY requirements.txt /tmp/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Copy server files
COPY redfishMockupCreate.py /usr/src/app/

# Env settings
WORKDIR /usr/src/app
ENTRYPOINT ["python", "/usr/src/app/redfishMockupCreate.py", "-D", "/mockup"]
