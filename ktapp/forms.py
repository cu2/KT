from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from ktapp import models


class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ['domain', 'film', 'topic', 'poll', 'content', 'reply_to']


class QuoteForm(forms.ModelForm):
    class Meta:
        model = models.Quote
        fields = ['film', 'content']


class TriviaForm(forms.ModelForm):
    class Meta:
        model = models.Trivia
        fields = ['film', 'content']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = models.Review
        fields = ['film', 'content']


class PictureUploadForm(forms.ModelForm):
    class Meta:
        model = models.Picture
        fields = ['film', 'img', 'picture_type', 'source_url']
        # fields = ['film', 'img', 'picture_type', 'source_url', 'artists']


class TopicForm(forms.ModelForm):
    class Meta:
        model = models.Topic
        fields = ['title']


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = models.KTUser
        fields = ['username', 'email', 'gender', 'location', 'year_of_birth']

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords don\'t match')
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label=('Password'),
        help_text=('Raw passwords are not stored, so there is no way to see '
                   'this user\'s password, but you can change the password '
                   'using <a href="password/">this form</a>.'))

    class Meta:
        model = models.KTUser
        fields = ['gender', 'location', 'year_of_birth']

    def clean_password(self):
        return self.initial['password']
