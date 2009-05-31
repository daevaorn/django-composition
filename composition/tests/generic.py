from composition.tests import models

class BaseTest(object):
    def renew_object(self, obj):
        instance = getattr(self, obj)
        setattr(self, obj, instance.__class__.objects.get(pk=instance.pk))

class GenericEventTest(BaseTest):
    def setUp(self):
        self.event = self.event_model.objects.create()

        for i in range(5):
            self.visit_model.objects.create(event=self.event)

    def test_event(self):
        self.renew_object("event")
        self.assertEqual(self.event.visit_count, 5)

        self.event.visit_count = 0
        self.event.save()

        self.event.sync_visit_count()

        self.renew_object("event")
        self.assertEqual(self.event.visit_count, 5)

class GenericMovieTest(BaseTest):
    def setUp(self):
        self.country = models.Country.objects.create(name="USA")
        self.person = models.Person.objects.create(
            name="George Lucas",
            country=self.country
        )

        self.movie = self.movie_model(
            title="Star Wars Episode IV: A New Hope",
            director=self.person
        )
        self.movie.save()

    def test_movie(self):
        self.movie.update_headline()

        self.renew_object("movie")
        self.assertEqual(
            self.movie.headline,
            "Star Wars Episode IV: A New Hope, by George Lucas"
        )

        self.person.name = "George W. Lucas"
        self.person.save()

        self.renew_object("movie")
        self.assertEqual(
            self.movie.headline,
            "Star Wars Episode IV: A New Hope, by George W. Lucas"
        )

class GenericPostTest(BaseTest):
    def setUp(self):
        self.post = self.post_model.objects.create()

        for i in range(5):
            self.comment_model.objects.create(post=self.post)

    def test_post(self):
        self.renew_object("post")
        self.assertEqual(self.post.comment_count, 5)

        self.post.comment_count = 0
        self.post.save()

        self.post.update_comment_count()

        self.renew_object("post")
        self.assertEqual(self.post.comment_count, 5)
