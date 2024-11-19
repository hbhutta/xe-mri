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