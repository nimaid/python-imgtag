import libxmp
import warnings
import os
import shutil
from math import floor
import resource
import psutil
import tempfile

__DEFAULT_MEMORY_LIMIT_RATIO__ = 0.8 # If more than this percent of available memory is used, an error is returned
__DEFAULT_BLOCK_SIZE__ = 1 * (1024*1024) # 1 MiB

def set_memory_limit(limit_ratio=__DEFAULT_MEMORY_LIMIT_RATIO__):
    # Sets a memory limit based on a percentage of available memory at the time of calling
    if limit_ratio == None:
        # No limit
        resource.setrlimit(resource.RLIMIT_AS, (-1, -1))
    else:
        if type(limit_ratio) not in [float, int]:
            raise TypeError("The parameter 'limit_ratio' requires a float greater than 0 and less than or equal to 1")
        if limit_ratio <= 0 or limit_ratio > 1:
            raise ValueError("The parameter 'limit_ratio' requires a float greater than 0 and less than or equal to 1")
        
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        available_memory = psutil.virtual_memory().available
        resource.setrlimit(resource.RLIMIT_AS, (round(available_memory * limit_ratio), hard))

def strip_file_blank_space(filename, block_size=__DEFAULT_BLOCK_SIZE__):
    # Strip blank space at the end of a file, and return the new file size
    file_end_loc = None # This will be used if the file is larger than the block size
    simple_data = None # This is used if the file is smaller than the block size
    with open(filename, "rb") as f:
        # Get original file size
        filesize = os.fstat(f.fileno()).st_size
        # Test if file size is less than (or equal to) the block size
        if filesize <= block_size:
            # Load data to do a normal rstrip all in-memory
            simple_data = f.read()
        else:
            # Compute number of whole blocks (remainder at beginning processed seperately)
            num_whole_blocks = floor(filesize / block_size)
            # Compute number of remaining bytes
            num_bytes_partial_block = filesize - (num_whole_blocks * block_size)
            # Go through each block, looking for the end location
            for block in range(num_whole_blocks):
                # Set file position
                current_position = filesize - ((block+1) * block_size)
                f.seek(current_position)
                # Read current block
                block_data = f.read(block_size)
                # Strip current block from right side
                block_data = block_data.rstrip(b"\x00")
                # Test if the block data was all zeros
                if len(block_data) == 0:
                    # Move on to next block
                    continue
                # If it was not all zeros
                else:
                    # Find the location in the file where the real data ends
                    blocks_not_processed = num_whole_blocks - (block+1)
                    file_end_loc = num_bytes_partial_block + (blocks_not_processed * block_size) + len(block_data)
                    break
            # Test if the end location was not found
            if file_end_loc == None:
                # Read partial block
                f.seek(0)
                partial_block_data = f.read(num_bytes_partial_block)
                # Strip from the right side
                partial_block_data = partial_block_data.rstrip(b"\x00")
                # Test if this block (and therefore the entire file) is zeros
                if len(partial_block_data) == 0:
                    # Warn about the empty file
                    warnings.warn("File was all zeros and will be replaced with an empty file")
                # Set the location where the real data begins
                file_end_loc = len(partial_block_data)
    
    # If we are doing a normal strip:
    if simple_data != None:
        # Strip right leading null bytes
        simple_data = simple_data.rstrip(b'\x00')
        # Directly replace file
        with open(filename, "wb") as f:
            f.write(simple_data)
            new_filesize = os.fstat(f.fileno()).st_size
        # Return the new file size
        return len(simple_data)
    # If we are doing a block-by-block copy and replace
    else:
        # Create temporary file (do not delete, will move myself
        temp_file = tempfile.NamedTemporaryFile(mode="wb", delete=False)
        # Open the source file for reading
        with open(filename, "rb") as f:
            # Test if data is smaller than (or equal to) the block size
            if file_end_loc <= block_size:
                # Do a direct copy
                f.seek(0)
                data = f.read(file_end_loc)
                temp_file.write(data)
                temp_file.close()
            # If the data is larger than the block size
            else:
                # Find number of whole blocks to copy
                num_whole_blocks_copy = floor(file_end_loc / block_size)
                # Find partial block data size
                num_bytes_partial_block_copy = file_end_loc - (num_whole_blocks_copy * block_size)
                # Copy whole blocks
                f.seek(0)
                for block in range(num_whole_blocks_copy):
                    # Read block data (automatically moves position)
                    block_data = f.read(block_size)
                    # Write block to temp file
                    temp_file.write(block_data)
                # Test for any partial block data
                if num_bytes_partial_block_copy > 0:
                    # Read remaining data
                    partial_block_data = f.read(num_bytes_partial_block_copy)
                    # Write remaining data to temp file
                    temp_file.write(partial_block_data)
                # Close temp file
                temp_file.close()
        # Delete original file
        os.remove(filename)
        # Replace original with temporary file
        shutil.move(temp_file.name, filename)
        # Return the new file size
        return(file_end_loc)



