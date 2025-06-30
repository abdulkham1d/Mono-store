from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from apps.users.models import User
from .models import Review, Customer, ShippingAddress, Contact


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Review',
            }),
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
    }))


class RegistrationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username',
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm Password',
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last name',
    }))
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First name',
    }))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2')


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('name',)
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Name',
            })
        }


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ('address', 'city', 'region', 'phone')
        widgets = {
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your Address',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your City',
            }),
            'region': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your Region',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your Phone',
            })
        }


class ContactForm(forms.ModelForm):
    """
    Contact form - connected to model
    """

    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'subject', 'message']

        # Widgets and attributes
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
                'required': True,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+998 (99) 123 45 67',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Message subject',
                'required': True,
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Write your message here...',
                'required': True,
            }),
        }

        # Labels
        labels = {
            'name': 'Full Name',
            'email': 'Email Address',
            'phone': 'Phone Number',
            'subject': 'Subject',
            'message': 'Message',
        }

        # Help texts
        help_texts = {
            'phone': 'Optional. Example: +1234567890',
            'message': 'Please enter at least 10 characters',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Telefon raqam validatorini sozlash
        from django.core.validators import RegexValidator
        phone_validator = RegexValidator(
            regex=r'^\+?[0-9\s\-\(\)]{7,20}$',
            message="Iltimos, toʻgʻri telefon raqamini kiriting"
        )
        self.fields['phone'].validators = [phone_validator]

        # Barcha maydonlarni required qilish (phone dan tashqari)
        for field_name, field in self.fields.items():
            if field_name != 'phone':
                field.required = True

    def clean_name(self):
        """Name validation"""
        name = self.cleaned_data.get('name')
        if name:
            # Only letters and spaces
            if not all(c.isalpha() or c.isspace() for c in name):
                raise forms.ValidationError('Name should only contain letters and spaces')

            # At least 2 words
            if len(name.split()) < 2:
                raise forms.ValidationError('Please enter your full name (first and last name)')

        return name

    def clean_subject(self):
        """Subject validation"""
        subject = self.cleaned_data.get('subject')
        if subject and len(subject) < 5:
            raise forms.ValidationError('Subject must be at least 5 characters long')
        return subject

    def clean_message(self):
        """Message validation"""
        message = self.cleaned_data.get('message')
        if message:
            if len(message) < 10:
                raise forms.ValidationError('Message must be at least 10 characters long')

            # Check for spam words
            spam_words = ['spam', 'casino', 'viagra', 'lottery', 'winner', 'congratulations']
            message_lower = message.lower()
            for spam_word in spam_words:
                if spam_word in message_lower:
                    raise forms.ValidationError('Your message contains inappropriate content')

        return message

    def clean_email(self):
        """Email validation"""
        email = self.cleaned_data.get('email')
        if email:
            # Blocked domains
            blocked_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com', 'mailinator.com']
            domain = email.split('@')[1].lower()
            if domain in blocked_domains:
                raise forms.ValidationError('This email provider is not allowed')

        return email
