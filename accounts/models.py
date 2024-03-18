from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
#Not Used ... Use for extra fields
class CustomUserManager(BaseUserManager):
    def create_user(self, userloginname, password=None, **extra_fields):
        if not userloginname:
            raise ValueError('The userloginname field must be set')
        
        user = self.model(userloginname=userloginname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, userloginname, password=None, **extra_fields):
        # Ensure the user has the superuser status and any other necessary attributes
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(userloginname, password, **extra_fields)
    

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(db_column='UserID', primary_key=True, max_length=10)  # Field name made lowercase.
    userdepartmentid = models.CharField(db_column='UserDepartmentID', max_length=10, blank=True, null=True)  # Field name made lowercase.
    employeecode = models.CharField(db_column='EmployeeCode', max_length=10, blank=True, null=True)  # Field name made lowercase.
    username = models.CharField(db_column='UserName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    userloginname = models.CharField(db_column='UserLoginName',unique=True, max_length=100, blank=True, null=True)  # Field name made lowercase.
    password = models.CharField(db_column='UserPassword', max_length=100, blank=True, null=True)  # Field name made lowercase.
    post = models.CharField(db_column='Post', max_length=100, blank=True, null=True)  # Field name made lowercase.
    joining_date = models.CharField(db_column='Joining_Date', max_length=20, blank=True, null=True)  # Field name made lowercase.
    address = models.CharField(db_column='Address', max_length=500, blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=100, blank=True, null=True)  # Field name made lowercase.
    state = models.CharField(db_column='State', max_length=100, blank=True, null=True)  # Field name made lowercase.
    dateofbirth = models.CharField(db_column='DateofBirth', max_length=20, blank=True, null=True)  # Field name made lowercase.
    ph1 = models.CharField(db_column='Ph1', max_length=20, blank=True, null=True)  # Field name made lowercase.
    ph2 = models.CharField(max_length=20, blank=True, null=True)
    fax = models.CharField(db_column='Fax', max_length=20, blank=True, null=True)  # Field name made lowercase.
    email = models.CharField(db_column='Email', max_length=100)  # Field name made lowercase.
    referreddby = models.CharField(db_column='ReferreddBy', max_length=100, blank=True, null=True)  # Field name made lowercase.
    isactive = models.IntegerField(db_column='IsActive', blank=True, null=True)  # Field name made lowercase.
    auid = models.CharField(db_column='AUID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    adatetime = models.DateTimeField(db_column='ADateTime', default=timezone.now)  # Field name made lowercase.
    muid = models.CharField(db_column='MUID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    mdatetime = models.CharField(db_column='MDateTime', max_length=50)  # Field name made lowercase.
    companyid = models.IntegerField(db_column='CompanyID', blank=True, null=True)  # Field name made lowercase.
    mgtlevels = models.IntegerField(db_column='MgtLevels', blank=True, null=True)  # Field name made lowercase.
    icompanyid = models.CharField(db_column='Icompanyid', max_length=10)  # Field name made lowercase.
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

    class Meta:
        managed = False
        db_table = 'usermaster'
        unique_together = (('id', 'email'),)
    objects = CustomUserManager()

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
        return (timezone.now() - self.created_at).total_seconds() > 180

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
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # icon = models.ImageField(upload_to='app_icons/', blank=True, null=True) #if you want to use icons for the specific module
    permissions = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    ordering = models.IntegerField(default=0)
    visibility_condition = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name

