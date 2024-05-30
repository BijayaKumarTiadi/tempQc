from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password
from imagekit.models import ProcessedImageField
from django.utils.html import format_html
# Create your models here.


#for change log 
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
#Not Used ... Use for extra fields
class CustomUserManager(BaseUserManager):
    def create_user(self, userloginname, password=None, **extra_fields):
        if not userloginname:
            raise ValueError('The userloginname field must be set')
        
        user = self.model(userloginname=userloginname, **extra_fields)
        if password:
            user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, userloginname, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(userloginname, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(db_column='UserID', primary_key=True, max_length=10)  
    userdepartmentid = models.CharField(db_column='UserDepartmentID', max_length=10, blank=True, null=True)  
    employeecode = models.CharField(db_column='EmployeeCode', max_length=10, blank=True, null=True)  
    username = models.CharField(db_column='UserName', max_length=100, blank=True, null=True)  
    userloginname = models.CharField(db_column='UserLoginName',unique=True, max_length=100, blank=True, null=True)  
    password = models.CharField(db_column='UserPassword', max_length=100, blank=True, null=True)  
    post = models.CharField(db_column='Post', max_length=100, blank=True, null=True)  
    joining_date = models.CharField(db_column='Joining_Date', max_length=20, blank=True, null=True)  
    address = models.CharField(db_column='Address', max_length=500, blank=True, null=True)  
    city = models.CharField(db_column='City', max_length=100, blank=True, null=True)  
    state = models.CharField(db_column='State', max_length=100, blank=True, null=True)  
    dateofbirth = models.CharField(db_column='DateofBirth', max_length=20, blank=True, null=True)  
    ph1 = models.CharField(db_column='Ph1', max_length=20, blank=True, null=True)  
    ph2 = models.CharField(max_length=20, blank=True, null=True)
    fax = models.CharField(db_column='Fax', max_length=20, blank=True, null=True)  
    email = models.CharField(db_column='Email', max_length=100)  
    referreddby = models.CharField(db_column='ReferreddBy', max_length=100, blank=True, null=True)  
    isactive = models.IntegerField(db_column='IsActive', blank=True, null=True)  
    auid = models.CharField(db_column='AUID', max_length=50, blank=True, null=True)  
    adatetime = models.DateTimeField(db_column='ADateTime', default=timezone.now)  
    muid = models.CharField(db_column='MUID', max_length=50, blank=True, null=True)  
    mdatetime = models.CharField(db_column='MDateTime', max_length=50)  
    companyid = models.IntegerField(db_column='CompanyID', blank=True, null=True)  
    mgtlevels = models.IntegerField(db_column='MgtLevels', blank=True, null=True)  
    icompanyid = models.CharField(db_column='Icompanyid', max_length=10)  
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField(blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    is_staff = models.IntegerField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    date_joined = models.DateTimeField(blank=True, null=True)


    USERNAME_FIELD = 'userloginname'

    def __str__(self):
        return self.userloginname
    def get_id(self):
        """
        This is used for the JWT which is required only model.id in our case we have only userid
        """
        return str(self.id)
    objects = CustomUserManager()
    class Meta:
        managed = False
        db_table = 'usermaster'
        unique_together = (('id', 'email'),)

    def save(self, *args, **kwargs):
        # Hash the password if it's set and the user is being created
        if self.password:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

class OTP(models.Model):
    objects = None
    DoesNotExist = None
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    expired = models.BooleanField(default=False)
    resend_attempts = models.PositiveIntegerField(default=0)

    def is_expired(self):
        # OTP expires in 3 minutes
        return (timezone.now() - self.created_at).total_seconds() > 18000000000

    def can_resend(self):
        # Allow a maximum of 2 resend attempts
        return self.resend_attempts < 2

    def resend_otp(self):
        if self.can_resend() and not self.expired:
            self.resend_attempts += 1
            self.save()
            return True
        return False

    def __str__(self):
        return f'OTP for {self.email}'

class AppModule(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    url = models.SlugField(max_length=100, unique=True,blank=True)
    description = models.TextField(blank=True)
    image = ProcessedImageField(upload_to='module_icons/',format='JPEG',options={'quality': 40}, null=True)#if you want to use icons for the specific module
    is_active = models.BooleanField(default=True)
    sort = models.IntegerField(default=0)
    def __str__(self):
        return self.name
    class Meta:
        ordering=['-sort']
    # def image_tag(self):
    #     return format_html(
    #         '<img src="/media/{}" style="width:40px;height:40px;border-radius:50%;"  />'.format(self.image))


#you can use this to log all the models 
class ChangeLog(models.Model):
    ACTION_FLAG_CHOICES = (
        (ADDITION, 'Addition'),
        (CHANGE, 'Change'),
        (DELETION, 'Deletion'),
    )

    action_time = models.DateTimeField(auto_now_add=True)
    object_id = models.TextField(null=True, blank=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField(choices=ACTION_FLAG_CHOICES)
    change_message = models.TextField()
    content_type = models.ForeignKey(ContentType, blank=True, null=True, related_name='change_logs', on_delete=models.SET_NULL)
    user = models.ForeignKey(CustomUser, blank=True, null=True, related_name='change_logs', on_delete=models.SET_NULL)

    class Meta:
        ordering = ('-action_time',)

    @property
    def action_name(self):
        return self.get_action_flag_display()

    def __str__(self):
        return f'{self.action_time} - {self.object_repr} - {self.get_action_flag_display()} by {self.user.username}'
