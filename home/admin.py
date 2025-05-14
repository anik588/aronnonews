from datetime import timedelta
import pytz
from django.contrib import admin

from django.urls import reverse
from django.utils.html import format_html
from django.utils.timesince import timesince


from .models import (
    Ad, AdvertisementOfflineChart, PopupAd,
    Section, Category,
    Commenter, Comment,
    NewsList, PhotoGallery, EPaper, FrontPage, AdvertisementOnlineChart, Footer,ContactInfo
)
from django.core.cache import cache
from .models import Video

class ActiveStateFilter(admin.SimpleListFilter):
    title = 'active state'
    parameter_name = 'active_state'

    def lookups(self, request, model_admin):
        return (
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        )

    def queryset(self, request, queryset):
        active_state = cache.get('comments_active_state', True)
        value = self.value()
        if value == 'active':
            return queryset if active_state else queryset.none()
        elif value == 'inactive':
            return queryset if not active_state else queryset.none()
        return queryset

from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User, Group
from django.contrib import admin
from django.urls import reverse, NoReverseMatch
from django.apps import apps


class CustomAdminSite(admin.AdminSite):
    """
    A custom admin site with grouped app list and customized permissions.
    """
    site_header = "Custom Admin Dashboard"
    site_title = "Admin Portal"
    index_title = "Welcome to the Custom Admin"

    def get_inline_instances(self, request, obj=None):
        """
        Overriding to control which inlines are shown.
        """
        inline_instances = []
        for inline_class in self.get_inline_classes(request, obj):
            inline = inline_class(self.model, self.admin_site)
            # Debugging
            print(f"Processing inline: {inline}")
            # Ensure the inline always gets added
            if hasattr(inline, 'has_add_permission') and not inline.has_add_permission(request, obj):
                print(f"Inline blocked: {inline}")
                continue
            inline_instances.append(inline)
        return inline_instances

    def has_add_permission(self, request, obj=None):
        # Get the admin class for the model type of the object `obj`
        model_admin = self._registry.get(type(obj))

        # Check if the admin class has a `has_add_permission` method defined
        if model_admin and hasattr(model_admin, 'has_add_permission'):
            # Call the `has_add_permission` method on that admin class
            return model_admin.has_add_permission(request, obj)

        # If no `has_add_permission` method is defined or no admin class exists, allow addition by default
        return True

    def has_change_permission(self, request, obj=None):
        model_admin = self._registry.get(type(obj))
        if model_admin and hasattr(model_admin, 'has_change_permission'):
            return model_admin.has_change_permission(request, obj)
        return True  # Default to True if no custom check is defined

    def has_view_permission(self, request, obj=None):
        model_admin = self._registry.get(type(obj))
        if model_admin and hasattr(model_admin, 'has_view_permission'):
            return model_admin.has_view_permission(request, obj)
        return True  # Default to True if no custom check is defined

    def has_delete_permission(self, request, obj=None):
        model_admin = self._registry.get(type(obj))
        if model_admin and hasattr(model_admin, 'has_delete_permission'):
            return model_admin.has_delete_permission(request, obj)
        return True  # Default to True if no custom check is defined

    def has_module_permission(self, request):
        # Check module-level permissions
        return True  # Default to True if no custom check is defined


    def get_app_list(self, request, app_label=None):
        """
        Override the default method to group models under custom categories.
        """
        grouped_models = {
            "Content": [
                {"model_name": "newslist", "app_label": "home"},
                {"model_name": "frontpage", "app_label": "home"},
                {"model_name": "photogallery", "app_label": "home"},
                {"model_name": "video", "app_label": "home"},
                {"model_name": "epaper", "app_label": "home"},
            ],
            "Comments": [
                {"model_name": "commenter", "app_label": "home"},
                {"model_name": "comment", "app_label": "home"},
            ],
            "Advertisements": [
                {"model_name": "ad", "app_label": "home"},
                {"model_name": "advertisementofflinechart", "app_label": "home"},
                {"model_name": "advertisementonlinechart", "app_label": "home"},
                {"model_name": "popupad", "app_label": "home"},
            ],
            "Sections": [
                {"model_name": "section", "app_label": "home"},
                {"model_name": "category", "app_label": "home"},
            ],
            "Contacts & Footer": [
                {"model_name": "footer", "app_label": "home"},
                {"model_name": "contactinfo", "app_label": "home"},
            ],

        }

        custom_app_list = []
        for group_name, models in grouped_models.items():
            model_list = []
            for model_info in models:
                try:
                    model = apps.get_model(model_info["app_label"], model_info["model_name"])
                    admin_url = reverse(
                        f"admin:{model._meta.app_label}_{model._meta.model_name}_changelist"
                    )
                    model_list.append({
                        "name": model._meta.verbose_name_plural.title(),
                        "object_name": model._meta.object_name,
                        "admin_url": admin_url,
                        "app_label": model._meta.app_label,
                    })
                except (LookupError, NoReverseMatch) as e:
                    print(f"Error adding model {model_info['model_name']}: {str(e)}")

            if model_list:
                custom_app_list.append({
                    "name": group_name,
                    "app_label": "custom",  # Custom group label
                    "models": model_list
                })

        # Include default app models not explicitly grouped
        default_apps = super().get_app_list(request, app_label)
        for app in default_apps:
            if app['app_label'] != 'home':  # Exclude already-grouped 'home' app models
                custom_app_list.append(app)

        return custom_app_list


