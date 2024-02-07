from django import forms

from ktapp import models


class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ["domain", "film", "topic", "poll", "content", "reply_to"]


class QuoteForm(forms.ModelForm):
    class Meta:
        model = models.Quote
        fields = ["film", "content"]


class TriviaForm(forms.ModelForm):
    class Meta:
        model = models.Trivia
        fields = ["film", "content"]


class ReviewForm(forms.ModelForm):
    class Meta:
        model = models.Review
        fields = ["film", "content"]


class PictureUploadForm(forms.ModelForm):
    class Meta:
        model = models.Picture
        fields = ["img", "picture_type", "source_url"]


class TopicForm(forms.ModelForm):
    class Meta:
        model = models.Topic
        fields = ["title"]


class UserChangeForm(forms.ModelForm):
    class Meta:
        model = models.KTUser
        exclude = ["password"]
