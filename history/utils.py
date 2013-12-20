import os

from evaluation_system.misc import utils
from models import History
from django_evlauation import settings
from contrib.comments.views.moderation import delete


def pygtailwrapper(id, restart = False):
    """
    This function return the pygtail result for the slurm file
    specified in the history
    """
    from pygtail import Pygtail

    history_object = History.objects.get(id=id)
    full_file_name = history_object.slurm_output
        
    # path for the offset file
    utils.supermakedirs(settings.TAIL_TMP_DIR, 0777)
    
    file_name = os.path.basename(full_file_name)
    
    # offset file
    offset_file_name = os.path.join(settings.TAIL_TMP_DIR, file_name)
    offset_file_name = offset_file_name + '.offset'
    
    if restart and os.path.isfile(offset_file_name):
        os.remove(offset_file_name)
    
    
    return Pygtail(full_file_name, offset_file=offset_file_name)    

class FileDict(dict):
    """
    This class ease the browsing through a bunch of files in several directories.
    """
    def _add_file(self, split_path, value):
        if len(split_path)==1:
            self[split_path[0]] = value
        else:
            fdict = self.get(split_path[0], None)
            
            if not isinstance(fdict, FileDict):
                fdict = FileDict()
                     
            self[split_path[0]] = fdict._add_file(split_path[1:], value)
        return self
    def add_file(self, str_to_file, value=None):
        """
        Adds a file to the directory structure and assigns a value to it.
        :type str_to_file: string
        :param str_to_file: The path of a file
        :type value: arbitrary
        :param value: A value which can be assigned to the file (the path is a useful choice)
        """
        split_path = []
        # create a list of directories      
        while str_to_file:
            (str_to_file, head) = os.path.split(str_to_file)              
            split_path.append(head)
        self._add_file(split_path[::-1], value)
        
    def compressed_copy(self):
        """
        Returns a copy where single sub-directories are joined to their parents 
        """
        fdcopy = FileDict()
        
        for k in self.keys():
            fdict = self[k]
            if isinstance(fdict, FileDict):
                fdict = fdict.compressed_copy()
                
                if len(fdict) == 1:
                    k2, v2 = fdict.popitem()
                    # create a compressed key
                    newkey = os.path.join(k, k2)
                    fdcopy[newkey] = v2
                else:
                    fdcopy[k] = fdict
            else:
                fdcopy[k] = fdict
        return fdcopy
    
    def get_list(self):
        """
        Returns a nested list of the tree object. 
        """
        ret =[]
        
        for item in self.items():
            ret.append(item[0])
            if isinstance(item[1], FileDict):
                ret.append(item[1].get_list())
        
        return ret
        
