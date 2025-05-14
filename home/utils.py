from django.utils import timezone
from .models import FrontPage, NewsList, Video, Ad,EPaper  # Make sure Ad is imported
from datetime import datetime




# def get_active_e_paper():
#     """Retrieve the latest active EPaper object, or None if no active one exists."""
#     try:
#         return EPaper.objects.filter(is_active=True).latest('id')
#     except EPaper.DoesNotExist:
#         return None



# E-paper logic end

# Ads logic start
def get_active_ads(category):
    """
    Utility function to get active ads for a specific category or for 'section_category_details'.
    If a category is provided, it filters based on that category.
    If the 'section_category_details' is needed, it filters separately.
    """
    now = datetime.now()

    if category == 'section_category_details':
        return Ad.objects.filter(category='section_category_details', is_active=True, start_date__lte=now,
                                 end_date__gte=now)

    # For all other categories
    return Ad.objects.filter(category=category, is_active=True)
# Ads logic end


# Front page logic start
def get_selected_news_slots():
    latest_highlighted_news = NewsList.objects.filter(verified=True, highlighted=True).order_by('-created_at')[:3]
    latest_highlighted_news_ids = latest_highlighted_news.values_list('id', flat=True)

    # Initialize news slots
    news_slots = {i: None for i in range(1, 10)}

    # Get the front-page news
    front_page_news = FrontPage.objects.order_by('serial_number')[:9]
    for item in front_page_news:
        news_slots[item.serial_number] = item.news_item

    front_page_news_ids = [item.news_item_id for item in front_page_news]
    additional_recent_news = NewsList.objects.filter(verified=True).exclude(id__in=front_page_news_ids).exclude(
        id__in=latest_highlighted_news_ids).order_by('-created_at')
    recent_news_iter = iter(additional_recent_news)

    # Fill any remaining empty news slots
    for slot in news_slots:
        if news_slots[slot] is None:
            try:
                news_slots[slot] = next(recent_news_iter)
            except StopIteration:
                break

    all_news = [news_slots[i] for i in range(1, 10)]
    return news_slots, all_news
# Front page logic end


# Video logic start

def extract_video_id(youtube_url):
    # Function to extract the YouTube video ID from the URL
    # Example implementation (You might need to adjust this based on your URL format):
    video_id = youtube_url.split('v=')[-1].split('&')[0]
    return video_id

def get_videos():
    """
    Retrieve the highlighted video and a list of other videos excluding the highlighted one.
    """
    # Get the highlighted video (first video that matches the highlighted criteria)
    highlighted_video = Video.objects.filter(
        verified=True,
        highlighted=True,
        highlight_until__gt=timezone.now()
    ).first()

    # Get all other videos, excluding the highlighted one
    video_list = Video.objects.filter(
        verified=True
    ).exclude(id=highlighted_video.id if highlighted_video else None)[:3]

    # Return the video data
    return {
        'highlighted_video': highlighted_video,
        'video_list': video_list
    }




