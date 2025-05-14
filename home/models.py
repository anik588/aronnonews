import mimetypes
from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.utils.timesince import timesince


class BaseModel(models.Model):
    class Meta:
        abstract = True

    def clean(self):
        pass

    def save(self, *args, **kwargs):
        # Any shared logic for all models can go here
        super().save(*args, **kwargs)


from django.db import models

class EPaper(models.Model):
    title = models.CharField(max_length=255)
    pdf_file = models.FileField(upload_to='epapers/', default="")
    thumbnail = models.ImageField(upload_to='epaper_thumbnails/')  # Separate thumbnail field
    upload_time = models.DateTimeField(auto_now_add=False)
    is_active = models.BooleanField(default=False, verbose_name='সক্রিয় (Active)')

    def __str__(self):
        return self.title


# E paper MODEL End


# Define the choices for advertisement categories

from django.db import models
from django.utils import timezone


class Ad(models.Model):
    # Define the choices for ad categories
    AD_POSITION_CHOICES = [
        ('top_logo', 'Top Logo'),
        ('front_news_one', 'Homepage Highlighted Ads'),


        ('front_news_three', 'Selected News Ads One'),
        ('front_news_four', 'Selected News Ads Two'),

        ('section_one', 'Frontpage Section One'),
        ('section_two', 'Frontpage Section Two'),
        ('section_three', 'Frontpage Section Three'),
        ('section_four', 'Frontpage Section Four'),
        ('section_five', 'Frontpage Section Five'),
        ('section_six', 'Frontpage Section Six'),
        ('highlight_category_section_one', 'Between Frontpage Category Ads One'),
        ('highlight_category_section_two', 'Between Frontpage Category Ads Two'),

        ('news_details', 'News Details'),
        ('news_details_side_ads_one', 'News Details Side Ads One'),
        ('news_details_side_ads_two', 'News Details Side Ads Two'),
        ('section_category_ad', 'Section & Category Pages'),

        ('section_page_ads_one', 'Section page Side Ads One'),
        ('section_page_ads_two', 'Section page Side Ads Two'),
    ]

    category = models.CharField(max_length=50, choices=AD_POSITION_CHOICES, verbose_name='ক্যাটেগরি (Category)')
    image = models.FileField(upload_to='ads/', verbose_name='মিডিয়া (Media)')  # Upload media (image, video, gif)
    link = models.URLField(max_length=255, blank=True, null=True, verbose_name='লিংক (Link)')  # Link for the ad
    alt_text = models.CharField(max_length=255, blank=True, null=True,
                                verbose_name='বিকল্প টেক্সট (Alt Text)')  # Alt text for accessibility
    start_date = models.DateTimeField(
        verbose_name='শুরু করার তারিখ (Start Date)')  # When the ad should start displaying
    end_date = models.DateTimeField(verbose_name='শেষ করার তারিখ (End Date)')  # When the ad should stop displaying
    is_active = models.BooleanField(default=False, verbose_name='সক্রিয় (Active)')  # Toggle for active/inactive ads

    @property
    def media_type(self):
        # Check if the image field is not None
        if self.image:
            mime_type, _ = mimetypes.guess_type(self.image.name)  # Ensure you use the correct field name

            # Debugging output
            print(f"File name: {self.image.name}, MIME type: {mime_type}")

            if mime_type:
                if mime_type.startswith('image'):
                    return 'image'
                elif mime_type.startswith('video'):
                    return 'video'
                elif mime_type.startswith('image/gif'):
                    return 'gif'

        return 'unknown'  # Return unknown if the type is not recognized

    def __str__(self):
        return f"{self.get_category_display()} Ad"

    class Meta:
        ordering = ['category', 'start_date']

    def is_currently_active(self):
        """Check if the ad is currently active based on start and end dates."""
        now = timezone.now()
        return self.is_active and (self.start_date <= now <= self.end_date)

    def save(self, *args, **kwargs):
        # Ensure timezone-aware datetimes
        if self.start_date and timezone.is_naive(self.start_date):
            self.start_date = timezone.make_aware(self.start_date)
        if self.end_date and timezone.is_naive(self.end_date):
            self.end_date = timezone.make_aware(self.end_date)

        # Call the original save method
        super().save(*args, **kwargs)


