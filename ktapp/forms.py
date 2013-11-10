from django.forms import Form, ModelForm, ImageField
from ktapp.models import Comment, Quote, Trivia, Review, Picture, Topic


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["domain", "film", "topic", "poll", "content", "reply_to"]


class QuoteForm(ModelForm):
    class Meta:
        model = Quote
        fields = ["film", "content"]


class TriviaForm(ModelForm):
    class Meta:
        model = Trivia
        fields = ["film", "content"]


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ["film", "content"]


class PictureUploadForm(ModelForm):
    class Meta:
        model = Picture
        fields = ["film", "img", "picture_type", "source_url", "artists"]


class TopicForm(ModelForm):
    class Meta:
        model = Topic
        fields = ["title"]
