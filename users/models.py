from django.db import models
from django.contrib.auth.models import User
from PIL import Image


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg',
                              upload_to='profile_pics')
    patronym = models.CharField(max_length=100, default='')
    is_lecturer = models.BooleanField(default=False)
    interests = models.TextField('Укажите свои интересы через запятую (например: машинное обучение, кибербезопасность)', default='')

    def __str__(self):
        return f'{self.user.username} Profile'

    def interests_as_list(self):
        return self.interests.split(',')

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def delete(self, *args, **kwargs):
        self.image.delete()
        super().delete(*args, **kwargs)

