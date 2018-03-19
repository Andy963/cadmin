from django.db import models

# Create your models here.

class User(models.Model):
    name = models.CharField(verbose_name='用户名',max_length=20)
    age = models.IntegerField(verbose_name='年龄')

    def __str__(self):
        return self.name

class Book(models.Model):
    name = models.CharField(verbose_name='书名', max_length=30)
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='价格')

    def __str__(self):
        return self.name

class Role(models.Model):
    title = models.CharField(verbose_name='Role title', max_length=32)

    def __str__(self):
        return self.title

class Department(models.Model):
    caption = models.CharField(verbose_name='Department name', max_length=20)

    def __str__(self):
        return self.caption

class UserInfo(models.Model):
    name = models.CharField(verbose_name='User name', max_length=32)
    email = models.EmailField(verbose_name='Email', max_length=32, default='1')
    pwd = models.CharField(verbose_name='password', max_length=32, default='1')
    user_type = models.ForeignKey(to="UserType", default=1)
    GENDER_CHOICE = {
        (1, 'male'),
        (2, 'female'),
    }
    gender = models.IntegerField(verbose_name='gender', choices=GENDER_CHOICE,default=1)
    depart = models.ForeignKey(verbose_name='department', to=Department, default=1)
    role = models.ManyToManyField(verbose_name='Role', to=Role)


    def __str__(self):
        return self.name

class UserType(models.Model):
    type = models.CharField(verbose_name='type', max_length=32,default='class1')

    def __str__(self):
        return self.type

class Host(models.Model):
    hostname = models.CharField(verbose_name='主机名',max_length=32)
    ip = models.GenericIPAddressField(verbose_name="IP",protocol='ipv4')
    port = models.IntegerField(verbose_name='端口')

    def __str__(self):
        return self.hostname