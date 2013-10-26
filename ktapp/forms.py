from django.forms import ModelForm
from ktapp.models import Comment


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["domain", "film", "topic", "poll", "content", "reply_to"]
