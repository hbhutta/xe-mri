# Specify base image
FROM ubuntu

# Install executables
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    nifti-bin

# Copy files in this directory into the container
COPY . .

# Install Python dependencies
RUN ls -alh && \
    nifti_tool -ver && \
    python3 --version && \
    python3 -m venv xe-mri-venv && \
    cd xe-mri-venv && \
    source bin/activate && \
    pip3 install -r requirements.txt && \
    pip3 list

# Run pipeline
ENTRYPOINT ["python", "main.py"]

# Usage (--help flag): docker run --help 
# Usage (--dir flag): docker run --dir <dir>