# Instantiate the custom admin site
custom_admin_site = CustomAdminSite(name='custom_admin')
admin.site = custom_admin_site
# Custom UserAdmin to handle groups safely
class CustomUserAdmin(DefaultUserAdmin):


    def get_fieldsets(self, request, obj=None):
        """
        Remove 'groups' and 'user_permissions' from the fieldsets.
        """
        fieldsets = super().get_fieldsets(request, obj)
        filtered_fieldsets = []
        for name, options in fieldsets:
            fields = options.get("fields", ())
            # Exclude groups and user_permissions
            fields = tuple(f for f in fields if f not in ["groups", "user_permissions"])
            filtered_fieldsets.append((name, {**options, "fields": fields}))
        return filtered_fieldsets

    def get_form(self, request, obj=None, **kwargs):
        """
        Remove 'groups' and 'user_permissions' from the form.
        """
        form = super().get_form(request, obj, **kwargs)
        for field_name in ["groups", "user_permissions"]:
            if field_name in form.base_fields:
                del form.base_fields[field_name]
        return form


# Safely unregister Group if registered
try:
    custom_admin_site.unregister(Group)
except admin.sites.NotRegistered:
    pass
# Register User with the custom admin site
custom_admin_site.register(User, CustomUserAdmin)




#  ----------------------  grouping END ------------


# Register models with the custom admin site
# Content Group -- Start-------------

# NewsList Start
class NewsListAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'reporter',
        'category',
        'section',
        'verified',
        'highlighted',
        'section_highlighted',
        'created_at',
        'breaking_news',
        'for_you',
        'views_count',
        'highlighted_at',
    )

    list_filter = (
        'category', 'section', 'verified', 'highlighted', 'breaking_news', 'created_at', 'for_you',
        'section_highlighted', 'highlighted_at')
    search_fields = ('red_tag', 'title', 'title2', 'title3','reporter')
    readonly_fields = ('views_count', 'created_at', 'highlighted_at')

    def category_name_bn(self, obj):
        # Show the Bangla name of the category
        return obj.category.name_bn

    category_name_bn.short_description = 'বিভাগের নাম (Category Name in Bangla)'

    def section_name_bn(self, obj):
        # Show the Bangla name of the section, or 'No Section' if not available
        return obj.section.name_bn if obj.section else 'No Section'

    section_name_bn.short_description = 'সেকশনের নাম (Section Name in Bangla)'

    def time_since_created(self, obj):
        return timesince(obj.created_at)

    time_since_created.short_description = 'তৈরি হওয়ার তারিখ (Created At)'

    # Custom actions
    def toggle_verified(self, request, queryset):
        for obj in queryset:
            obj.verified = not obj.verified
            obj.save()

    toggle_verified.short_description = "Change Verified Status"

    def toggle_highlighted(self, request, queryset):
        for obj in queryset:
            obj.highlighted = not obj.highlighted
            obj.save()

    toggle_highlighted.short_description = "Change Highlighted Status"

    def toggle_section_highlighted(self, request, queryset):
        for obj in queryset:
            obj.section_highlighted = not obj.section_highlighted
            obj.save()

    toggle_section_highlighted.short_description = "Change Section Highlighted Status"

    def toggle_breaking_news(self, request, queryset):
        for obj in queryset:
            obj.breaking_news = not obj.breaking_news
            obj.save()

    toggle_breaking_news.short_description = "Change Breaking News Status"

    def toggle_for_you(self, request, queryset):
        for obj in queryset:
            obj.for_you = not obj.for_you
            obj.save()

    toggle_for_you.short_description = "Change For-You Status"

    # Adding actions to the admin interface
    actions = [toggle_verified, toggle_highlighted, toggle_section_highlighted, toggle_breaking_news, toggle_for_you]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            # Make 'is_active' read-only for non-superusers
            readonly_fields = readonly_fields + ('verified',)
        return readonly_fields

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser:
            # Hide 'active' and 'verified' for non-superusers by not including them in the fields
            fields = [field for field in fields if field not in ['verified']]
        return fields


