from django import forms
from .models import Image
import requests
from django.core.files.base import ContentFile
from django.utils.text import slugify

class ImageCreateForm(forms.ModelForm):
    image_upload = forms.ImageField(required=False)  # Allow file uploads

    class Meta:
        model = Image
        fields = ['title', 'url', 'image_upload', 'description']
        widgets = {
            'url': forms.URLInput(attrs={'placeholder': 'Enter Image URL (Optional)'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        url = cleaned_data.get('url')
        image_upload = cleaned_data.get('image_upload')

        # If neither URL nor file is provided, raise an error
        if not url and not image_upload:
            raise forms.ValidationError("Either an image URL or an uploaded image is required.")

        if url:
            valid_extensions = ['jpg', 'jpeg', 'png']
            if "." in url:
                extension = url.rsplit('.', 1)[1].lower()
                if extension not in valid_extensions:
                    raise forms.ValidationError("Please enter a valid image URL.")

        return cleaned_data

    def save(self, commit=True):
        image = super().save(commit=False)
        image_url = self.cleaned_data.get('url')
        image_upload = self.cleaned_data.get('image_upload')

        if image_url:
            name = slugify(image.title)
            extension = image_url.rsplit('.', 1)[1].lower()
            image_name = f'{name}.{extension}'

            # Download the image from the URL
            response = requests.get(image_url)
            if response.status_code == 200:
                image.image.save(image_name, ContentFile(response.content), save=False)

        elif image_upload:
            image.image = image_upload  # Assign uploaded image

        if commit:
            image.save()
        return image
