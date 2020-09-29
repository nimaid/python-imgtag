# ImgTag
Simple XMP Image Tag & Metadata Editing Module

You must install `exempi` for your OS. For Debian:
```
sudo apt-get update && sudo apt-get install -y exempi
```

Once `exempi` is installed, install `imgtag` with:
```
python3 -m pip install -y imgtag
```

To use `imgtag`:
```python
from imgtag import ImgTag

# Open image for tag editing
test = ImgTag("test.jpg", force_case='lower', strip=True, no_duplicates=True)

# Print existing tags
print("Current tags:")
for tag in test.get_tags():
    print("  Tag:", tag)
print()

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