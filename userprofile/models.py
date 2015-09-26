from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Company(models.Model):
	full_name = models.CharField(_('Company name'), max_length=100)
	short_name = models.CharField(_('Company short name'), max_length=20)
	address = models.TextField(_('Company address'), blank=True)
	phone = models.CharField(_('Phone No'), max_length=30, blank=True)
	license_no = models.CharField(_('License No.'), max_length=30, blank=True)
	representative = models.CharField(_('Representative'), max_length=250, blank=True)

	def __unicode__(self):
		return self.full_name

	@classmethod
	def add_new_company(cls, dictionary):
		if dict:
			company = cls.objects.create(**dictionary)
			return company

	@classmethod
	def get_company_with_company_name(cls, company_name):
		try:
			company = cls.objects.get(full_name=company_name)
		except cls.DoesNotExist:
			company = None

		return company

	@classmethod
	def get_company_with_id(cls, pk):
		company = cls.objects.get(pk=pk)
		if company:
			return company
		return None

	@classmethod
	def get_or_create_company(cls, dictionary):
		company_data = cls.get_company_with_company_name(dictionary["full_name"])
		if company_data is None:
			company_data = cls.add_new_company(dictionary)
		return company_data

	@classmethod
	def update_company_info(cls, dictionary):
		company = cls.get_company_with_id(dictionary["id"])
		if company:
			company.full_name = dictionary["full_name"]
			company.short_name = dictionary["short_name"]
			company.address = dictionary["address"]
			company.phone = dictionary["phone"]
			company.license_no = dictionary["license_no"]
			company.representative = dictionary["representative"]
			company.save()


class UserProfile(models.Model):
	user = models.OneToOneField(User, related_name="user_profile")
	company = models.ForeignKey("Company", null=True, blank=True)
	is_customer_superadmin = models.IntegerField(default=0)
	permission = models.ManyToManyField("transaction.Form", null=True, blank=True)

	def __unicode__(self):
		return self.user.username

	@classmethod
	def add_new_user(cls, dictionary):
		if dict:
			user = User.objects.create_user(
				username=dictionary["username"],
				email=dictionary["email"],
				password=dictionary["password"],
				first_name=dictionary["first_name"],
				last_name=dictionary["last_name"],
			)
			user.is_staff = dictionary["is_staff"]
			user.save()
			return user

	@classmethod
	def add_user_profile(cls, user, **extra_field):
		cls.objects.create(user=user, **extra_field)

	@classmethod
	def get_user_info_by_username(cls, username):
		return User.objects.get(username=username)

	@classmethod
	def get_user_info_by_id(cls, id):
		return User.objects.get(id=id)

	@classmethod
	def check_user_exist(cls, username):
		if User.objects.filter(username=username):
			return True
		return False

	@classmethod
	def check_email_exist(cls, email_address):
		if User.objects.filter(email=email_address):
			return True
		return False

	@classmethod
	def update_user(cls, dictionary):
		user = cls.get_user_info_by_username(dictionary["old_username"])
		user.username = dictionary["new_username"]
		user.email = dictionary["email"]
		user.first_name = dictionary["first_name"]
		user.last_name = dictionary["last_name"]
		if dictionary["password"] is not None:
			user.set_password(dictionary["password"])
		user.save()
		return user


# def create_user_profile(sender, instance, created, **kwargs):
# 	if created:
# 		UserProfile.objects.create(user=instance)
#
# post_save.connect(create_user_profile, sender=User)
