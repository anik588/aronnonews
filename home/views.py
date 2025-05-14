from .models import Ad, NewsList, Comment, PhotoGallery, Category, Section, FrontPage, EPaper, AdvertisementOnlineChart, \
    AdvertisementOfflineChart, ContactInfo

from home.models import PopupAd
import urllib.parse
from django.utils import timezone

import logging

from .utils import get_selected_news_slots, get_videos, get_active_ads

logger = logging.getLogger(__name__)


def news_view(request, section_id=None):
    news_slots, all_news = get_selected_news_slots()
    # Get highlighted news
    # Fetch all verified news
    # Fetch the latest highlighted news (if any)
    latest_highlighted_news = NewsList.objects.filter(verified=True, highlighted=True).order_by('-highlighted_at')[:3]

    all_recent_news = NewsList.objects.filter(verified=True).exclude(id__in=latest_highlighted_news).exclude(
        id__in=[news_item.id for news_item in all_news if news_item is not None]
    ).order_by('-created_at')[:15]


    # Fetch the highlighted video
    # Get video data
    video_data = get_videos()
    sections = Section.objects.all()
    # Get the latest comments and photos
    latest_comments = Comment.objects.filter(is_active=True).order_by('-created_at')[:3]
    photos = PhotoGallery.objects.filter(verified=True).order_by('-created_at')[:3]
    extra_photos = PhotoGallery.objects.filter(verified=True).exclude(id__in=photos.values_list('id', flat=True)).order_by('-created_at')[:3]


    # Filter and send breaking news to the template
    breaking_news = NewsList.objects.filter(breaking_news=True, verified=True).order_by('-created_at')

    section_categories = sections

    # Initialize all variables to a default value
    main_news1 = main_news2 = main_news3 = main_news4 = main_news5 = main_news6 = None
    secondary_news1 = secondary_news2 = secondary_news3 = secondary_news4 = secondary_news5 = secondary_news6 = []

    # Ensure you have enough sections before trying to access them
    if len(sections) > 0:
        main_news1 = NewsList.objects.filter(section=sections[0], verified=True, section_highlighted=True).order_by(
            '-created_at').first()
        secondary_news1 = NewsList.objects.filter(section=sections[0], section_highlighted=False,
                                                  verified=True).order_by('-created_at')[:4]

    if len(sections) > 1:
        main_news2 = NewsList.objects.filter(section=sections[1], verified=True, section_highlighted=True).order_by(
            '-created_at').first()
        secondary_news2 = NewsList.objects.filter(section=sections[1], section_highlighted=False,
                                                  verified=True).order_by('-created_at')[:4]

    if len(sections) > 2:
        main_news3 = NewsList.objects.filter(section=sections[2], verified=True, section_highlighted=True).order_by(
            '-created_at').first()
        secondary_news3 = NewsList.objects.filter(section=sections[2], section_highlighted=False,
                                                  verified=True).order_by('-created_at')[:4]

    if len(sections) > 3:
        main_news4 = NewsList.objects.filter(section=sections[3], verified=True, section_highlighted=True).order_by(
            '-created_at').first()
        secondary_news4 = NewsList.objects.filter(section=sections[3], section_highlighted=False,
                                                  verified=True).order_by('-created_at')[:4]

    if len(sections) > 4:
        main_news5 = NewsList.objects.filter(section=sections[4], verified=True, section_highlighted=True).order_by(
            '-created_at').first()
        secondary_news5 = NewsList.objects.filter(section=sections[4], section_highlighted=False,
                                                  verified=True).order_by('-created_at')[:4]

    if len(sections) > 5:
        main_news6 = NewsList.objects.filter(section=sections[5], verified=True, section_highlighted=True).order_by(
            '-created_at').first()
        secondary_news6 = NewsList.objects.filter(section=sections[5], section_highlighted=False,
                                                  verified=True).order_by('-created_at')[:4]

    # Get all categories that are linked to sections

    # Get categories that are linked to at least one section
    # Get categories that are not linked to any section and should be shown


    # Step 1: Filter categories without sections and shown on the front page
    categories_without_sections = Category.objects.filter(sections__isnull=True, show_in_frontpage=True)

    # Step 2: Get the first 4 categories and the remaining categories
    first_four_categories = categories_without_sections[:4]
    remaining_categories = categories_without_sections[4:]

    # Step 3: Get the news items for the first set of categories
    first_four_section_highlighted_news = NewsList.objects.filter(
        category__in=first_four_categories,
        section_highlighted=True
    ).order_by('-created_at')[:1]  # Get the latest 4

    first_four_remaining_news = NewsList.objects.filter(
        category__in=first_four_categories
    ).exclude(
        id__in=first_four_section_highlighted_news.values_list('id', flat=True)
    ).order_by('-created_at')[:4]  # Get the latest 4 excluding the highlighted ones

    # Step 4: Get the news items for the remaining categories
    remaining_section_highlighted_news = NewsList.objects.filter(
        category__in=remaining_categories,
        section_highlighted=True
    ).order_by('-created_at')[:1]  # Get the latest 4

    remaining_categories_news = NewsList.objects.filter(
        category__in=remaining_categories
    ).exclude(
        id__in=remaining_section_highlighted_news.values_list('id', flat=True)
    ).order_by('-created_at')[:4]  # Get the latest 4 excluding the highlighted ones


    #
    #     # Map category names to Bangla for the remaining categories
    #     frontpage_category_remaining_bangla = {
    #         get_bangla_name(category): news_items
    #         for category, news_items in frontpage_category_remaining.items()
    #     }

    # E paper

    # Most Read news
    top_news = NewsList.objects.order_by('-views_count')[:15]

    # Popover ads

    popup_ad = PopupAd.objects.filter(is_active=True).first()  # Get the first active ad
    print(f"Popup Ad Object: {popup_ad}")

    # Convert to JSON string
    # Prepare the context for rendering
    context = {
        'all_news': all_news,
        'all_recent_news': all_recent_news,
        'latest_highlighted_news': latest_highlighted_news,

        # new
        'main_news1': main_news1,
        'secondary_news1': secondary_news1,
        'main_news2': main_news2,
        'secondary_news2': secondary_news2,
        'main_news3': main_news3,
        'secondary_news3': secondary_news3,
        'main_news4': main_news4,
        'secondary_news4': secondary_news4,
        'main_news5': main_news5,
        'secondary_news5': secondary_news5,
        'main_news6': main_news6,
        'secondary_news6': secondary_news6,
        'section_categories': section_categories,
        'sections': sections,
        #videos
        'video_data':video_data,

        #comments
        'latest_comments': latest_comments,
        'photos': photos,
        'extra_photos':extra_photos,

        #
        'breaking_news': breaking_news,  # breaking news
        # # Category front page
        'first_four_categories': first_four_categories,
        'remaining_categories': remaining_categories,

        #         #section's catagory pass
        #         'sections': sections,

        # ADS
        'top_logo_ad': get_active_ads('top_logo'),
        'highlight_category_section_one': get_active_ads('highlight_category_section_one'),
        'highlight_category_section_two': get_active_ads('highlight_category_section_two'),
        'section_one_ads': get_active_ads('section_one'),
        'section_two_ads': get_active_ads('section_two'),
        'section_three_ads': get_active_ads('section_three'),
        'section_four_ads': get_active_ads('section_four'),
        'section_five_ads': get_active_ads('section_five'),
        'section_six_ads': get_active_ads('section_six'),
        # 'section_seven_ads': get_active_ads('section_seven'),
        'category_one_ads': get_active_ads('category_one'),
        'category_two_ads': get_active_ads('category_two'),

        'front_news_one_ad': get_active_ads('front_news_one'), #Home 1
        'front_news_two_ad': get_active_ads('front_news_two'), #Home 2
        'front_news_three_ad': get_active_ads('front_news_three'), #Selected 1
        'front_news_four_ad': get_active_ads('front_news_four'), #Selected 2


        # Most Read News
        'top_news': top_news,
        # popup ads

        'popup_ad': popup_ad,
    }

    print(f"Ad Object: {popup_ad}")
    return render(request, 'index.html', context)


