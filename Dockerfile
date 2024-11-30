# Specify OS
FROM ubuntu

# Install executables
RUN apt-get update && apt-get install --yes-assume \
    python \ # Latest Python version
    nifti_tool # Any additional packages

# Install Python dependencies
COPY setup/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Run pipeline
ENTRYPOINT ["python", "main.py"]


