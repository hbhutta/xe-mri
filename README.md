
# About
This pipeline registers MRI to CT images for a patient (or a batch of patients)
and applies the forward transforms from the registration to the 
ventilation images. `--dir` specifies either a single patient directory or a batch of patient directories.

# Installing dependencies
Only install locally installed packages (excludes globally installed packages) and does not ask for user input
```bash
pip freeze --local --no-input > requirements.txt
```
# Usage
If we have a directory called `PIm_0123/`, we can run the pipeline with:
```bash
git clone https://github.com/hbhutta/xe-mri.git
cd xe-mri
docker build -t xe_mri_image ./Dockerfile
docker run xe_mri_image --dir PIm_0123/
```

To get more information about flags, change the last command to:
```bash
docker run xe_mri_image --help
```
