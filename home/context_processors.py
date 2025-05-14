from .models import Footer

def footer_context(request):
    # Fetch the single Footer instance, or return None if it doesn't exist
    footer = Footer.objects.first()

    # Return the footer instance as part of the template context
    return {'footer': footer}


from .models import ContactInfo

def contact_info(request):
    contact = ContactInfo.objects.first()  # Assuming a single contact info entry
    return {'contact_info': contact}