class ImgTag:
    def __init__(self, filename, force_case=None, strip=True, no_duplicates=True):
        self.is_open = False
        
        self.tags = None
        self.title = None
        self.description = None
        self.xmpfile = None
        self.xmp = None
        
        if not os.path.isfile(filename):
            raise ValueError("file does not exist: {}".format(filename))
        self.filename = filename
        
        if force_case not in [None, "upper", "lower"]:
            raise ValueError("force_case argument must be either None, 'upper' or 'lower'")
        self.force_case = force_case
        
        if type(strip) != bool:
            raise ValueError("strip argument must be either True or False")
        self.strip = strip
        
        if type(no_duplicates) != bool:
            raise ValueError("no_duplicates argument must be either True or False")
        self.no_duplicates = no_duplicates
        
        self.open()
    
    def __del__(self):
        self.close()
    
    def _force_case(self, input):
        if self.force_case != None:
            if self.force_case == "upper":
                output = [x.upper() for x in input]
            elif self.force_case == "lower":
                output = [x.lower() for x in input]
        else:
            output = input
        
        return output
    
    def _strip(self, input):
        if self.strip:
            output = [x.strip() for x in input]
        else:
            output = input
        
        return output
    
    def _remove_duplicates(self, input):
        if self.no_duplicates:
            output = list(set(input))
        else:
            output = input
        
        return output
    
    def open(self):
        if not self.is_open:
            # Set a memory limit (some .gf files cause libxmp to freak out)
            set_memory_limit(limit_ratio=__DEFAULT_MEMORY_LIMIT_RATIO__)
            # Try to open the file
            try:
                # Open file for updating
                self.xmpfile = libxmp.XMPFiles(file_path=self.filename, open_forupdate=True)

                # Try to read existing XMP
                self.xmp = self.xmpfile.get_xmp()

                # Make new XMP if not exist
                if self.xmp is None:
                    self.xmp = libxmp.core.XMPMeta()
            except KeyError:
                # Unable to open
                raise SystemError("Cannot open file for XMP editing!")
            except libxmp.XMPError:
                # libxmp died
                raise SystemError("Cannot open file for XMP editing!")
            
            self.is_open = True
            
            # Get title
            temp = self.get_title()
            
            # Get description
            temp = self.get_description()
            
            # Get tags
            temp = self.get_tags()
    
    def close(self):
        if self.is_open:
            # Test if can write tags
            if self.xmpfile.can_put_xmp(self.xmp):
                try:
                    # Write tags
                    self.xmpfile.put_xmp(self.xmp)

                    # Close file
                    self.xmpfile.close_file()
                    saved = True
                except libxmp.XMPError:
                    warnings.warn("Could not save metadata in image!")
                    saved = False
            else:
                # Close file
                self.xmpfile.close_file()
                warnings.warn("Could not save metadata in image!")
                saved = False
            
            # Reset memory limit
            set_memory_limit(limit_ratio=None)
            
            self.is_open = False
            
            self.tags = None
            self.title = None
            self.description = None
            self.xmpfile = None
            self.xmp = None
            
            # Sometimes, libxmp saves hundreds of megabytes of zeros at the end
            # This fixes it
            if saved:
                temp = strip_file_blank_space(self.filename)
            
            return saved
    
    def get_tags(self):
        # Open if not opened
        if not self.is_open:
            self.open()
        
        # Get existing tags
        num_tags = self.xmp.count_array_items(libxmp.consts.XMP_NS_DC, "subject")
        tags = [self.xmp.get_array_item(libxmp.consts.XMP_NS_DC, "subject", i).strip().lower() for i in range(1, num_tags+1)]
        
        # Strip
        tags = self._strip(tags)
        
        # Force case
        tags = self._force_case(tags)
        
        # Remove duplicates
        tags = self._remove_duplicates(tags)
        
        self.tags = tags
        return self.tags
    
    def get_title(self):
        self.title = None
        if self.xmp.does_property_exist(libxmp.consts.XMP_NS_DC, "title"):
            self.title = self.xmp.get_array_item(libxmp.consts.XMP_NS_DC, "title", 1)
        return self.title
    
    def get_description(self):
        self.description = None
        if self.xmp.does_property_exist(libxmp.consts.XMP_NS_DC, "description"):
            self.description = self.xmp.get_array_item(libxmp.consts.XMP_NS_DC, "description", 1)
        return self.description
    
    def add_tags(self, tags):
        # Get existing tags (updates self.tags)
        temp = self.get_tags()
        
        # Strip
        tags = self._strip(tags)
        
        # Force case
        tags = self._force_case(tags)
        
        # Append tags
        for tag in tags:
            # Skip duplicates
            if self.no_duplicates:
                if tag in self.tags:
                    continue
            
            # Append
            self.xmp.append_array_item(libxmp.consts.XMP_NS_DC, "subject", tag, {"prop_array_is_ordered":True, "prop_value_is_array":True})
            self.tags.append(tag)
      
    def clear_tags(self):
        self.tags = []
        self.xmp.delete_property(libxmp.consts.XMP_NS_DC, "subject")
    
    def set_tags(self, tags):
        self.clear_tags()
        self.add_tags(tags)
    
    def remove_tags(self, tags):
        # Get existing tags
        final_tags = self.get_tags()
        
        # Strip
        tags = self._strip(tags)
        
        # Force case
        tags = self._force_case(tags)
        
        # Remove tags provided
        final_tags = [x for x in final_tags if x not in tags]
        
        # Set the tags
        self.set_tags(final_tags)
    
    def clear_title(self):
        self.xmp.delete_property(libxmp.consts.XMP_NS_DC, "title")
        self.title = None
    
    def set_title(self, text):
        self.clear_title()
        
        self.xmp.append_array_item(libxmp.consts.XMP_NS_DC, "title", text, {"prop_array_is_alt":True})
        self.title = text
    
    def clear_description(self):
        self.xmp.delete_property(libxmp.consts.XMP_NS_DC, "description")
        self.description = None
    
    def set_description(self, text):
        self.clear_description()
        
        self.xmp.append_array_item(libxmp.consts.XMP_NS_DC, "description", text, {"prop_array_is_alt":True})
        self.description = text
    
    