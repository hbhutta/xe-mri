
# Install Python and other executables that will live inside the bin file
RUN apt-get update && apt-get install -y \
        python \

# Install the python packages based on the requirements.txt file
# in the local folder (git repo).
# Also ensure that unnecessary/garbage packages are removed before 
# running this
COPY setup/requirements.txt requirements.txt
RUN pip install -r requirements.txt


