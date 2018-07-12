# coding=utf-8

import scraperwiki
import lxml.html
import sqlite3
import re


def cleanup(string):

    # Strip any annoying whitespace
    string = string.strip()

    # Lose any curled apostrophies
    string = string.replace(u'’', '\'')

    return string


PERSON_MAP = {
    '229':  'Q55372604',
}

PARTY_MAP = {
    'Conservative': 'Q9626',
    'Garforth & Swillington Independents': 'Q55465979',
    'Green Party': 'Q9669',
    'Labour': 'Q9630',
    'Liberal Democrats': 'Q9624',
    'Morley Borough Independents': 'Q55465915',
}

WARD_MAP = {
    'Adel and Wharfedale': 'Q55466756',
    'Alwoodley': 'Q2131866',
    'Ardsley and Robin Hood': 'Q55466797',
    'Armley': 'Q55466825',
    'Beeston and Holbeck': 'Q55466755',
    'Bramley and Stanningley': 'Q55466807',
    'Burmantofts and Richmond Hill': 'Q55466805',
    'Calverley and Farsley': 'Q55466776',
    'Chapel Allerton': 'Q55466785',
    'Cross Gates and Whinmoor': 'Q55466803',
    'Farnley and Wortley': 'Q55466762',
    'Garforth and Swillington': 'Q55466783',
    'Gipton and Harehills': 'Q55466757',
    'Guiseley and Rawdon': 'Q55466823',
    'Harewood': 'Q55466789',
    'Headingley and Hyde Park': 'Q55466799',
    'Horsforth': 'Q55466779',
    'Hunslet and Riverside': 'Q55466821',
    'Killingbeck and Seacroft': 'Q55466786',
    'Kippax and Methley': 'Q55466808',
    'Kirkstall': 'Q55466761',
    'Little London and Woodhouse': 'Q55466753',
    'Middleton Park': 'Q6842031',
    'Moortown': 'Q55466778',
    'Morley North': 'Q55466800',
    'Morley South': 'Q55466782',
    'Otley and Yeadon': 'Q55466766',
    'Pudsey': 'Q55466813',
    'Rothwell': 'Q55466765',
    'Roundhay': 'Q2735485',
    'Temple Newsam': 'Q55466781',
    'Weetwood': 'Q55466759',
    'Wetherby': 'Q55466810',
}

BASE_URL = 'https://democracy.leeds.gov.uk/mgMemberIndex.aspx?VW=TABLE&PIC=1&FN='

parsedMembers = []
unreconciledWards = []
unreconciledParties = []
unreconciledPeople = []

print('(i) Scraping from ' + BASE_URL)

# Get the page!
html = scraperwiki.scrape(BASE_URL)
ssRoot = lxml.html.fromstring(html)

rows = ssRoot.cssselect('#mgTable1 tr')

# Skip the header row
for row in rows[1:]:

    memberData = {}

    print row

    nameLink = row.cssselect('a')[0]

    nameUnparsed = nameLink.text.strip()

    nameRegex = re.search('(.+?) (.+)', nameUnparsed)
    memberData['honorific_string'] = nameRegex.group(1)

    memberData['name'] = cleanup(nameRegex.group(2))

    # print('    ' + memberData['name'])

    linkHref = nameLink.attrib['href']

    idRegex = re.search('mgUserInfo\.aspx\?UID=([0-9]+)', linkHref)
    memberData['id'] = idRegex.group(1)

    if memberData['id'] in PERSON_MAP:
        memberData['wikidata_id'] = PERSON_MAP[memberData['id']]
    else:
        unreconciledPeople.append(memberData['name'])

    memberData['url'] = cleanup('https://democracy.leeds.gov.uk/mgUserInfo.aspx?UID=' + memberData['id'])

    partyName = row.cssselect('td')[2].text
    memberData['party'] = partyName

    if partyName in PARTY_MAP:
        memberData['party_id'] = PARTY_MAP[partyName]
    else:
        unreconciledParties.append(partyName)

    wardName = row.cssselect('td')[3].text
    memberData['ward'] = wardName

    if wardName in WARD_MAP:
        memberData['ward_id'] = WARD_MAP[wardName]
    else:
        unreconciledWards.append(wardName)

    print memberData
    parsedMembers.append(memberData)


print('(i) Done.')
print '(i) Counted {} Members in total'.format(len(parsedMembers))
print '<!> {} unreconciled people:'.format(len(unreconciledPeople))
print unreconciledPeople
print '<!> {} unreconciled wards:'.format(len(unreconciledWards))
print unreconciledWards
print '<!> {} unreconciled parties:'.format(len(unreconciledParties))
print unreconciledParties


try:
    scraperwiki.sqlite.execute('DELETE FROM data')
except sqlite3.OperationalError:
    pass
scraperwiki.sqlite.save(
    unique_keys=['id'],
    data=parsedMembers)
