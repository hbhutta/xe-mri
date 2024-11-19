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


# Installing GNU Octave
Install [GNU Octave](https://docs.octave.org/interpreter/Installation.html) with:
```bash
sudo apt install octave
```

Ensure that `octave` is in your bin with, for example:
```bash
cd bin && ls | grep octave
```

Check the installation version with:

```bash
octave --version
```