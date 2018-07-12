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
    '106': 'Q55469268',
    '107': 'Q32066575',
    '109': 'Q55469119',
    '111': 'Q55469097',
    '114': 'Q55469185',
    '181': 'Q55469116',
    '184': 'Q55469085',
    '185': 'Q55469121',
    '192': 'Q55469358',
    '197': 'Q55469136',
    '198': 'Q55469195',
    '199': 'Q55469151',
    '201': 'Q55469096',
    '204': 'Q55068719',
    '206': 'Q55469172',
    '214': 'Q55469216',
    '220': 'Q55469177',
    '221': 'Q55469217',
    '222': 'Q55469279',
    '229': 'Q55372604',
    '230': 'Q55469264',
    '234': 'Q55469143',
    '236': 'Q55469218',
    '239': 'Q55469138',
    '241': 'Q55469210',
    '242': 'Q55469223',
    '244': 'Q55469171',
    '253': 'Q55469224',
    '256': 'Q55469228',
    '260': 'Q55469236',
    '269': 'Q55469239',
    '466': 'Q55469132',
    '1356': 'Q55469191',
    '1357': 'Q55469156',
    '1358': 'Q55469134',
    '1363': 'Q55469204',
    '1852': 'Q55469259',
    '2263': 'Q55469184',
    '2285': 'Q55469173',
    '2288': 'Q55469179',
    '2290': 'Q55469174',
    '2291': 'Q55469221',
    '2301': 'Q55469205',
    '2302': 'Q55469242',
    '2304': 'Q55469080',
    '2627': 'Q55469197',
    '2628': 'Q55469123',
    '2629': 'Q55469111',
    '2631': 'Q55469277',
    '2632': 'Q55469133',
    '2633': 'Q55469125',
    '2634': 'Q55469131',
    '4563': 'Q55469176',
    '4568': 'Q55469180',
    '4569': 'Q338032',
    '4576': 'Q55469113',
    '4577': 'Q55469206',
    '4578': 'Q55469091',
    '6003': 'Q55469150',
    '6006': 'Q55469235',
    '6007': 'Q55469241',
    '6008': 'Q55469255',
    '6009': 'Q55469263',
    '6339': 'Q55469190',
    '6340': 'Q55469189',
    '6341': 'Q55469088',
    '6660': 'Q55469154',
    '6661': 'Q55469090',
    '6662': 'Q55469237',
    '6663': 'Q55469262',
    '6667': 'Q55469256',
    '6668': 'Q55469148',
    '7105': 'Q55469108',
    '7106': 'Q55469247',
    '7107': 'Q55469192',
    '7108': 'Q55469199',
    '7109': 'Q55469188',
    '7110': 'Q55469245',
    '7111': 'Q55469187',
    '7112': 'Q55469167',
    '7113': 'Q55469278',
    '7114': 'Q55469158',
    '7115': 'Q55469203',
    '7116': 'Q55469186',
    '7117': 'Q55469152',
    '7118': 'Q55469084',
    '7119': 'Q55469243',
    '7120': 'Q55469118',
    '7121': 'Q55469215',
    '7122': 'Q55469160',
    '7123': 'Q55469222',
    '7124': 'Q55469149',
    '7125': 'Q55469254',
    '7126': 'Q55469261',
    '7127': 'Q55469282',
    '7128': 'Q55469141',
    '7129': 'Q55469142',
    '7130': 'Q55469196',
    '7131': 'Q55469094',
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
