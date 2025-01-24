from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import markdown

class UserProfile(models.Model):
    """
    Represents the profile of a user, linked to the Django User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    score = models.PositiveIntegerField(default=0)  # Store user score for ranking

    def __str__(self):
        return f"{self.user.username} Profile"

    def increase_score(self, amount=1):
        """Increase the score of the user safely."""
        self.score += amount
        self.save()

class Label(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default="#000000")  # Hex color code

    def __str__(self):
        return self.name

class Question(models.Model):
    """
    Represents a question posted by a user.
    """
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    likes_count = models.ManyToManyField(User, related_name="liked_questions", blank=True)
    dislikes_count = models.ManyToManyField(User, related_name="disliked_questions", blank=True)
    labels = models.ManyToManyField(Label, related_name="questions", blank=True)
    view_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

class Reply(models.Model):
    """
    Represents a reply to a question, with Markdown content.
    """
    content = models.TextField()  # Stores the reply content in Markdown format
    question = models.ForeignKey(Question, related_name="replies", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.content[:50]

    def get_content_as_html(self):
        """
        Converts the Markdown content into HTML for display in the question view.
        """
        return markdown.markdown(self.content, extensions=["fenced_code"])

# سیگنال‌ها برای مدیریت امتیاز
@receiver(post_save, sender=Reply)
def update_score_on_approval(sender, instance, created, **kwargs):
    """Update the user's score when a reply is approved."""
    if instance.is_approved:
        user_profile = instance.user.userprofile
        user_profile.increase_score()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile for new users."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the user profile when the user is saved."""
    instance.userprofile.save()

class QuestionReaction(models.Model):
    """
    Represents a reaction (like or dislike) to a question by a user.
    """
    LIKE = 1
    DISLIKE = -1
    REACTION_CHOICES = [
        (LIKE, "Like"),
        (DISLIKE, "Dislike"),
    ]

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.IntegerField(choices=REACTION_CHOICES)

    class Meta:
        unique_together = ("question", "user")

    def __str__(self):
        return f"{self.user.username} {self.get_reaction_type_display()} {self.question.title}"

class News(models.Model):
    """
    Represents a news article.
    """
    title = models.CharField(max_length=200, verbose_name="News Title")
    content = models.TextField(verbose_name="Content")
    published_at = models.DateTimeField(auto_now_add=True, verbose_name="Published Date")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="news", verbose_name="Author")

    def __str__(self):
        return self.title

