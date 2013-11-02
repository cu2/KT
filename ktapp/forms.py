from django.forms import ModelForm
from ktapp.models import Comment, Quote, Trivia


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
