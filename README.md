# ImgTag
### Simple XMP Image Tag & Metadata Editing Module

It is recomended to install using Conda to create a virtual python environment, as it makes it easy to install and manage different packages. Use the following commands to set up an environment:
```
conda env create -f environment.yml
conda activate imgtag
```

<br/>

If you close to install manually, you must install `exempi` for your OS.

For Debian:
```
sudo apt-get install -y exempi
```
For a Conda environment:
```
conda install -c conda-forge exempi
```

Once `exempi` is installed, install `imgtag` with:
```
python3 -m pip install -y imgtag
```

<br/>

To use `imgtag`:
```python
from imgtag import ImgTag

# Open image for tag editing
test = ImgTag(
           filename="test.jpg", # The image file
           force_case="lower",  # Converts the case of all tags
                                # Can be `None`, `"lower"`, `"upper"`
                                # Default: None
           strip=True,          # Strips whitespace from the ends of all tags
                                # Default: True
           no_duplicates=True   # Removes all duplicate tags (case sensitive)
                                # Default: True
       )

# Print existing tags
print("Current tags:")
for tag in test.get_tags():
    print("  Tag:", tag)

# Add tags
test.add_tags(["sleepy", "happy"])

# Remove tags
test.remove_tags(["cute"])

# Set tags, removing all existing tags
test.set_tags(["dog", "good boy"])

# Save changes and close file
test.close()

# Re-open for tag editing
test.open()

# Remove all tags
test.clear_tags()

# Delete the ImgTag object, automatically saving and closing the file
del(test)
```