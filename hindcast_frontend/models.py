from django.db import models


class HindcastEvaluation(models.Model):

    path_map = models.CharField(max_length=255, null=True, blank=True)
    path_fieldmean = models.CharField(max_length=255, null=True, blank=True)
    score = models.CharField(max_length=50)
    eva_time_start = models.IntegerField()
    eva_time_end = models.IntegerField()
    region = models.CharField(max_length=255)
    time_frequency = models.CharField(max_length=255)
    variable = models.CharField(max_length=255)
    reference = models.CharField(max_length=255)
    hindcast_set = models.CharField(max_length=255)

    path_structure = 'hindcast_set/reference/variable/time_frequency/region/eva_type/'.split('/')


    def populate_from_path(self, path):
        facet_list = path.split('/')

        self.path = path

        for i in xrange(-1, -1 - len(self.path_structure), -1):
            setattr(self, self.path_structure[i], facet_list[i])
        fn = facet_list.pop(-1)
        fn_list = fn.split('_')
        self.score = fn_list[1]
        time_list = fn_list[2].split('-')
        self.eva_time_start = time_list[0]
        self.eva_time_end = time_list[1]