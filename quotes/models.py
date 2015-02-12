"""
    Models module for Quotes app
"""
from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    """
        Tag model defines a keyword that can be associated with a Quote
    """
    name = models.CharField(max_length=20)

    def __unicode__(self):
        """
            Defines a string representation of the object
        """
        return self.name


class Quote(models.Model):
    """
        Quotes model defines most of the data for the application
    """
    text = models.TextField()
    author = models.CharField(max_length=100)
    source = models.CharField(max_length=150)
    notes = models.TextField(null=True)
    date_added = models.DateField(auto_now_add=True)
    order = models.IntegerField()
    user = models.ForeignKey(User)
    tags = models.ManyToManyField(Tag)

    def __unicode__(self):
        """
            Defines a string representation of the object
        """
        return self.text[:30]

    def get_tags_as_list_of_str(self):
        """
            Returns a list of strings that represent the tags associated with the quote
        """
        return [str(t) for t in self.tags.all()]

    def remove_tags_not_in_list(self, tags_new):
        """
            Any tags that are not in the tags_new list are removed from the quote
        """
        for t in self.tags.all():
            if not t.name in tags_new:
                self.tags.remove(t)

    def add_tag_from_str(self, new):
        """
            If there is a tag matching the new tag string, add that tag to the quote.
            Otherwise, create a new tag from the string and add it to the quote.
        """
        existing = Tag.objects.filter(name=new, quote__user=self.user)
        if len(existing) > 1:
            print "ERROR: duplicate tags"
        if existing:
            self.tags.add(existing[0])
        else:
            new_tag = Tag(name=new)
            new_tag.save()
            self.tags.add(new_tag)