custom_admin_site.register(NewsList, NewsListAdmin)


# NewsList END
# Front News Control Start
class FrontPageAdmin(admin.ModelAdmin):
    autocomplete_fields = ['news_item']
    list_display = ('news_item', 'serial_number')
    fields = ('news_item', 'serial_number')


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Filter only verified news items
        return qs.filter(news_item__verified=True)



custom_admin_site.register(FrontPage, FrontPageAdmin)


# Front News Control Start

from django.contrib import admin

class PhotoGalleryAdmin(admin.ModelAdmin):
    list_display = ('caption', 'verified', 'created_at')
    search_fields = ('caption',)  # Corrected to use 'caption' instead of 'title'
    list_filter = ('verified',)  # List filter for 'verified'
    exclude = ('category',)  # Exclude the 'category' field globally

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            # Make 'verified' read-only for non-superusers
            readonly_fields = readonly_fields + ('verified',)
        return readonly_fields

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if 'category' in fields:
            fields.remove('category')  # Dynamically remove 'category'
        if not request.user.is_superuser:
            # Further restrict fields for non-superusers
            fields = [field for field in fields if field not in ['verified']]
        return fields

# Register the model with the custom admin
custom_admin_site.register(PhotoGallery, PhotoGalleryAdmin)

from django.utils import timezone
from datetime import timedelta

