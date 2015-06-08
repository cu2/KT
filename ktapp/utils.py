import re


def bbcode_to_html(value):
    value = re.sub('\[link=([^\]]*)\]', '<a href="\\1">', value)
    value = value.replace('[/link]', '</a>')
    value = value.replace('[b]', '<b>')
    value = value.replace('[/b]', '</b>')
    value = value.replace('[i]', '<i>')
    value = value.replace('[/i]', '</i>')
    value = value.replace('[u]', '<u>')
    value = value.replace('[/u]', '</u>')
    value = value.replace('[del]', '<del>')
    value = value.replace('[/del]', '</del>')
    value = value.replace('[spoiler]', '<span class="spoiler">')
    value = value.replace('[/spoiler]', '</span>')
    value = re.sub('\[img\]([^\]]*)\[/img\]', '<img src="\\1" class="comment_img" />', value)
    return value


def html_to_bbcode(value):
    value = re.sub('<a href="([^"]*)">', '[link=\\1]', value)
    value = value.replace('</a>', '[/link]')
    value = value.replace('<b>', '[b]')
    value = value.replace('</b>', '[/b]')
    value = value.replace('<i>', '[i]')
    value = value.replace('</i>', '[/i]')
    value = value.replace('<u>', '[u]')
    value = value.replace('</u>', '[/u]')
    value = value.replace('<del>', '[del]')
    value = value.replace('</del>', '[/del]')
    value = value.replace('<div id="SPOIL1">', '[spoiler]')
    value = value.replace('</div>', '[/spoiler]')
    value = re.sub('<img src="([^"]*)">', '[img]\\1[/img]', value)
    return value