def get_active_ads(category):
    """
    Utility function to get active ads for a specific category or for 'section_category_details'.
    Filters ads based on the provided category and checks for active status and date range.
    """
    now = timezone.now()  # Use timezone-aware current datetime

    if category == 'section_category_details':
        return Ad.objects.filter(
            category='section_category_details',
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        )

    # For all other categories
    return Ad.objects.filter(
        category=category,
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    )


from django.db import models


class Category(models.Model):
    name_en = models.CharField(max_length=100, unique=True, default='',
                               verbose_name="বিভাগের নাম (Category Name in English)")
    name_bn = models.CharField(max_length=100, unique=True, default='',
                               verbose_name="বিভাগের বাংলা নাম (Category Name in Bangla)")
    show_in_frontpage = models.BooleanField(default=True, verbose_name="ফ্রন্ট পেজে দেখান (Show in Front Page)")

    def __str__(self):
        return f"{self.name_en} / {self.name_bn}"



from django.core.exceptions import ValidationError
from django.db import models

class Section(models.Model):
    name_en = models.CharField(max_length=100, unique=True, default='',
                               verbose_name="সেকশনের নাম (Section Name in English)")
    name_bn = models.CharField(max_length=100, unique=True, default='',
                               verbose_name="সেকশনের বাংলা নাম (Section Name in Bangla)")
    categories = models.ManyToManyField(Category, blank=True, related_name='sections',
                                        verbose_name="বিভাগসমূহ (Categories)")

    def __str__(self):
        return f"{self.name_en} / {self.name_bn}"

from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.utils.timesince import timesince


