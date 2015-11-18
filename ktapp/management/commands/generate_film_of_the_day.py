import datetime
import random

from django.core.management.base import BaseCommand

from ktapp import models


class Command(BaseCommand):
    help = 'Generate Film of the Day'

    def handle(self, *args, **options):
        self.today = datetime.date.today()
        models.OfTheDay.objects.filter(domain=models.OfTheDay.DOMAIN_FILM).filter(day__lte=self.today).update(public=True)
        self.future = datetime.date.today() + datetime.timedelta(days=2)
        self.stdout.write('Generating Film Of the Day for %s...' % self.future)
        try:
            fotd = models.OfTheDay.objects.get(
                domain=models.OfTheDay.DOMAIN_FILM,
                day=self.future,
            )
        except models.OfTheDay.DoesNotExist:
            fotd = None
        if fotd:
            self.stdout.write('Film Of the Day generated: %s' % unicode(fotd.film))
            return
        offset = self.future.weekday()
        self.from_date = self.future - datetime.timedelta(days=offset)  # this Monday
        self.until_date = self.future - datetime.timedelta(days=offset-6)  # this Sunday
        weekday = self.future.isoweekday()
        while True:
            film_of_the_day = {
                1: self.get_old_film,
                2: self.get_international_film,
                3: self.get_hidden_gem,
                4: self.get_premier_film,
                5: self.get_top250_film,
                6: self.get_new_film,
                7: self.get_hungarian_film,
            }[weekday]()
            if weekday == 4:
                break  # get_premier_film cannot generate another film, so we must break no matter what
            if not self.is_it_duplicate(film_of_the_day):  # check if it's repetition within a year
                break
        fotd = models.OfTheDay.objects.create(
            domain=models.OfTheDay.DOMAIN_FILM,
            day=self.future,
            film=film_of_the_day,
        )
        self.stdout.write('Film Of the Day generated: %s' % unicode(fotd.film))

    def is_it_duplicate(self, film_of_the_day):
        fotd_from_the_last_year = models.OfTheDay.objects.filter(
            domain=models.OfTheDay.DOMAIN_FILM,
            day__gte=self.future - datetime.timedelta(days=365),
        )
        fotds = set()
        for f in fotd_from_the_last_year:
            fotds.add(f.id)
        return film_of_the_day.id in fotds

    def get_old_film(self):
        return models.Film.objects.filter(
            main_poster__isnull=False,
            number_of_ratings__gte=50,
            average_rating__gte=4,
            year__lte=1989,
            number_of_comments__gte=5,
        ).exclude(
            main_premier__gte=self.from_date,
        # ).count()  # 612
        ).order_by('?')[0]

    def get_international_film(self):
        keyword_hungarian_id = models.Keyword.objects.get(keyword_type='C', name='magyar').id
        keyword_american_id = models.Keyword.objects.get(keyword_type='C', name='amerikai').id
        return models.Film.objects.filter(
            main_poster__isnull=False,
            number_of_ratings__gte=50,
            average_rating__gte=4,
            number_of_comments__gte=5,
        ).exclude(
            keywords__in=[keyword_hungarian_id, keyword_american_id],
        ).exclude(
            main_premier__gte=self.from_date,
        # ).count()  # 414
        ).order_by('?')[0]

    def get_hidden_gem(self):
        return models.Film.objects.filter(
            main_poster__isnull=False,
            number_of_ratings__gte=10,
            number_of_ratings__lte=29,
            average_rating__gte=4,
            number_of_comments__gte=1,
        ).exclude(
            main_premier__gte=self.from_date,
        # ).count()  # 478
        ).order_by('?')[0]

    def get_premier_film(self):
        return models.Film.objects.raw('''
        SELECT f.*, COUNT(DISTINCT w.wished_by_id) AS wish_count
        FROM ktapp_film f
        LEFT JOIN ktapp_premier p ON p.film_id = f.id
        LEFT JOIN ktapp_wishlist w ON w.film_id = f.id AND w.wish_type = 'Y'
        WHERE main_premier BETWEEN %s AND %s OR p.`when` BETWEEN %s AND %s
        GROUP BY f.id
        ORDER BY COUNT(DISTINCT w.wished_by_id) + f.number_of_ratings_4 + f.number_of_ratings_5 DESC
        LIMIT 1
        ''', [
            self.from_date, self.until_date,
            self.from_date, self.until_date,
        ])[0]

    def get_top250_film(self):
        films = models.Film.objects.filter(
            main_poster__isnull=False,
            number_of_ratings__gte=100,
            average_rating__gte=4,
            genre_cache_is_music_video=False,
            genre_cache_is_mini=False,
            genre_cache_is_short=False,
        ).exclude(
            main_premier__gte=self.from_date,
        ).order_by('-average_rating')[:250]
        # return len(films)  # 250
        return random.choice(films)

    def get_new_film(self):
        return models.Film.objects.filter(
            main_poster__isnull=False,
            number_of_ratings__gte=50,
            average_rating__gte=4,
            year__gte=2000,
            number_of_comments__gte=5,
        ).exclude(
            main_premier__gte=self.from_date,
        # ).count()  # 359
        ).order_by('?')[0]

    def get_hungarian_film(self):
        keyword_hungarian_id = models.Keyword.objects.get(keyword_type='C', name='magyar').id
        return models.Film.objects.filter(
            main_poster__isnull=False,
            number_of_ratings__gte=30,
            average_rating__gte=4,
            number_of_comments__gte=3,
            keywords=keyword_hungarian_id,
        ).exclude(
            main_premier__gte=self.from_date,
        # ).count()  # 108
        ).order_by('?')[0]
