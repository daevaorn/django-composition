"""Test for composition low level interface"""
from django.test import TestCase

from composition.tests.generic import *

from composition.tests.models import Movie, Visit, Person, Event,\
                                                  Post, Comment

class LowEventTest(GenericEventTest, TestCase):
    event_model = Event
    visit_model = Visit

class LowMovieTest(GenericMovieTest, TestCase):
    movie_model = Movie

class LowPostTest(GenericPostTest, TestCase):
    post_model = Post
    comment_model = Comment