class NewsList(models.Model):
    # First set of title, description, image, and caption
    reporter = models.TextField(verbose_name='প্রতিবেদক (Reporter)', default='', blank=True, null=True)
    red_tag = models.TextField(verbose_name='লাল শিরোনাম (Red Tag)', default='', blank=True, null=True)
    title = models.TextField(verbose_name='শিরোনাম ১ (Title 1)')
    description = models.TextField(verbose_name='বর্ণনা ১ (Description 1)')
    image = models.ImageField(upload_to='news_images/', blank=True, null=True, verbose_name='ছবি ১ (Image 1)',
                              default='img/logo.png')
    image_caption = models.CharField(max_length=255, blank=True, null=True,
                                     verbose_name='ছবির ক্যাপশন ১ (Image Caption 1)')
    link = models.URLField(blank=True, null=True, verbose_name='লিংক ১ (Link 1)')
    link_caption1 = models.CharField(max_length=255, blank=True, null=True,
                                     verbose_name='লিংক ক্যাপশন ১ (Link Caption 1)')

    # Second set of title, description, image, and caption
    title2 = models.TextField(verbose_name='শিরোনাম ২ (Title 2)', blank=True, null=True)
    description2 = models.TextField(verbose_name='বর্ণনা ২ (Description 2)', blank=True, null=True)
    image2 = models.ImageField(upload_to='news_images/', blank=True, null=True, verbose_name='ছবি ২ (Image 2)',
                               default='img/logo.png')
    image_caption2 = models.CharField(max_length=255, blank=True, null=True,
                                      verbose_name='ছবির ক্যাপশন ২ (Image Caption 2)')
    link2 = models.URLField(blank=True, null=True, verbose_name='লিংক ২ (Link 2)')
    link_caption2 = models.CharField(max_length=255, blank=True, null=True,
                                     verbose_name='লিংক ক্যাপশন ২ (Link Caption 2)')

    # Third set of title, description, image, and caption
    title3 = models.TextField(verbose_name='শিরোনাম ৩ (Title 3)', blank=True, null=True)
    description3 = models.TextField(verbose_name='বর্ণনা ৩ (Description 3)', blank=True, null=True)
    image3 = models.ImageField(upload_to='news_images/', blank=True, null=True, verbose_name='ছবি ৩ (Image 3)',
                               default='img/logo.png')
    image_caption3 = models.CharField(max_length=255, blank=True, null=True,
                                      verbose_name='ছবির ক্যাপশন ৩ (Image Caption 3)')
    link3 = models.URLField(blank=True, null=True, verbose_name='লিংক ৩ (Link 3)')
    link_caption3 = models.CharField(max_length=255, blank=True, null=True,
                                     verbose_name='লিংক ক্যাপশন ৩ (Link Caption 3)')

    # Foreign key relationships for category and section
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, verbose_name='বিভাগ (Category)')
    section = models.ForeignKey('Section', on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name='সেকশন (Section)', related_name='news_items')

    # Additional fields for status, counts, etc.
    views_count = models.PositiveIntegerField(default=0)
    verified = models.BooleanField(default=False, verbose_name='যাচাইকৃত (Verified)')
    breaking_news = models.BooleanField(default=False, verbose_name='ব্রেকিং নিউজ (Breaking News)')
    section_highlighted = models.BooleanField(default=False, verbose_name='Section Highlighted')
    for_you = models.BooleanField(default=False, verbose_name='আপনার জন্য (For You)')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='তৈরি হওয়ার তারিখ (Created At)')
    highlighted = models.BooleanField(default=False, verbose_name='বিশেষ খবর (Highlighted)')
    highlighted_at = models.DateTimeField(null=True, blank=True, verbose_name='হাইলাইট করা তারিখ (Highlighted At)')

    def save(self, *args, **kwargs):
        # Set highlighted_at when highlighted is set to True
        if self.highlighted and not self.highlighted_at:
            self.highlighted_at = timezone.now()
        elif not self.highlighted:
            self.highlighted_at = None  # Clear the timestamp if not highlighted

        # Automatically untick `section_highlighted`, `breaking_news`, and `for_you` if expired
        expiry_time_30days = timezone.now() - timedelta(days=30)
        if self.section_highlighted and self.created_at < expiry_time_30days:
            self.section_highlighted = False
        if self.breaking_news and self.created_at < expiry_time_30days:
            self.breaking_news = False
        if self.for_you and self.created_at < expiry_time_30days:
            self.for_you = False

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def time_since_created(self):
        return timesince(self.created_at, timezone.now())

    def get_formatted_time_date_since_created(self):
        # Add 6 hours to the original created_at time
        created_time = self.created_at + timedelta(hours=6)

        # Convert English numbers to Bangla with leading zero
        def convert_to_bangla_number(number, leading_zero=False):
            bangla_numerals = '০১২৩৪৫৬৭৮৯'
            number_str = f"{number:02}" if leading_zero else str(number)  # Add leading zero if necessary
            return ''.join(bangla_numerals[int(digit)] for digit in number_str)

        # Format time in ১২-hour Bangla format with AM/PM
        def format_bangla_time(time):
            hour = time.hour
            minute = time.minute
            am_pm = "এএম" if hour < 12 else "পিএম"
            hour = hour % 12 or 12  # Convert to 12-hour format
            return f"{convert_to_bangla_number(hour, leading_zero=True)}:{convert_to_bangla_number(minute, leading_zero=True)} {am_pm}"

        # Format the date in Bangla
        def format_bangla_date(date):
            bangla_months = ['জানুয়ারি', 'ফেব্রুয়ারি', 'মার্চ', 'এপ্রিল', 'মে', 'জুন', 'জুলাই', 'আগস্ট', 'সেপ্টেম্বর',
                             'অক্টোবর', 'নভেম্বর', 'ডিসেম্বর']
            day = convert_to_bangla_number(date.day, leading_zero=True)  # Add leading zero for days
            month = bangla_months[date.month - 1]
            year = convert_to_bangla_number(date.year)
            return f"{day} {month} {year}"

        # Format time and date in Bangla with the adjusted time
        formatted_time = format_bangla_time(created_time)
        formatted_date = format_bangla_date(created_time)

        return f"{formatted_time}, {formatted_date}"

