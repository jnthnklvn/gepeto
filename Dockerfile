# using ubuntu LTS version
FROM --platform=linux/amd64 python:3.11-slim-bullseye AS python-image

RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
            build-essential \
            libssl-dev \
            ca-certificates \
            libasound2 \
            wget \
            ffmpeg \
    ; \
	rm -rf /var/lib/apt/lists/*

# Set the working directory to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY . .

# make sure all messages always reach console
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "app.py"]