def news_details(request, news_id):

    # Video template data
    video_data = get_videos()

    # Fetch the news item or return a 404 if not found
    news = get_object_or_404(NewsList, id=news_id)
    breaking_news = NewsList.objects.filter(breaking_news=True, verified=True).order_by('-created_at')
    # Get the session key for the news item
    session_key = f'viewed_news_{news_id}'

    # Check if the news item has already been viewed in the current session
    if not request.session.get(session_key, False):
        # Increment the view count
        news.views_count += 1
        news.save()

        # Mark this news item as viewed in the session
        request.session[session_key] = True

    # Match category of news to Category model

    # Access both English and Bangla category names
    if news.category:
        category_name_en = news.category.name_en
        category_name_bn = news.category.name_bn
    else:
        category_name_en = "No category"
        category_name_bn = "No category"

    # Get recent news for the same category
    category_recent_news = NewsList.objects.filter(verified=True,
                                                   category=news.category
                                                   ).exclude(id=news_id).order_by('-created_at')[
                           :10]  # Exclude the current news item

    # Get related sections' news (based on section) and exclude the entire category
    related_sections_news = NewsList.objects.filter(verified=True,
                                                    section=news.section
                                                    ).exclude(category=news.category).exclude(id=news_id).order_by(
        '-created_at')[:10]  # Exclude current news item

    # Get all recent news & Top Views (latest 10 items)
    all_recent_news = NewsList.objects.filter(verified=True).order_by('-created_at').exclude(
        category=news.category).exclude(id=news_id).exclude(section=news.section)[:15]
    top_news = NewsList.objects.filter(verified=True).order_by('-views_count').exclude(category=news.category).exclude(
        id=news_id).exclude(section=news.section)[:10]

    popup_ad = PopupAd.objects.filter(is_active=True).first()  # Get the first active ad
    print(f"Popup Ad Object: {popup_ad}")
    # Get the Bengali name for the section
    # section_bangla_name = get_section_bangla_name(news.section)
    # category_bangla_name = get_bangla_name(news.category)

    # Prepare the context
    context = {
                # E paper

        'top_logo_ad': get_active_ads('top_logo'),

        'article': news,
        'news_id': news_id,
        'category_recent_news': category_recent_news,
        'related_sections_news': related_sections_news,
        'all_recent_news': all_recent_news,

        'category_name_bn': category_name_bn,
        'category_name_en': category_name_en,

        'views_count': news.views_count,  # Add this line
        'breaking_news': breaking_news,  # breaking news
        'top_news': top_news,

        'news_details_ad': get_active_ads('news_details'),
        'news_details_side_ads_one': get_active_ads('news_details_side_ads_one'),
        'news_details_side_ads_two': get_active_ads('news_details_side_ads_two'),

        # Video
        'video_data':video_data,
        # popup ads

        'popup_ad': popup_ad,
    }

    return render(request, 'news_details.html', context)