from django.db import models
from django.core.exceptions import ValidationError

class FrontPage(models.Model):
    news_item = models.OneToOneField(
        NewsList,
        on_delete=models.CASCADE,
        related_name='front_page',
        verbose_name='সংবাদ (News)'
    )
    serial_number = models.PositiveIntegerField(
        choices=[(i, str(i)) for i in range(1, 10)],
        unique=True,
        verbose_name='সিরিয়াল (Serial)'
    )

    def save(self, *args, **kwargs):
        # Ensure no more than 9 items have serial numbers
        if FrontPage.objects.filter(serial_number__isnull=False).count() >= 9:
            raise ValidationError('You cannot have more than 9 items on the front page.')

        super().save(*args, **kwargs)

    def __str__(self):
        return self.news_item.title  # Return the title of the news item




# Comment Model
class Commenter(models.Model):
    name = models.CharField(max_length=50, default='', verbose_name='নাম (Name)')
    designation = models.CharField(max_length=255, blank=True, default='', verbose_name='উপাধি (Designation)')
    image = models.ImageField(
        upload_to='commenters/',
        verbose_name='মন্তব্যকারীর ছবি (Commenter Image)',
        default='img/logo.png'
    )
    social_media_link = models.URLField(blank=True, null=True, verbose_name='সোশ্যাল মিডিয়া লিঙ্ক (Social Media Link)')

    def __str__(self):
        return self.name


class Comment(models.Model):
    title = models.CharField(max_length=100, verbose_name='শিরোনাম (Title)')
    description = models.TextField(verbose_name='বিবরণ (Description)')
    commenter = models.ForeignKey(
        Commenter,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='মন্তব্যকারী (Commenter)'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='তৈরি হওয়ার তারিখ (Created At)')
    is_active = models.BooleanField(default=False, verbose_name='সক্রিয় (Active)')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_formatted_time_since_created(self):
        now = timezone.now()
        time_diff = now - self.created_at

        # Convert English numbers to Bangla
        def convert_to_bangla_number(number):
            bangla_numerals = '০১২৩৪৫৬৭৮৯'
            return ''.join(bangla_numerals[int(digit)] for digit in str(number))

        if time_diff < timedelta(minutes=1):
            return "কয়েক সেকেন্ড আগে"
        elif time_diff < timedelta(hours=1):
            minutes = int(time_diff.total_seconds() / 60)
            return f"{convert_to_bangla_number(minutes)} মিনিট আগে"
        elif time_diff < timedelta(days=1):
            hours = int(time_diff.total_seconds() / 3600)
            return f"{convert_to_bangla_number(hours)} ঘণ্টা আগে"
        else:
            days = int(time_diff.total_seconds() / 86400)
            return f"{convert_to_bangla_number(days)} দিন আগে"


from django.db import models
from django.utils import timezone
from datetime import timedelta

