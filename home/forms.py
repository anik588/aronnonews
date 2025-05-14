from django import forms
from .models import Section, Category

class SectionAdminForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Section
        fields = '__all__'

    def clean_categories(self):
        categories = self.cleaned_data.get('categories', [])
        if len(categories) > 4:
            raise forms.ValidationError('You cannot select more than 4 categories.')
        return categories
