
# About
This pipeline registers MRI to CT images for a patient (or a batch of patients)
and applies the forward transforms from the registration to the 
ventilation images. `--dir` specifies either a single patient directory or a batch of patient directories.

For more information about the flag, run:
```
docker run --help
```

# Installing dependencies
Only install locally installed packages (excludes globally installed packages) and does not ask for user input

```bash
pip freeze --local --no-input > requirements.txt
```

# Refactoring updates
In the current design `utils.py` has many unrelated functions put together in one file. `utils.py` should not just be a dump of various utility functions, these functions should at least be related somehow. 

`utils.py` can be made more organized by making a separate subclass of `nib.nifti1.Nifti1Image` and then making any NIFTI related functions class methods of this subclass. This would also be object-oriented.

# Usage
If we have a directory called `PIm_0123/`, we can run the pipeline with:
```bash
docker run --dir PIm_0123
```