class Video(models.Model):
    youtube_url = models.URLField(verbose_name='YouTube URL')
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='বিভাগ (Category)'
    )
    title = models.TextField(max_length=255, verbose_name='Title', blank=True)
    reporter = models.CharField(max_length=255, verbose_name='Reporter', blank=True, null=True)
    description = models.TextField(verbose_name='Description', blank=True, null=True)
    news_link = models.URLField(verbose_name='Related News Link', blank=True, null=True)
    highlighted = models.BooleanField(default=False, verbose_name='Highlighted')

    highlight_until = models.DateTimeField(blank=True, null=True, verbose_name='Highlight Until')
    verified = models.BooleanField(default=False, verbose_name='Verified')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created Time')

    highlighted_at = models.DateTimeField(null=True, blank=True, verbose_name='Highlighted At')

    video_code = models.IntegerField(unique=True, blank=True, null=True, verbose_name='Video Code')

    def save(self, *args, **kwargs):
        # Generate a unique video_code if not already set
        if not self.video_code:
            last_video = Video.objects.order_by('-video_code').first()
            self.video_code = last_video.video_code + 1 if last_video else 700001

        # Set highlighted_at when highlighted is True, clear when False
        if self.highlighted and not self.highlighted_at:
            self.highlighted_at = timezone.now()
        elif not self.highlighted:
            self.highlighted_at = None

        # Set default highlight_until to 24 hours from now
        if self.highlighted and not self.highlight_until:
            self.highlight_until = timezone.now() + timedelta(hours=24)

        super().save(*args, **kwargs)

    def time_since_created(self):
        """Returns time since creation in a human-readable format."""
        return timesince(self.created_at, timezone.now())

    def get_formatted_time_date_since_created(self):
        """Formats the creation time and date in Bangla."""
        created_time = self.created_at + timedelta(hours=6)

        def convert_to_bangla_number(number, leading_zero=False):
            bangla_numerals = '০১২৩৪৫৬৭৮৯'
            number_str = f"{number:02}" if leading_zero else str(number)
            return ''.join(bangla_numerals[int(digit)] for digit in number_str)

        def format_bangla_time(time):
            hour = time.hour
            minute = time.minute
            am_pm = "এএম" if hour < 12 else "পিএম"
            hour = hour % 12 or 12
            return f"{convert_to_bangla_number(hour, leading_zero=True)}:{convert_to_bangla_number(minute, leading_zero=True)} {am_pm}"

        def format_bangla_date(date):
            bangla_months = [
                'জানুয়ারি', 'ফেব্রুয়ারি', 'মার্চ', 'এপ্রিল', 'মে', 'জুন',
                'জুলাই', 'আগস্ট', 'সেপ্টেম্বর', 'অক্টোবর', 'নভেম্বর', 'ডিসেম্বর'
            ]
            day = convert_to_bangla_number(date.day, leading_zero=True)
            month = bangla_months[date.month - 1]
            year = convert_to_bangla_number(date.year)
            return f"{day} {month} {year}"

        formatted_time = format_bangla_time(created_time)
        formatted_date = format_bangla_date(created_time)

        return f"{formatted_time}, {formatted_date}"

    def __str__(self):
        return self.title


from django.db import models

class PhotoGallery(models.Model):
    caption = models.TextField(verbose_name='ক্যাপশন', blank=True)
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='বিভাগ (Category)'
    )
    image = models.ImageField(upload_to='gallery/', verbose_name='ছবি')
    news_link = models.URLField(verbose_name='Related News Link', blank=True, null=True)
    verified = models.BooleanField(default=False, verbose_name='যাচাইকৃত ')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.caption or "Untitled Photo"

class AdvertisementBase(models.Model):
    title = models.TextField(max_length=255, blank=True, null=True,
                             verbose_name='শিরোনাম (Title)')
    media = models.FileField(upload_to='media/', blank=True, null=True,
                             verbose_name='ফাইল আপ্লোড করুন (Upload File)')
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='তৈরি হওয়ার তারিখ (Created At)')
    is_active = models.BooleanField(default=False,
                                    verbose_name='সক্রিয় (Active)')

    def __str__(self):
        return self.title if self.title else "কোন শিরোনাম নেই"

    def has_media(self):
        return bool(self.media)

    class Meta:
        abstract = True

class AdvertisementOfflineChart(AdvertisementBase):
    pass

class AdvertisementOnlineChart(AdvertisementBase):
    pass


