import libxmp
import warnings
import os

class ImgTag:
    def __init__(self, filename, force_case=None, strip=True, no_duplicates=True):
        self.is_open = False
        
        self.tags = None
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
            # Open file for updating
            self.xmpfile = libxmp.XMPFiles(file_path=self.filename, open_forupdate=True)
            
            # Try to read existing XMP
            self.xmp = self.xmpfile.get_xmp()
            
            # Make new XMP if not exist
            if self.xmp is None:
                self.xmp = libxmp.core.XMPMeta()
            
            self.is_open = True
            
            # Get description
            temp = self.get_description()
            
            # Get tags
            temp = self.get_tags()
    
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
                self.xmpfile.close_file()
                warnings.warn("Could not save tags in image!")
                saved = False
            
            self.is_open = False
            
            self.tags = None
            self.description = None
            self.xmpfile = None
            self.xmp = None
            
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
    
    
    def clear_description(self):
        self.xmp.delete_property(libxmp.consts.XMP_NS_DC, "description")
        self.description = None
    
    def set_description(self, text):
        self.clear_description()
        
        self.xmp.append_array_item(libxmp.consts.XMP_NS_DC, "description", text, {"prop_array_is_alt":True})
        self.description = text
    
    