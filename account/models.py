from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_brith = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/', blank=False, default='users/user_logo_default.png')
    
    def __str__(self):
        return 'Profile for user {}'.format(self.user.username)

class Contact(models.Model):
    user_from = models.ForeignKey('auth.User', related_name='rel_from_set', on_delete=models.CASCADE)
    user_to = models.ForeignKey('auth.User', related_name='rel_to_set', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return '{} follows {}'.format(self.user_from, self.user_to)

# Adaugarea dinamica a campului following in tabelul User din Django
User.add_to_class('following', models.ManyToManyField('self', through=Contact, related_name='followers', symmetrical=False))