class PopupAd(models.Model):
    image = models.ImageField(upload_to='popup_ads/')
    link = models.URLField(max_length=200,blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"Popup Ad - {self.link}"

# Define the validation function
def validate_excluding_spaces(value):
    if len(value.replace(" ", "")) > 1000:
        raise ValidationError("Exceeded 1000 characters excluding spaces.")

class Footer(models.Model):
    field_name_1 = models.CharField(max_length=100, blank=True, null=True, help_text="প্রথম ফিল্ডের নাম")
    field_value_1 = models.CharField(max_length=255, blank=True, null=True, help_text="প্রথম ফিল্ডের মান")
    field_name_2 = models.CharField(max_length=100, blank=True, null=True, help_text="দ্বিতীয় ফিল্ডের নাম (ঐচ্ছিক)")
    field_value_2 = models.CharField(max_length=255, blank=True, null=True, help_text="দ্বিতীয় ফিল্ডের মান (ঐচ্ছিক)")
    # Update the model field
    field_value_3 = models.TextField(blank=True,null=True,
                    help_text="তৃতীয় ফিল্ডের মান (ঐচ্ছিক)",validators=[validate_excluding_spaces])


    mobile = models.CharField(max_length=15, blank=True, null=True, help_text="মোবাইল নম্বর")
    email = models.EmailField(blank=True, null=True, help_text="ইমেইল")
    ads_email = models.EmailField(blank=True, null=True, help_text="বিজ্ঞাপনের ইমেইল")
    footer_description = models.TextField(blank=True, null=True, help_text="ফুটার বর্ণনা")

    def save(self, *args, **kwargs):
        # Ensure only one footer record is created
        if not self.pk and Footer.objects.exists():
            raise ValueError("Only one Footer instance is allowed.")
        super(Footer, self).save(*args, **kwargs)

    def __str__(self):
        return f"Footer: {self.field_name_1}: {self.field_value_1}"


from django.db import models

class ContactInfo(models.Model):
    # Fields for English
    title_en = models.CharField(max_length=100, verbose_name="Title (English)")
    address_en1_title = models.TextField(default='',max_length=500,verbose_name="Address-1-Title (English)")
    address_en1_value = models.TextField(default='',max_length=500,verbose_name="Address-1 (English)")
    address_en2_title = models.TextField(default='',max_length=500,verbose_name="Address-2-Title (English)")
    address_en2_value = models.TextField(default='',max_length=500,verbose_name="Address-2 (English)")
    publication_name = models.TextField(default='',max_length=500, blank=True ,verbose_name="Publication Name (English)")
    phone_en = models.CharField(max_length=50,default='', blank=True ,verbose_name="Phone (English)")
    mobile_en = models.CharField(max_length=50,default='', blank=True, verbose_name="Mobile (English)")

    email_news_en = models.EmailField(verbose_name="News Email (English)")
    email_ads_en = models.EmailField(verbose_name="Ads Email (English)")

    # Fields for Bengali
    title_bn = models.CharField(max_length=100, verbose_name="Title (Bengali)")
    address_bn1_title = models.TextField(default='',max_length=800,verbose_name="Address-1-Title (Bengali)")
    address_bn1_value = models.TextField(default='',max_length=800,verbose_name="Address-1 (Bengali)")
    address_bn2_title = models.TextField(default='',max_length=800,verbose_name="Address-2-Title (Bengali)")
    address_bn2_value = models.TextField(default='',max_length=800,verbose_name="Address-2 (Bengali)")
    publication_name_bn = models.TextField(default='',max_length=500, blank=True ,verbose_name="Publication Name (Bengali)")
    phone_bn = models.CharField(max_length=50,default='', blank=True, verbose_name="Phone (Bengali)")
    mobile_bn = models.CharField(max_length=50,default='', blank=True, verbose_name="Mobile (Bengali)")



    class Meta:
        verbose_name = "Contact Information"
        verbose_name_plural = "Contact Information"

    def __str__(self):
        return f"Contact Info - {self.title_en}"
