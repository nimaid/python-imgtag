import libxmp
import warnings

class ImgTag:
    def __init__(self, filename, force_case=None, strip=True, no_duplicates=True):
        self.filename = filename
        self.is_open = False
        
        self.tags = None
        
        # Add valueerrors
        self.force_case = force_case
        self.strip = strip
        self.no_duplicates = no_duplicates
        
        self.open()
        temp = self.get_tags()
    
    def __del__(self):
        self.close()
    
    def open(self):
        if not self.is_open:
            # Open file for updating
            self.xmpfile = libxmp.XMPFiles(file_path=self.filename, open_forupdate=True)
            
            # Try to read existing XMP
            self.xmp = self.xmpfile.get_xmp()
            
            # Make new XMP if not exist
            if self.xmp is None:
                self.xmp = libxmp.core.XMPMeta()
            
            self.is_open = True

    def close(self):
        if self.is_open:
            # Test if can write tags
            if self.xmpfile.can_put_xmp(self.xmp):
                # Write tags
                self.xmpfile.put_xmp(self.xmp)
                
                # Close file
                self.xmpfile.close_file()
                saved = True
            else:
                # Close file
                xmpfile.close_file()
                warnings.warn("Could not save tags in image!")
                saved = False
            
            self.is_open = False
            return saved
    
    def get_tags(self):
        # Open if not opened
        if not self.is_open:
            self.open()
        
        # Get existing tags
        num_tags = self.xmp.count_array_items(libxmp.consts.XMP_NS_DC, "subject")
        tags = [self.xmp.get_array_item(libxmp.consts.XMP_NS_DC, "subject", i).strip().lower() for i in range(1, num_tags+1)]
        
        # Strip
        if self.strip == True:
             tags = [x.strip() for x in tags]
        elif self.strip != False:
            raise ValueError("strip argument must be either True or False")
        
        # Force case
        if self.force_case != None:
            if self.force_case.lower() == "upper":
                tags = [x.upper() for x in tags]
            elif self.force_case.lower() == "lower":
                tags = [x.lower() for x in tags]
            else:
                raise ValueError("force_case argument must be either None, 'upper' or 'lower'")
        
        # Remove duplicates
        if self.no_duplicates == True:
            tags = list(set(tags))
        elif self.no_duplicates != False:
            raise ValueError("no_duplicates argument must be either True or False")
        
        self.tags = tags
        return self.tags
    
    def add_tags(self, tags):
        # Get existing tags (updates self.tags)
        temp = self.get_tags()
        
        # Strip
        if self.strip == True:
            tags = [x.strip() for x in tags]
        
        # Force case
        if self.force_case != None:
            if self.force_case.lower() == "upper":
                tags = [x.upper() for x in tags]
            elif self.force_case.lower() == "lower":
                tags = [x.lower() for x in tags]
        
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
        self.xmp = self.xmpfile.get_xmp()