def comment_details_view(request, comment_id):

    comment = get_object_or_404(Comment, id=comment_id)

    breaking_news = NewsList.objects.filter(breaking_news=True, verified=True).order_by('-created_at')

    all_comments = Comment.objects.filter(is_active=True).exclude(id=comment_id).order_by('-created_at')
    all_recent_news = NewsList.objects.filter(verified=True).order_by('-created_at')[:8]

    # Enumerate all_recent_news to include indices
    all_recent_news = list(enumerate(all_recent_news))

    num_comments = len(all_comments)
    row_1_comments = all_comments[:num_comments // 2]
    row_2_comments = all_comments[num_comments // 2:num_comments]

    context = {
            # E paper

        'comment': comment,
        'row_1_comments': row_1_comments,
        'row_2_comments': row_2_comments,
        'all_recent_news': all_recent_news,
        'top_logo_ad': get_active_ads('top_logo'),
        'breaking_news': breaking_news,  # breaking news
    }

    return render(request, 'comment_details.html', context)


from datetime import timedelta, datetime
from django.utils import timezone


def section_details(request, section_name):

    # Get the section object using the section_name (English name)
    section = get_object_or_404(Section, name_en=section_name)

    # Fetch breaking news and top news
    breaking_news = NewsList.objects.filter(breaking_news=True, verified=True).order_by('-created_at')
    top_news = NewsList.objects.order_by('-views_count')[:15]

    # Initialize a dictionary to hold news items for each category under this section
    category_news = {}



    # Get all categories under this section
    categories = section.categories.all()

    # Loop through each category and get the top 4 recent news items from the last 7 days
    for category in categories:
        recent_news = NewsList.objects.filter(
            category=category,
            verified=True,

        ).order_by('-created_at')[:10]

        if recent_news:  # Only add category to context if it has recent news
            category_news[category] = recent_news

    # Get 10 recent news items for the entire section from the last 7 days
    all_section_news = list(enumerate(NewsList.objects.filter(
        section=section,
        verified=True,

    ).order_by('-created_at')[:6]))

    # Get active ads for the section category
    section_category_ads = get_active_ads('section_category_ad')

    # Fetch top news for the section
    top_section_news = NewsList.objects.filter(section=section, verified=True).order_by('-views_count')[:10]

    # Get recent news excluding this section
    all_recent_news = NewsList.objects.filter(verified=True).exclude(section=section).order_by('-created_at')[:10]

    # Get selected news (e.g., 'For You' feature), excluding this section
    selected_news = NewsList.objects.filter(verified=True, for_you=True).exclude(section=section).order_by(
        '-created_at')[:5]

    # Context data to pass to the template
    context = {
            # E paper

        'top_logo_ad': get_active_ads('top_logo'),
        'breaking_news': breaking_news,  # Breaking news

        'section_page_ads_one': get_active_ads('section_page_ads_one'),
        'section_page_ads_two': get_active_ads('section_page_ads_two'),
        'section': section,
        'category_news': category_news,
        'all_section_news': all_section_news,  # Now contains index and news
        'top_section_news': top_section_news,
        'section_category_ad': section_category_ads,
        'all_recent_news': all_recent_news,

        'selected_news': selected_news,
        'top_news': top_news,
    }

    # Render the section details page
    return render(request, 'section_details.html', context)


# Adjust the import according to your model's location
def category_details(request, category_name_en):

    # Get the category object based on the English name
    category = get_object_or_404(Category, name_en=category_name_en)

    # Fetch news related to this category
    main_news = NewsList.objects.filter(category=category, verified=True).order_by('-created_at')[:5]
    breaking_news = NewsList.objects.filter(breaking_news=True, verified=True).order_by('-created_at')
    top_news = NewsList.objects.order_by('-views_count')[:15]
    all_recent_news = NewsList.objects.filter(verified=True).order_by('-created_at')[:10]


    # Get related sections for the current category
    related_sections = Section.objects.filter(categories=category)

    # Fetch news related to the sections
    section_news = NewsList.objects.filter(section__in=related_sections, verified=True).order_by('-created_at')[:10]

    # Fetch related categories excluding the current category
    related_categories = Category.objects.filter(sections__in=related_sections).exclude(id=category.id).distinct()

    context = {
            # E paper

        'top_logo_ad': get_active_ads('top_logo'),
        'news_items': main_news,
        'category': category,
        'breaking_news': breaking_news,
        'top_news': top_news,
        'all_recent_news': all_recent_news,
        'section_category_ad': get_active_ads('section_category_ads'),
        'section_news': section_news,
        'related_categories': related_categories,  # Add this line
    }

    return render(request, 'category_details.html', context)


def contact_us_view(request):


    breaking_news = NewsList.objects.filter(breaking_news=True, verified=True).order_by('-created_at')

    context = {
            # E paper

        'top_logo_ad': get_active_ads('top_logo'),
        'breaking_news': breaking_news,  # breaking news
    }
    return render(request, 'contact_us.html', context)



from .models import NewsList, ContactInfo

def about_us_view(request):

    breaking_news = NewsList.objects.filter(breaking_news=True, verified=True).order_by('-created_at')

    # Fetch contact info
    contact_info = ContactInfo.objects.first()

    if contact_info:
        contact_info_data = {
            # English fields
            'publication_name_en': contact_info.publication_name,
            'title_en': contact_info.title_en,
            'address_en1_title': contact_info.address_en1_title,
            'address_en1_value': contact_info.address_en1_value,
            'address_en2_title': contact_info.address_en2_title,
            'address_en2_value': contact_info.address_en2_value,
            'phone_en': contact_info.phone_en,
            'mobile_en': contact_info.mobile_en,

            'email_news_en': contact_info.email_news_en,
            'email_ads_en': contact_info.email_ads_en,

            # Bengali fields
            'publication_name_bn': contact_info.publication_name_bn,
            'title_bn': contact_info.title_bn,
            'address_bn1_title': contact_info.address_bn1_title,
            'address_bn1_value': contact_info.address_bn1_value,
            'address_bn2_title': contact_info.address_bn2_title,
            'address_bn2_value': contact_info.address_bn2_value,
            'phone_bn': contact_info.phone_bn,
            'mobile_bn': contact_info.mobile_bn,


        }
    else:
        contact_info_data = {
            # English fields (in case contact info is not found)
            'publication_name_en': None,
            'title_en': None,
            'address_en1_title': None,
            'address_en1_value': None,
            'address_en2_title': None,
            'address_en2_value': None,
            'phone_en': None,
            'mobile_en': None,

            'email_news_en': None,
            'email_ads_en': None,

            # Bengali fields (in case contact info is not found)
            'publication_name_bn': None,
            'title_bn': None,
            'address_bn1_title': None,
            'address_bn1_value': None,
            'address_bn2_title': None,
            'address_bn2_value': None,
            'phone_bn': None,
            'mobile_bn': None,

        }

    context = {

        'top_logo_ad': get_active_ads('top_logo'),
        'breaking_news': breaking_news,
        'contact_info': contact_info_data,
    }

    return render(request, 'about_us.html', context)




def policy_view(request):

    breaking_news = NewsList.objects.filter(breaking_news=True, verified=True).order_by('-created_at')

    context = {
            # E paper

        'top_logo_ad': get_active_ads('top_logo'),
        'breaking_news': breaking_news,  # breaking news
    }
    return render(request, 'policy.html', context)

from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from urllib.parse import unquote
import logging

logger = logging.getLogger(__name__)

def search_view(request, search_term):
    top_news = NewsList.objects.order_by('-views_count')[:15]
    all_recent_news = NewsList.objects.filter(verified=True).order_by('-created_at')[:10]
    breaking_news = NewsList.objects.filter(breaking_news=True, verified=True).order_by('-created_at')

    # Decode the search term if it's URL-encoded
    search_term = unquote(search_term)
    logger.debug(f"Decoded search term: {search_term}")


    breaking_news = NewsList.objects.filter(breaking_news=True, verified=True).order_by('-created_at')


    search_results = []  # Initialize the results list



    # Check if search_term is provided
    if search_term:
        # Log the raw and decoded search term
        logger.info(f"Received search term: {search_term}")

        # Define the fields to search across
        search_fields = [
            'title', 'description', 'red_tag', 'title2', 'title3',
            'description2', 'description3', 'category__name_en','category__name_bn', 'section__name_en', 'section__name_bn'
        ]

        # Dynamically build the Q object based on the fields
        query = Q()
        for field in search_fields:
            query |= Q(**{f"{field}__icontains": search_term})

        # Perform the query using the combined Q object
        search_results = NewsList.objects.filter(query)

        # Log the number of search results
        logger.info(f"Found {len(search_results)} search results for term: {search_term}")

    # Paginate the results - 4 per page
    paginator = Paginator(search_results, 4)
    page_number = request.GET.get('page', 1)

    try:
        # Get the results for the current page
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.get_page(paginator.num_pages)
    except PageNotAnInteger:
        page_obj = paginator.get_page(1)



    # Render the search results in the template
    return render(request, 'search.html', {
        'search_results': page_obj,  # Pass the paginated results
        'search_term': search_term,
        'top_logo_ad': get_active_ads('top_logo'),
        'breaking_news': breaking_news,  # Breaking news
        'all_recent_news': all_recent_news,
        'top_news': top_news,

        'front_news_one_ad': get_active_ads('front_news_one'), #Home 1
        'front_news_two_ad': get_active_ads('front_news_two'), #Home 2
    })


def advertisement_chart_view(request):
    # Fetch contact info
    contact_info = ContactInfo.objects.first()

    if contact_info:
        contact_info_data = {
            'mobile': contact_info.mobile_en,
            'phone': contact_info.phone_en,
            'email_ads': contact_info.email_ads_en,
            'address': contact_info.address_en1_value,
        }
    else:
        contact_info_data = {
            'mobile': None,

            'phone': None,
            'email_ads': None,
            'address': None,
        }

    # Fetch news and advertisements
    top_news = NewsList.objects.order_by('-views_count')[:15]
    all_recent_news = NewsList.objects.filter(verified=True).order_by('-created_at')[:10]
    breaking_news = NewsList.objects.filter(breaking_news=True, verified=True).order_by('-created_at')


    advertisements_offline = AdvertisementOfflineChart.objects.filter(is_active=True)
    advertisements_online = AdvertisementOnlineChart.objects.filter(is_active=True)

    context = {
        'contact_info': contact_info_data,
        'top_news': top_news,
        'all_recent_news': all_recent_news,
        'breaking_news': breaking_news,

        'advertisements_offline': advertisements_offline,
        'advertisements_online': advertisements_online,
    }

    return render(request, 'advertisements.html', context)


from django.shortcuts import render, get_object_or_404
from .models import Video
from .models import NewsList  # Assuming you also want news details in this context

def video_detail(request, video_code):
    top_news = NewsList.objects.order_by('-views_count')[:15]
    all_recent_news = NewsList.objects.filter(verified=True).order_by('-created_at')[:10]
    breaking_news = NewsList.objects.filter(breaking_news=True, verified=True).order_by('-created_at')

    # Retrieve the video by video_code
    video = get_object_or_404(Video, video_code=video_code, verified=True)

    # Extract the YouTube video ID from the URL
    video_id = None
    if 'v=' in video.youtube_url:
        video_id = video.youtube_url.split('v=')[-1]
    elif 'youtu.be/' in video.youtube_url:
        video_id = video.youtube_url.split('/')[-1]

    # Fetch the 8 most recent videos excluding the current one
    recent_videos = Video.objects.filter(verified=True).exclude(video_code=video_code).order_by('-created_at')[:9]

    # Prepare context for the template
    context = {
        'video': video,
        'video_id': video_id,
        'top_logo_ad': get_active_ads('top_logo'),

        'breaking_news': breaking_news,
        'all_recent_news': all_recent_news,
        'top_news': top_news,

        'front_news_one_ad': get_active_ads('front_news_one'),  # Home 1
        'front_news_two_ad': get_active_ads('front_news_two'),  # Home 2
        'recent_videos': recent_videos,  # Add the recent videos to context
    }

    return render(request, 'video_detail.html', context)

from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Video  # Assuming you have a Video model

def video_all(request):
    top_news = NewsList.objects.order_by('-views_count')[:15]
    all_recent_news = NewsList.objects.filter(verified=True).order_by('-created_at')[:10]
    breaking_news = NewsList.objects.filter(breaking_news=True, verified=True).order_by('-created_at')


    # Fetch the latest video
    latest_video = Video.objects.latest('created_at')  # Assuming 'created_at' is the field for time

    # Fetch all videos, excluding the latest one
    all_videos = Video.objects.exclude(id=latest_video.id).order_by('-created_at')  # Exclude latest video

    # Pagination for the "other_videos" section (3 videos per page)
    paginator = Paginator(all_videos, 6)  # Show 3 videos per page
    page_number = request.GET.get('page')
    videos = paginator.get_page(page_number)

    # Get the current set of videos for "other_videos"
    other_videos = videos.object_list  # Get the current set of 3 videos from the page

    return render(request, 'video_all.html', {
        'latest_video': latest_video,
        'other_videos': other_videos,
        'videos': videos,

        'breaking_news': breaking_news,
        'all_recent_news': all_recent_news,
        'top_news': top_news,

        'front_news_one_ad': get_active_ads('front_news_one'),  # Home 1
        'front_news_two_ad': get_active_ads('front_news_two'),  # Home 2
    })

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from .models import PhotoGallery

def photo_gallery_all(request):
    top_news = NewsList.objects.order_by('-views_count')[:15]
    all_recent_news = NewsList.objects.filter(verified=True).order_by('-created_at')[:10]
    breaking_news = NewsList.objects.filter(breaking_news=True, verified=True).order_by('-created_at')

    photos = PhotoGallery.objects.all().order_by('-created_at')  # Order by newest first
    paginator = Paginator(photos, 5)  # 20 photos per page

    page = request.GET.get('page')
    try:
        paginated_photos = paginator.page(page)
    except PageNotAnInteger:
        paginated_photos = paginator.page(1)
    except EmptyPage:
        paginated_photos = paginator.page(paginator.num_pages)

    context = {
        'photos': paginated_photos,

        'breaking_news': breaking_news,
        'all_recent_news': all_recent_news,
        'top_news': top_news,
    }
    return render(request, 'photogallery_all.html', context)




from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.core.cache import cache
from .models import NewsList, Category

def news_archive(request):

    breaking_news = NewsList.objects.filter(breaking_news=True, verified=True).order_by('-created_at')

    # Fetch categories (cached for performance)
    categories = cache.get_or_set('categories', Category.objects.all(), 300)

    # Fetch latest 20 news items
    latest_news = NewsList.objects.filter(verified=True).order_by('-created_at')[:20]

    # Filtering by date and category
    date_filter = request.GET.get('date', '').strip()
    category_filter = request.GET.get('category', '').strip()
    news_items = NewsList.objects.filter(verified=True).order_by('-created_at')

    if date_filter:
        news_items = news_items.filter(created_at__date=date_filter)
    if category_filter:
        news_items = news_items.filter(category__id=category_filter)

    # Check if news_items is empty
    no_news_found = not news_items.exists()

    # Pagination
    paginator = Paginator(news_items, 20)  # 20 news items per page
    page_number = request.GET.get('page')
    try:
        paged_news = paginator.get_page(page_number)
    except PageNotAnInteger:
        paged_news = paginator.get_page(1)
    except EmptyPage:
        paged_news = paginator.get_page(paginator.num_pages)

    # Render template with context
    return render(request, 'archive.html', {
        'categories': categories,
        'latest_news': latest_news,
        'news_items': paged_news,
        'no_news_found': no_news_found,  # Pass the flag to the template

                    # E paper
        'top_logo_ad': get_active_ads('top_logo'),
        'breaking_news': breaking_news,  # breaking news

    })



def using_terms_view(request):

    breaking_news = NewsList.objects.filter(breaking_news=True, verified=True).order_by('-created_at')

    context = {
            # E paper

        'top_logo_ad': get_active_ads('top_logo'),
        'breaking_news': breaking_news,  # breaking news
    }
    return render(request, 'using_terms.html', context)


def epaper_view(request):
    selected_date = request.GET.get("date", "").strip()
    epaper = None

    if selected_date:
        try:
            selected_date_obj = datetime.strptime(selected_date, "%B %Y")
            year = selected_date_obj.year
            month = selected_date_obj.month

            epaper = EPaper.objects.filter(
                upload_time__year=year,
                upload_time__month=month,
                is_active=True  # Ensure it's active
            ).first()
        except ValueError as e:
            epaper = None
    else:
        epaper = EPaper.objects.filter(is_active=True).order_by("-upload_time").first()

    latest_epapers = EPaper.objects.filter(is_active=True).order_by("-upload_time")[:4]

    return render(request, "epaper.html", {"epaper": epaper, "latest_epapers": latest_epapers})



from django.shortcuts import render, get_object_or_404
from .models import EPaper

def epaper_detail(request, id):
    epaper = get_object_or_404(EPaper, id=id)

    # Fetch the latest 4 e-papers (excluding the current one)
    latest_epapers = EPaper.objects.exclude(id=id).order_by("-upload_time")[:4]

    return render(request, "epaper.html", {"epaper": epaper, "latest_epapers": latest_epapers})










