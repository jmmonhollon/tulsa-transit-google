from datetime import datetime
import os.path

from django.conf import settings
from django.db import models

class MediaFile(models.Model):
    '''An uploaded or generated file'''
    TYPE_CHOICES = (
        #(u'I', 'Import .zip'),
        (u'F', 'GTFS Feed .zip'),
    )
    
    TYPE_LOCAL_FORMATS = dict(
        #I='import.%s.zip',
        F='feed.%s.zip',
    )
    
    name = models.CharField(max_length=30)
    added_at = models.DateField()
    local_name = models.CharField(max_length=30)
    file_type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    source = models.CharField(max_length=30)
    
    def save_upload(self, request_file, file_type='I'):
        if not self.added_at:
            self.added_at = datetime.now()
        if not self.file_type:
            self.file_type = file_type
        if not self.local_name:
            fmt = self.TYPE_LOCAL_FORMATS[self.file_type]
            self.local_name = fmt % self.added_at.strftime('%Y%m%d.%H%M')
        if not self.source:
            self.source = 'Uploaded'
        local_path = os.path.join(settings.MEDIA_ROOT, self.local_name)
        with open(local_path, 'wb+') as destination:
            for chunk in request_file.chunks():
                destination.write(chunk)
        self.save()

