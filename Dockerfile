
# Install executables
RUN apt-get update && apt-get install --yes-assume \
    python \
    nifti_tool

# Install Python dependencies
COPY setup/requirements.txt requirements.txt
RUN pip install -r requirements.txt


