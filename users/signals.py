from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User # sender
from django.dispatch import receiver
from .models import Profile
from .views import variables

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if len(variables) == 0:
            Profile.objects.create(user=instance)

        else:
            if variables[1] == 'lecturer':
                Profile.objects.create(user=instance, patronym=variables[0], is_lecturer=True)

            else:
                Profile.objects.create(user=instance, patronym=variables[0])

@receiver(pre_save, sender=Profile)
def delete_old_image(sender, instance, *args, **kwargs):
    try:
        old_img = Profile.objects.get(user=instance.user).image.path
        try:
            new_img = instance.image.path
        except:
            new_img = None
        if new_img != old_img:
            import os
            if os.path.exists(old_img):
                if '\\media\\default.jpg' not in old_img:
                    os.remove(old_img)
    except:
        pass