class VideoAdmin(admin.ModelAdmin):
    # Define the columns to display in the admin panel
    list_display = ('video_code','verified', 'title', 'created_at', 'highlighted')
    readonly_fields = ('video_code', 'highlighted_at')  # Make these fields read-only
    search_fields = ('video_code', 'title')
    list_filter = ('highlighted',)

    def created_time_display(self, obj):
        """Display the created time in a human-readable format"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')  # Format the date as per your requirement
    created_time_display.short_description = 'Created Time'  # Custom column title for the created time

    def save_model(self, request, obj, form, change):
        """Override save_model to ensure highlight_until is correctly set when highlighted is true"""
        if obj.highlighted and not obj.highlight_until:
            obj.highlight_until = timezone.now() + timedelta(hours=24)
        elif not obj.highlighted:
            obj.highlight_until = None  # Reset if not highlighted
        super().save_model(request, obj, form, change)  # Call the parent class method to save the object

    def get_readonly_fields(self, request, obj=None):
        """Make certain fields read-only for non-superusers"""
        readonly_fields = super().get_readonly_fields(request, obj)

        # If the user is not a superuser, make 'verified' read-only
        if not request.user.is_superuser:
            readonly_fields = readonly_fields + ('verified',)

        return readonly_fields

    def get_fields(self, request, obj=None):
        """Hide certain fields for non-superusers"""
        fields = super().get_fields(request, obj)

        # If the user is not a superuser, remove 'verified' from the form fields
        if not request.user.is_superuser:
            fields = [field for field in fields if field != 'verified']

        return fields

# Register the Video model with the custom admin
custom_admin_site.register(Video, VideoAdmin)

# video END

# E Paper Start
class EPaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'pdf_file', 'thumbnail', 'upload_time', 'is_active')  # Display the 'upload_time' in the list
    list_filter = ('is_active',)
    search_fields = ('title',)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            # Make 'is_active' read-only for non-superusers
            readonly_fields = readonly_fields + ('is_active',)
        return readonly_fields

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser:
            # Hide 'is_active' for non-superusers by not including it in the form fields
            fields = [field for field in fields if field not in ['is_active']]
        return fields

custom_admin_site.register(EPaper, EPaperAdmin)

# E Paper END
# ------Content group ------ END

from django.contrib import admin
from django.utils.timezone import localtime, timedelta
from .models import Comment, Commenter  # Ensure you have these models imported


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    verbose_name = 'মন্তব্য'  # Bengali for 'Comment'
    verbose_name_plural = 'মন্তব্যগুলি'  # Bengali for 'Comments'

    def has_add_permission(self, request, obj=None):
        return True  # No restrictions for adding comments

    def has_change_permission(self, request, obj=None):
        return True  # No restrictions for editing comments

    def has_delete_permission(self, request, obj=None):
        return True  # No restrictions for deleting comments


class CommenterAdmin(admin.ModelAdmin):
    inlines = [CommentInline]  # Include CommentInline in Commenter admin
    list_display = ('name', 'designation')
    search_fields = ('name',)

    verbose_name = 'মন্তব্যকারী'  # Bengali for 'Commenter'
    verbose_name_plural = 'মন্তব্যকারীরা'  # Bengali for 'Commenters'

    # Remove all permission checks
    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def get_inline_instances(self, request, obj=None):
        """
        Ensure that inline instances are always processed correctly, even if
        permissions are ignored or overridden.
        """
        inline_instances = []
        for inline_class in self.inlines:
            inline = inline_class(self.model, self.admin_site)
            # Always add inline instances, regardless of permissions
            inline_instances.append(inline)
        return inline_instances

class CommentAdmin(admin.ModelAdmin):
    list_display = ('title', 'commenter', 'created_at', 'time_since_created', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    actions = ['toggle_is_active']

    verbose_name = 'মন্তব্য'  # Bengali for 'Comment'
    verbose_name_plural = 'মন্তব্যগুলি'  # Bengali for 'Comments'

    def time_since_created(self, obj):
        return time_since_in_bengali(obj.created_at)

    time_since_created.short_description = 'প্রকাশের সময়'  # Bengali for 'Time Since Published'

    def toggle_is_active(self, request, queryset):
        for obj in queryset:
            obj.is_active = not obj.is_active
            obj.save()

    toggle_is_active.short_description = "Toggle Active Status"

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            readonly_fields = readonly_fields + ('is_active',)
        return readonly_fields

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser:
            fields = [field for field in fields if field not in ['is_active']]
        return fields


def time_since_in_bengali(datetime_obj):
    time_diff = localtime() - datetime_obj
    if time_diff < timedelta(minutes=1):
        return 'কমেন্টটি এখনই পোস্ট করা হয়েছে'
    elif time_diff < timedelta(hours=1):
        minutes = int(time_diff.total_seconds() // 60)
        return f'{minutes} মিনিট আগে'
    elif time_diff < timedelta(days=1):
        hours = int(time_diff.total_seconds() // 3600)
        return f'{hours} ঘণ্টা আগে'
    elif time_diff < timedelta(days=7):
        days = int(time_diff.total_seconds() // 86400)
        return f'{days} দিন আগে'
    else:
        return datetime_obj.strftime('%d/%m/%Y')  # 'DD/MM/YYYY' format


# Registering the models with the custom admin site
custom_admin_site.register(Commenter, CommenterAdmin)
custom_admin_site.register(Comment, CommentAdmin)

# Commenter & Comments END
# ------------- Commenter & Comments Group --- END

# ads Group -- Start --------------
# Ads Start
class AdAdmin(admin.ModelAdmin):
    list_display = ('category', 'get_bdt_start_date', 'get_bdt_end_date', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('category',)
    ordering = ('-start_date',)

    def get_bdt_start_date(self, obj):
        """Return the start date in Bangladesh Time."""
        if obj.start_date:
            return obj.start_date.astimezone(pytz.timezone('Asia/Dhaka')).strftime('%Y-%m-%d %H:%M:%S')
        return None

    def get_bdt_end_date(self, obj):
        """Return the end date in Bangladesh Time."""
        if obj.end_date:
            return obj.end_date.astimezone(pytz.timezone('Asia/Dhaka')).strftime('%Y-%m-%d %H:%M:%S')
        return None

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            # Make 'is_active' read-only for non-superusers
            readonly_fields = readonly_fields + ('is_active',)
        return readonly_fields


    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser:
            # Hide 'active' and 'verified' for non-superusers by not including them in the fields
            fields = [field for field in fields if field not in ['is_active']]
        return fields

    get_bdt_start_date.admin_order_field = 'start_date'  # Allows sorting by start_date
    get_bdt_start_date.short_description = 'Start Date (BDT)'

    get_bdt_end_date.admin_order_field = 'end_date'  # Allows sorting by end_date
    get_bdt_end_date.short_description = 'End Date (BDT)'


custom_admin_site.register(Ad, AdAdmin)


# Ads END
# Base Admin Class

class AdvertisementBaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_active', 'has_media')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title',)
    readonly_fields = ('created_at',)

    def has_media(self, obj):
        """Show whether this advertisement has media."""
        return bool(obj.media)

    has_media.boolean = True

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser:
            # Hide 'is_active' for non-superusers
            fields = [field for field in fields if field != 'is_active']
        return fields

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            # Make 'is_active' read-only for non-superusers
            readonly_fields = readonly_fields + ('is_active',)
        return readonly_fields

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        if not request.user.is_superuser:
            list_display = [field for field in list_display if field != 'is_active']
        return list_display

# Register both models with the custom admin site
custom_admin_site.register(AdvertisementOfflineChart, AdvertisementBaseAdmin)
custom_admin_site.register(AdvertisementOnlineChart, AdvertisementBaseAdmin)




# Ad Chart END

# pop up AD Start
class PopupAdAdmin(admin.ModelAdmin):
    list_display = ('id', 'link', 'is_active')

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser:
            # Hide 'is_active' for non-superusers by not including it in the form fields
            fields = [field for field in fields if field not in ['is_active']]
        return fields

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            # Make 'is_active' read-only for non-superusers
            readonly_fields = readonly_fields + ('is_active',)
        return readonly_fields


custom_admin_site.register(PopupAd, PopupAdAdmin)


# pop up AD END
# --------- Ads Group -- END

# Section, Category Group -- Start--------------
# Section Start
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_bn')
    filter_horizontal = ('categories',)  # Allows selecting multiple categories easily


custom_admin_site.register(Section, SectionAdmin)


# Section END

# Category Start

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_bn')
    search_fields = ('name_en', 'name_bn')


custom_admin_site.register(Category, CategoryAdmin)

# Category END
# -------------- Section,Category Group --END


#Footer__START

class FooterAdmin(admin.ModelAdmin):
    list_display = ('field_value_1', 'mobile', 'email', 'ads_email')

    def has_add_permission(self, request):
        # Allow adding only if no Footer instance exists
        return not Footer.objects.exists() and request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Only superusers can change
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        # Allow view permissions to all staff or specific users as needed
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):  # <-- FIXED HERE
        # Only superusers can delete
        return request.user.is_superuser



# Register FooterAdmin with CustomAdminSite

custom_admin_site.register(Footer, FooterAdmin)

#Footer__END
from django.apps import apps
#ContactInfo_Start
from django.contrib import admin
from .models import ContactInfo

class ContactInfoAdmin(admin.ModelAdmin):
    # Display the relevant fields in the admin list view
    list_display = (
        'title_en', 'title_bn', 'address_en1_title', 'address_en1_value',
        'address_en2_title', 'address_en2_value', 'phone_en', 'phone_bn',
        'email_news_en'
    )

    # Override delete permission for this model
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # Only superusers can delete

# Register the model with the custom admin site
custom_admin_site.register(ContactInfo, ContactInfoAdmin)
#ContactInfo_END

admin.site = custom_admin_site




