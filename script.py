import django
import os

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aronno2.settings')
django.setup()

from home.models import Section

def get_section_categories():
    sections = Section.objects.prefetch_related('categories').all()
    section_categories = {}

    for section in sections:
        categories = [category.name for category in section.categories.all()]
        section_categories[section.name] = categories

    return sections, section_categories

# Call the function and print results
if __name__ == "__main__":
    sections, section_categories = get_section_categories()
    print("Sections:", sections)
    print("Section Categories:", section_categories)
