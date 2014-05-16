from django.db import models
from django.contrib.auth.models import User
from plugins.models import Version

import json

class History(models.Model):
    """
    The class belongs to a table containing all processes, which were started with analyze.
    """
    class Meta:
        """
        Set the user's permissions
        """
        permissions = (
                       ('history_submit_job', 'Can submit a job'),
                       ('history_cancel_job', 'Can cancel a job'),
                       ('browse_full_data', 'Can search all data'),
                      )

        

    class processStatus:
        """
        The allowed statuses
        finished           - the process finished and produced output files
        finished_no_output - the process finished, but no output files were created
        scheduled          - the job was send to slurm
        running            - the job is executed
        broken             - an exception occurred
        not_scheduled      - an error occurred during scheduling
        """
        finished, finished_no_output, broken, running, scheduled, not_scheduled = range(6)
        
    class Flag:
        """
        The possible flags are:
        public  - the data is accessible for everyone
        shared  - the data is can be only accessed by certain users
        private - the data is private
        deleted - the data set will be hidden
        """
        public, shared, private, deleted = range(4)
        guest = 8
        free = 9
        
    STATUS_CHOICES = ((processStatus.finished, 'finished'),
                      (processStatus.finished_no_output, 'finished (no output)'),
                      (processStatus.broken, 'broken'),
                      (processStatus.running, 'running'),
                      (processStatus.scheduled, 'scheduled'),
                      (processStatus.not_scheduled, 'not scheduled'),)
    
    FLAG_CHOICES = ((Flag.public, 'public'),
                    (Flag.shared, 'shared'),
                    (Flag.private, 'private'),
                    (Flag.deleted, 'deleted'),
                    (Flag.guest, 'users and guest'),
                    (Flag.free, 'no login required'),
                   )

    #: Date and time when the process were scheduled
    timestamp       = models.DateTimeField()
    #: Name of the tool
    tool            = models.CharField(max_length=50)
    #: Version of the tool
    version         = models.CharField(max_length=10)
    #: User ID
    version_details = models.ForeignKey(Version, default=0)
    #: The configuration this can be quiet lengthy
    configuration   = models.TextField()
    #: Output file generated by SLURM 
    slurm_output    = models.TextField()
    #: User ID
    uid             = models.ForeignKey(User, to_field='username', db_column='uid')#models.CharField(max_length=20)
    #: Status (scheduled, running, finished, cancelled)
    status          = models.IntegerField(max_length=1, choices=STATUS_CHOICES)
    #: Flag (deleted, private, shared, public)
    flag            = models.IntegerField(max_length=1, choices=FLAG_CHOICES, default=Flag.public)

    
    def __init__(self, *args, **kwargs):
        """
        Creates a dictionary for projectStatus
        """
        self.status_dict = dict()
        public_props = (name for name in dir(self.processStatus) if not name.startswith('_'))
        for name in public_props:
            self.status_dict[getattr(self.processStatus,name)] = name
        
        super(History, self).__init__(*args, **kwargs)
        
    def slurmId(self):
        #import string
        #alle = string.maketrans('','')
        #nodigs = alle.translate(alle, string.digits)
        #slurm_file = str(self.slurm_output)
        #slurm_file = '12312aasdas'
        return self.slurm_output[-8:-4]    
        

    def config_dict(self):
        """
        Converts the configuration to a dictionary
        """
        return json.loads(self.configuration)

    def status_name(self):
        """
        Returns status as string
        """    
        return self.status_dict[self.status]

        
        
            

class Result(models.Model):
    """
    This class belongs to a table storing results.
    The output files of process will be recorded here.
    """

    class Filetype:
        """
        Different IDs of file types
        data      - ascii or binary data to download
        plot      - a file which can be converted to a picture
        preview   - a local preview picture (copied or converted) 
        """
        data, plot, preview = range(3)

    FILE_TYPE_CHOICES = ((Filetype.data, 'data'),
                         (Filetype.plot, 'plot'),
                         (Filetype.preview, 'preview'),)       

    
    #: history id
    history_id      = models.ForeignKey(History)
    #: path to the output file
    output_file     = models.TextField()
    #: path to preview file
    preview_file    = models.TextField(default='')
    #: specification of a file type 
    file_type       = models.IntegerField(max_length=2, choices=FILE_TYPE_CHOICES)
    
    class Meta:
        """
        Set the user's permissions
        """
        permissions = (
                       ('results_view_others', 'Can view results from other users'),
                      )


    def fileExtension(self):
        """
        Returns the file extension of the result file
        """
        from os import path
        return path.splitext(self.output_file)[1]
    
    # some not yet implemented ideas
    ##: Allows a logical clustering of results
    # group           = models.IntegerField(max_length=2)
    ##: Defines an order for each group
    # group_order     = models.IntegerField(max_length=2)

class ResultTag(models.Model):
    """
    This class belongs to a table storing results.
    The output files of process will be recorded here.
    """

    class flagType:
        caption = range(1)    
    
    
    TYPE_CHOICES = ((flagType.caption, 'Caption'),)
    
    #: result id
    result_id      = models.ForeignKey(Result)
    #: specification of a file type 
    type           = models.IntegerField(max_length=2, choices = TYPE_CHOICES)
    #: path to the output file
    text           = models.TextField()
    

