from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    """Form for posting messages with optional file attachments."""

    class Meta:
        model = Message
        fields = ['content', 'image', 'pdf', 'video']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your thoughts with the Kingsapark community...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'pdf': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'video': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/*'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        image = cleaned_data.get('image')
        pdf = cleaned_data.get('pdf')
        video = cleaned_data.get('video')

        # Ensure at least one field is filled
        if not content and not image and not pdf and not video:
            raise forms.ValidationError('Please provide either text content or a file attachment.')

        return cleaned_data

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Validate image size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image file size must be less than 5MB.')
        return image

    def clean_pdf(self):
        pdf = self.cleaned_data.get('pdf')
        if pdf:
            # Validate PDF size (max 10MB)
            if pdf.size > 10 * 1024 * 1024:
                raise forms.ValidationError('PDF file size must be less than 10MB.')
            # Validate file extension
            if not pdf.name.lower().endswith('.pdf'):
                raise forms.ValidationError('Only PDF files are allowed.')
        return pdf

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video:
            # Validate video size (max 50MB)
            if video.size > 50 * 1024 * 1024:
                raise forms.ValidationError('Video file size must be less than 50MB.')
        return video
