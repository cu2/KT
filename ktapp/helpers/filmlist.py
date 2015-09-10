from ktapp import models
from ktapp import utils as kt_utils


def filmlist(user_id, filters=None, ordering=None, page=None, films_per_page=20):
    table_alias_idx = 0
    role_idx = 0
    additional_inner_joins = []
    my_rating_join_type = 'LEFT'
    additional_where = []
    additional_param = []
    additional_select = []
    nice_filters = []
    if filters:
        for filter_type, filter_value in filters:
            try:
                filter_value = kt_utils.strip_whitespace(filter_value)
            except AttributeError:
                filter_value = int(filter_value)
            if filter_type == 'title':
                title_pieces = []
                for title_piece in filter_value.split(' '):
                    title_piece = title_piece.strip()
                    if title_piece:
                        title_pieces.append(title_piece)
                        additional_where.append('''(f.orig_title LIKE %s OR f.second_title LIKE %s OR f.third_title LIKE %s)''')
                        additional_param.append('%{term}%'.format(term=title_piece))
                        additional_param.append('%{term}%'.format(term=title_piece))
                        additional_param.append('%{term}%'.format(term=title_piece))
                if title_pieces:
                    nice_filters.append(('title', ' '.join(title_pieces)))
            if filter_type == 'year':
                year_interval = kt_utils.str2interval(filter_value, int)
                if year_interval:
                    additional_where.append('''f.year BETWEEN %s AND %s''')
                    additional_param.append(year_interval[0])
                    additional_param.append(year_interval[1])
                    nice_filters.append(('year', filter_value))
            if filter_type == 'director':
                director_names = []
                for director_name in filter_value.split(','):
                    director_name = director_name.strip()
                    if director_name:
                        director_names.append(director_name)
                        directors = models.Artist.objects.filter(name__icontains=director_name)[:500]
                        if directors:
                            table_alias_idx += 1
                            additional_inner_joins.append('''
                                INNER JOIN ktapp_filmartistrelationship {table_name}
                                ON {table_name}.film_id = f.id
                                AND {table_name}.artist_id IN ({director_ids})
                                AND {table_name}.role_type = 'D'
                            '''.format(
                                table_name='director_%s' % table_alias_idx,
                                director_ids=','.join([str(d.id) for d in directors]),
                            ))
                if director_names:
                    nice_filters.append(('director', ', '.join(director_names)))
            if filter_type == 'actor':
                actor_names = []
                for actor_name in filter_value.split(','):
                    actor_name = actor_name.strip()
                    if actor_name:
                        actor_names.append(actor_name)
                        actors = models.Artist.objects.filter(name__icontains=actor_name)[:500]
                        if actors:
                            table_alias_idx += 1
                            role_idx += 1
                            additional_select.append('''
                                {table_name}.id AS role_id_{idx},
                                {table_name}.slug_cache AS role_slug_cache_{idx},
                                {table_name}.role_name AS role_role_name_{idx},
                                {table_name}.actor_subtype AS role_actor_subtype_{idx},
                            '''.format(
                                table_name='actor_%s' % table_alias_idx,
                                idx=role_idx,
                            ))
                            additional_inner_joins.append('''
                                INNER JOIN ktapp_filmartistrelationship {table_name}
                                ON {table_name}.film_id = f.id
                                AND {table_name}.artist_id IN ({actor_ids})
                                AND {table_name}.role_type = 'A'
                            '''.format(
                                table_name='actor_%s' % table_alias_idx,
                                actor_ids=','.join([str(a.id) for a in actors]),
                            ))
                if actor_names:
                    nice_filters.append(('actor', ', '.join(actor_names)))
            if filter_type == 'director_id':
                try:
                    director = models.Artist.objects.get(id=filter_value)
                except models.Artist.DoesNotExist:
                    director = None
                if director:
                    table_alias_idx += 1
                    additional_inner_joins.append('''
                        INNER JOIN ktapp_filmartistrelationship {table_name}
                        ON {table_name}.film_id = f.id
                        AND {table_name}.artist_id = {director_id}
                        AND {table_name}.role_type = 'D'
                    '''.format(
                        table_name='director_%s' % table_alias_idx,
                        director_id=director.id,
                    ))
                    nice_filters.append(('director_id', director.id))
            if filter_type == 'actor_id':
                try:
                    actor = models.Artist.objects.get(id=filter_value)
                except models.Artist.DoesNotExist:
                    actor = None
                if actor:
                    table_alias_idx += 1
                    role_idx += 1
                    additional_select.append('''
                        {table_name}.id AS role_id_{idx},
                        {table_name}.slug_cache AS role_slug_cache_{idx},
                        {table_name}.role_name AS role_role_name_{idx},
                        {table_name}.actor_subtype AS role_actor_subtype_{idx},
                    '''.format(
                        table_name='actor_%s' % table_alias_idx,
                        idx=role_idx,
                    ))
                    additional_inner_joins.append('''
                        INNER JOIN ktapp_filmartistrelationship {table_name}
                        ON {table_name}.film_id = f.id
                        AND {table_name}.artist_id = {actor_id}
                        AND {table_name}.role_type = 'A'
                    '''.format(
                        table_name='actor_%s' % table_alias_idx,
                        actor_id=actor.id,
                    ))
                    nice_filters.append(('actor_id', actor.id))
            if filter_type in {'country', 'genre', 'keyword'}:
                keyword_names = []
                for keyword_name in filter_value.split(','):
                    keyword_name = keyword_name.strip()
                    if keyword_name:
                        keyword_names.append(keyword_name)
                        keywords = models.Keyword.objects.filter(name__icontains=keyword_name)
                        if filter_type == 'country':
                            keywords = keywords.filter(keyword_type=models.Keyword.KEYWORD_TYPE_COUNTRY)
                        if filter_type == 'genre':
                            keywords = keywords.filter(keyword_type=models.Keyword.KEYWORD_TYPE_GENRE)
                        if filter_type == 'keyword':
                            keywords = keywords.filter(keyword_type__in=[models.Keyword.KEYWORD_TYPE_MAJOR, models.Keyword.KEYWORD_TYPE_OTHER])
                        keywords = keywords[:50]
                        if keywords:
                            table_alias_idx += 1
                            additional_inner_joins.append('''
                                INNER JOIN ktapp_filmkeywordrelationship {table_name}
                                ON {table_name}.film_id = f.id
                                AND {table_name}.keyword_id IN ({keyword_ids})
                                '''.format(
                                table_name='keyword_%s' % table_alias_idx,
                                keyword_ids=','.join([str(k.id) for k in keywords])
                            ))
                if keyword_names:
                    nice_filters.append((filter_type, ', '.join(keyword_names)))
            if filter_type == 'average_rating':
                min_value, max_value = filter_value.split('-')
                try:
                    avg_rating_min = float(kt_utils.strip_whitespace(min_value).replace(',', '.'))
                except ValueError:
                    avg_rating_min = None
                try:
                    avg_rating_max = float(kt_utils.strip_whitespace(max_value).replace(',', '.'))
                except ValueError:
                    avg_rating_max = None
                avg_rating_interval = kt_utils.minmax2interval(avg_rating_min, avg_rating_max, 0.0, 5.0)
                if avg_rating_interval:
                    additional_where.append('''f.average_rating BETWEEN %s AND %s''')
                    additional_param.append(avg_rating_interval[0])
                    additional_param.append(avg_rating_interval[1])
                    nice_filters.append((filter_type, filter_value))
            if filter_type == 'number_of_ratings':
                min_value, max_value = filter_value.split('-')
                try:
                    num_rating_min = int(kt_utils.strip_whitespace(min_value))
                except ValueError:
                    num_rating_min = None
                try:
                    num_rating_max = int(kt_utils.strip_whitespace(max_value))
                except ValueError:
                    num_rating_max = None
                num_rating_interval = kt_utils.minmax2interval(num_rating_min, num_rating_max, 0, 99999)
                if num_rating_interval:
                    additional_where.append('''f.number_of_ratings BETWEEN %s AND %s''')
                    additional_param.append(num_rating_interval[0])
                    additional_param.append(num_rating_interval[1])
                    nice_filters.append((filter_type, filter_value))
            if filter_type == 'number_of_comments':
                min_value, max_value = filter_value.split('-')
                try:
                    num_comment_min = int(kt_utils.strip_whitespace(min_value))
                except ValueError:
                    num_comment_min = None
                try:
                    num_comment_max = int(kt_utils.strip_whitespace(max_value))
                except ValueError:
                    num_comment_max = None
                num_comment_interval = kt_utils.minmax2interval(num_comment_min, num_comment_max, 0, 99999)
                if num_comment_interval:
                    additional_where.append('''f.number_of_comments BETWEEN %s AND %s''')
                    additional_param.append(num_comment_interval[0])
                    additional_param.append(num_comment_interval[1])
                    nice_filters.append((filter_type, filter_value))
            if filter_type == 'wished_by_id':
                wish_type, wished_by_id = filter_value.split(':')
                try:
                    wished_by = models.KTUser.objects.get(id=wished_by_id)
                except models.KTUser.DoesNotExist:
                    wished_by = None
                if wished_by:
                    table_alias_idx += 1
                    additional_inner_joins.append('''
                        INNER JOIN ktapp_wishlist {table_name}
                        ON {table_name}.film_id = f.id
                        AND {table_name}.wished_by_id = {wished_by_id}
                        AND {table_name}.wish_type = '{wish_type}'
                    '''.format(
                        table_name='wish_%s' % table_alias_idx,
                        wished_by_id=wished_by.id,
                        wish_type=wish_type,
                    ))
                    nice_filters.append((filter_type, filter_value))
            if filter_type == 'seen_by_id':
                try:
                    seen_by = models.KTUser.objects.get(id=filter_value)
                except models.KTUser.DoesNotExist:
                    seen_by = None
                if seen_by:
                    additional_select.append('''
                        {table_name}.rating AS other_rating,
                        {table_name}.`when` AS other_rating_when,
                        {table_name}.id AS other_rating_id,
                    '''.format(
                        table_name='seen_by_other',
                    ))
                    additional_inner_joins.append('''
                        INNER JOIN ktapp_vote {table_name}
                        ON {table_name}.film_id = f.id
                        AND {table_name}.user_id = {seen_by_id}
                    '''.format(
                        table_name='seen_by_other',
                        seen_by_id=seen_by.id,
                    ))
                    nice_filters.append((filter_type, filter_value))
            if filter_type == 'seen_it' and user_id:
                if filter_value == '1':
                    my_rating_join_type = 'INNER'
                    nice_filters.append((filter_type, filter_value))
                if filter_value == '0':
                    additional_where.append('''v.rating IS NULL''')
                    nice_filters.append((filter_type, filter_value))
            if filter_type == 'my_wish' and user_id:
                if filter_value == '1':
                    additional_where.append('''w.film_id IS NOT NULL''')
                    nice_filters.append((filter_type, filter_value))
                if filter_value == '0':
                    additional_where.append('''w.film_id IS NULL''')
                    nice_filters.append((filter_type, filter_value))
            if filter_type == 'fav_average_rating' and user_id:
                min_value, max_value = filter_value.split('-')
                try:
                    fav_avg_rating_min = float(kt_utils.strip_whitespace(min_value).replace(',', '.'))
                except ValueError:
                    fav_avg_rating_min = None
                try:
                    fav_avg_rating_max = float(kt_utils.strip_whitespace(max_value).replace(',', '.'))
                except ValueError:
                    fav_avg_rating_max = None
                fav_avg_rating_interval = kt_utils.minmax2interval(fav_avg_rating_min, fav_avg_rating_max, 0.0, 5.0)
                if fav_avg_rating_interval:
                    additional_where.append('''r.fav_average_rating BETWEEN %s AND %s''')
                    additional_param.append(fav_avg_rating_interval[0])
                    additional_param.append(fav_avg_rating_interval[1])
                    nice_filters.append((filter_type, filter_value))
            if filter_type == 'my_rating' and user_id:
                try:
                    min_value, max_value = filter_value.split('-')
                except ValueError:
                    min_value = max_value = filter_value
                try:
                    my_rating_min = int(kt_utils.strip_whitespace(min_value))
                except ValueError:
                    my_rating_min = None
                try:
                    my_rating_max = int(kt_utils.strip_whitespace(max_value))
                except ValueError:
                    my_rating_max = None
                my_rating_interval = kt_utils.minmax2interval(my_rating_min, my_rating_max, 0, 5)
                if my_rating_interval:
                    my_rating_join_type = 'INNER'
                    additional_where.append('''v.rating BETWEEN %s AND %s''')
                    additional_param.append(my_rating_interval[0])
                    additional_param.append(my_rating_interval[1])
                    nice_filters.append((filter_type, filter_value))
            if filter_type == 'other_rating':
                try:
                    min_value, max_value = filter_value.split('-')
                except ValueError:
                    min_value = max_value = filter_value
                try:
                    other_rating_min = int(kt_utils.strip_whitespace(min_value))
                except ValueError:
                    other_rating_min = None
                try:
                    other_rating_max = int(kt_utils.strip_whitespace(max_value))
                except ValueError:
                    other_rating_max = None
                other_rating_interval = kt_utils.minmax2interval(other_rating_min, other_rating_max, 0, 5)
                if other_rating_interval:
                    additional_where.append('''seen_by_other.rating BETWEEN %s AND %s''')
                    additional_param.append(other_rating_interval[0])
                    additional_param.append(other_rating_interval[1])
                    nice_filters.append((filter_type, filter_value))
    order_by = None
    if ordering:
        try:
            order_field, order_order = ordering
        except ValueError:
            order_field = ordering
            order_order = 'ASC'
        if order_order not in {'ASC', 'DESC'}:
            order_order = 'ASC'
        order_fields = []
        if order_field == 'title':
            order_fields = ['f.orig_title', 'f.year', 'f.id']
        if order_field == 'year':
            order_fields = ['f.year', 'f.orig_title', 'f.id']
        if order_field == 'director':
            order_fields = ['f.director_names_cache', 'f.orig_title', 'f.year', 'f.id']
        if order_field == 'genre':
            order_fields = ['f.genre_names_cache', 'f.orig_title', 'f.year', 'f.id']
        if order_field == 'number_of_ratings':
            order_fields = ['f.number_of_ratings', 'f.orig_title', 'f.year', 'f.id']
        if order_field == 'average_rating':
            order_fields = ['f.average_rating', 'f.number_of_ratings DESC', 'f.orig_title', 'f.year', 'f.id']
        if user_id:
            if order_field == 'fav_average_rating':
                order_fields = ['r.fav_average_rating', 'r.fav_number_of_ratings DESC', 'f.orig_title', 'f.year', 'f.id']
            if order_field == 'my_rating':
                order_fields = ['v.rating', 'f.orig_title', 'f.year', 'f.id']
            if order_field == 'my_rating_when':
                order_fields = ['v.`when`', 'v.id', 'f.orig_title', 'f.year', 'f.id']
            if order_field == 'my_wish':
                order_fields = ['CASE WHEN w.film_id IS NOT NULL THEN 1 ELSE 0 END', 'f.orig_title', 'f.year', 'f.id']
            if order_field == 'seen_it':
                order_fields = ['CASE WHEN v.rating IS NOT NULL THEN 1 ELSE 0 END', 'f.orig_title', 'f.year', 'f.id']
        if order_field == 'other_rating':
            order_fields = ['other_rating', 'f.orig_title', 'f.year', 'f.id']
        if order_field == 'other_rating_when':
            order_fields = ['other_rating_when', 'other_rating_id', 'f.orig_title', 'f.year', 'f.id']
        if order_field == 'number_of_comments':
            order_fields = ['f.number_of_comments', 'f.orig_title', 'f.year', 'f.id']
        if order_fields:
            order_by = ', '.join(['%s %s' % (order_fields[0], order_order)] + [of for of in order_fields[1:]])
    if page:
        try:
            page = int(page)
        except ValueError:
            page = None
    if user_id:
        sql_user_select = '''
            v.rating AS my_rating,
            v.`when` AS my_rating_when,
            CASE WHEN w.film_id IS NOT NULL THEN 1 ELSE 0 END AS my_wish,
            COALESCE(r.fav_number_of_ratings, 0) AS fav_number_of_ratings,
            r.fav_average_rating
        '''
        sql_user = '''
            {my_rating_join_type} JOIN ktapp_vote v ON v.film_id = f.id AND v.user_id = {user_id}
            LEFT JOIN ktapp_wishlist w ON w.film_id = f.id AND w.wished_by_id = {user_id} AND w.wish_type = 'Y'
            LEFT JOIN ktapp_recommendation r ON r.film_id = f.id AND r.user_id = {user_id}
        '''.format(
            user_id=user_id,
            my_rating_join_type=my_rating_join_type,
        )
    else:
        sql_user_select = '''
            NULL AS my_rating,
            NULL AS my_rating_when,
            0 AS my_wish,
            0 AS fav_number_of_ratings,
            NULL AS fav_average_rating
        '''
        sql_user = ''
    if films_per_page is not None:
        sql_limit = 'LIMIT {offset}, {row_count}'.format(
            offset=films_per_page * (page - 1) if page else 0,
            row_count=films_per_page,
        )
    else:
        sql_limit = ''
    sql = '''
        SELECT
          f.*,
          {additional_select}
          {sql_user_select}
        FROM ktapp_film f
        {additional_inner_joins}
        {sql_user}
        {additional_where}
        {order_by}
        {sql_limit}
    '''.format(
        additional_select='\n'.join(additional_select) if additional_select else '',
        additional_inner_joins='\n'.join(additional_inner_joins),
        sql_user_select=sql_user_select,
        sql_user=sql_user,
        additional_where='WHERE %s' % '\nAND\n'.join(additional_where) if additional_where else '',
        order_by='ORDER BY %s' % order_by if order_by else '',
        sql_limit=sql_limit,
    )
    qs = models.Film.objects.raw(sql, additional_param)
    # print qs.query.sql
    return qs, nice_filters


def get_filters_from_request(request):
    filters = []
    # seen_it
    # number_of_comments
    possible_fields = ['title', 'year', 'director', 'actor', 'country', 'genre', 'keyword', 'my_rating', 'other_rating', 'my_wish']
    for field in possible_fields:
        val = kt_utils.strip_whitespace(request.GET.get(field, ''))
        if val:
            filters.append((field, val))
    val = '%s-%s' % (kt_utils.strip_whitespace(request.GET.get('num_rating_min', '')), kt_utils.strip_whitespace(request.GET.get('num_rating_max', '')))
    if val != '':
        filters.append(('number_of_ratings', val))
    val = '%s-%s' % (kt_utils.strip_whitespace(request.GET.get('avg_rating_min', '')), kt_utils.strip_whitespace(request.GET.get('avg_rating_max', '')))
    if val != '':
        filters.append(('average_rating', val))
    val = '%s-%s' % (kt_utils.strip_whitespace(request.GET.get('fav_avg_rating_min', '')), kt_utils.strip_whitespace(request.GET.get('fav_avg_rating_max', '')))
    if val != '':
        filters.append(('fav_average_rating', val))
    return filters
