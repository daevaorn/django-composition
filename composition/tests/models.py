from django.db import models
from django.db.models import signals

from composition import CompositionField
from composition.shortcuts import ForeignAttributeField#,\
                                       #ChildsAggregationField, AttributesAggregationField


D = dict

class Visit(models.Model):
    event = models.ForeignKey("Event")

    class Meta:
        app_label = "composition"

class Event(models.Model):
    visit_count=CompositionField(
        native=models.PositiveIntegerField(default=0),
        trigger=[# Only for test. Don't do incremental counts in production code
            D(
                on=signals.post_save,
                do=lambda event, visit, signal: event.visit_count + 1
            ),
            D(
                on=signals.post_delete,
                do=lambda event, visit, signal: event.visit_count - 1
            )
        ],
        commons=D(
            sender_model="composition.Visit",
            field_holder_getter=lambda visit: visit.event,
        ),
        commit=True,
        update_method=D(
            do=0,
            initial=0,
            queryset=lambda event: event.visit_set.all(),
            name="sync_visit_count"
        )
    )

    class Meta:
        app_label = "composition"

class Country(models.Model):
    name = models.CharField(max_length=250)

    class Meta:
        app_label="composition"

class Person(models.Model):
    name = models.CharField(max_length=250)
    country = models.ForeignKey(Country)

    class Meta:
        app_label="composition"

class Movie(models.Model):
    title = models.CharField(max_length=250)
    director = models.ForeignKey(Person)

    headline = CompositionField(
        native=models.CharField(max_length=250),
        trigger=D(
            sender_model=Person,
            field_holder_getter=lambda director: director.movie_set.all(),
            do=lambda movie, _, signal: "%s, by %s" % (movie.title, movie.director.name)
        )
    )

    class Meta:
        app_label = "composition"

class Comment(models.Model):
    post = models.ForeignKey("Post", related_name="comments")

    class Meta:
        app_label = "composition"

class Post(models.Model):
    comment_count=CompositionField(
        native=models.PositiveIntegerField(default=0),
        trigger=D(
            on=(signals.post_save, signals.post_delete),
            do=lambda post, comment, signal: post.comments.count(),
            sender_model=Comment,
            field_holder_getter=lambda comment: comment.post,
        )
    )

    class Meta:
        app_label = "composition"

"""
class HLComment(models.Model):
    post = models.ForeignKey("HLPost", related_name="comments")

    class Meta:
        app_label = "composition"

class HLPost(models.Model):
    comment_count = ChildsAggregation(
        "comments",
        lambda post: post.comments.count(),
        native=models.PositiveIntegerField()
    )

    class Meta:
        app_label = "composition"
"""


class HLMovie(models.Model):
    title = models.CharField(max_length=250)
    director = models.ForeignKey(Person)

    #headline = AttributesAggregationField(
    #             native=models.CharField(max_length=250),
    #             fields=["director"],
    #             do=lambda movie: "%s, by %s" % (movie.title, movie.director.name)
    #          )

    director_name = ForeignAttributeField("director.name")
    director_country = ForeignAttributeField("director.country.name")

    class Meta:
        app_label = "composition"

"""
class HLIngridient(models.Model):
    name = models.CharField(max_length=100)

class HLFood(models.Model):
    ingridients = models.ManyToManyField(HLIngridient)

    ingridients_str = ChildsAggregation(
        native=models.CharField(max_length=250),
        field="ingridients",
        do=lambda food: ", ",join(food.ingridients.all(),
        signal=ingridient_added,
        instance_getter=lambda instance, to, *args, **kwargs: to
    )

    class Meta:
        app_label = "composition"
"""
