from django.contrib.auth.base_user import BaseUserManager


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password, user_type, name=None, user_image=None, address=None,
                    phone=None, ):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.user_type = user_type
        user.user_image = user_image
        user.name = name
        user.phone = phone
        user.address = address
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email,
            password=password,
            user_type=None,
        )
        user.is_staff = True
        user.user_type = 2
        user.save(using=self._db)
        return user
