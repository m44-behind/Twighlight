from django.db import models


# Create your models here.
class Streamer(models.Model):
    sid = models.IntegerField()
    login = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    profile_image_url = models.CharField(max_length=300)

    def __str__(self):
        return f'{self.sid}'


class Video(models.Model):
    vid = models.IntegerField()
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=False)
    duration = models.CharField(max_length=30)
    url = models.CharField(max_length=40)
    thumb_nail_url = models.CharField(max_length=300)
    streamer_id = models.ForeignKey(Streamer, on_delete=models.CASCADE)

    def __str__(self):
        #return f'{self.title}.{self.created_at}.{self.duration}.{self.url}.{self.thumb_nail_url}.{self.streamer_id}'
        return f'{self.title}{self.streamer_id}'


class Data(models.Model):
    data_time = models.IntegerField()
    video_id = models.ForeignKey(Video, on_delete=models.CASCADE)
    streamer_id = models.ForeignKey(Streamer, on_delete=models.CASCADE)

    def __str__(self):
        # return f'{self.title}.{self.created_at}.{self.duration}.{self.url}.{self.thumb_nail_url}.{self.streamer_id}'
        return f'{self.data_time}{self.video_id}{self.streamer_id}'


