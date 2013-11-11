from django.core.management.base import BaseCommand
from django.db import connection, transaction


class Command(BaseCommand):
    help = "Refresh film ratings cache"
    
    def handle(self, *args, **options):  # TODO: filter down to core users
        cursor = connection.cursor()
        sql = """
        update ktapp_film f, (
        select f.id,
        coalesce(sum(v.rating=1), 0) as r1,
        coalesce(sum(v.rating=2), 0) as r2,
        coalesce(sum(v.rating=3), 0) as r3,
        coalesce(sum(v.rating=4), 0) as r4,
        coalesce(sum(v.rating=5), 0) as r5
        from ktapp_film f
        left join ktapp_vote v on v.film_id=f.id
        group by f.id
        ) t
        set f.number_of_ratings_1 = t.r1,
            f.number_of_ratings_2 = t.r2,
            f.number_of_ratings_3 = t.r3,
            f.number_of_ratings_4 = t.r4,
            f.number_of_ratings_5 = t.r5
        where f.id = t.id
        """
        cursor.execute(sql)
        transaction.commit_unless_managed()
        self.stdout.write("Ratings cache refreshed.")
