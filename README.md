This registers MRI to CT images for a patient (or a batch of patients)
and applies the forward transforms from the registration to the 
ventilation images


Run pipeline with

```python

python main.py --dir DIR
``` 

`DIR` is either a single patient directory or a batch of patient directories.

For more explanation of the flags used to run `main.py`, run:

```python
python main.py --help
```

# Installing dependencies
Only install locally installed packages (excludes globally installed packages) and does not ask for user input
```bash
pip freeze --local --no-input > requirements.txt
```

# Refactoring updates
In the current design `utils.py` has many unrelated functions put together in one file. `utils.py` should not just be a dump of various utility functions, these functions should at least be related somehow. 

`utils.py` can be made more organized by making a separate subclass of `nib.nifti1.Nifti1Image` and then making any NIFTI related functions class methods of this subclass. This would also be object-oriented.

# Using Docker
Use the Dockerfile to build an image

Run a container from the image
