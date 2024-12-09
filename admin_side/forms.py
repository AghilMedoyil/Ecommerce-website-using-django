from PIL import Image
from django import forms
from .models import multiimage

class MultiImageForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = multiimage
        fields = ('img', 'x', 'y', 'width', 'height')

    def save(self, commit=True):
        multi_image_instance = super().save(commit=False)

        # Get crop values
        x = self.cleaned_data.get('x', 0)
        y = self.cleaned_data.get('y', 0)
        width = self.cleaned_data.get('width', 0)
        height = self.cleaned_data.get('height', 0)

        if x and y and width and height:
            # Open the uploaded image
            image = Image.open(multi_image_instance.img)

            # Crop and resize
            cropped_image = image.crop((x, y, x + width, y + height))
            resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)

            # Save the modified image back to the same path
            resized_image.save(multi_image_instance.img.path)

        if commit:
            multi_image_instance.save()

        return multi_image_instance
