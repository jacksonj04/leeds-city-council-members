# coding=utf-8

import scraperwiki
import lxml.html
import lxml.etree as etree
import sqlite3
import re
from datetime import datetime as dt

import lcc_id_map


CURRENT_MEMBERS_URL = 'https://democracy.leeds.gov.uk/mgMemberIndex.aspx?VW=TABLE&PIC=1&FN='


def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


def parse_date(date):

    parts = date.split('/')

    if len(parts)== 3:
        return parts[2] + '-' + parts[1] + '-' + parts[0]


def cleanup(string):

    # Strip any annoying whitespace
    string = string.strip()

    # Lose any curled apostrophies
    string = string.replace(u'’', '\'')

    return string


def get_content_of_label(page, label):

    element = page.xpath('//span[contains(text(),\'' + label + ':\')]/parent::p')

    if element:
        return element[0].text_content().replace(label + ':', '').strip()
    else:
        return None

def scrape_member_page(id):

    page_url = cleanup('https://democracy.leeds.gov.uk/mgUserInfo.aspx?UID=' + str(id))
    print('    Scraping ' + page_url)

    html = scraperwiki.scrape(page_url)
    pageRoot = lxml.html.fromstring(html)

    memberSessions = []
    memberData = {}

    memberData['lcc_id'] = str(id)
    memberData['url'] = page_url

    nameTitle = pageRoot.cssselect('#modgov h1')[0]

    nameUnparsed = nameTitle.text.strip()

    nameRegex = re.search('(.+?) (.+)', nameUnparsed)
    memberData['honorific_string'] = nameRegex.group(1)

    memberData['name'] = cleanup(nameRegex.group(2))

    print('        Name: ' + memberData['name'])

    party = get_content_of_label(pageRoot, 'Party')
    ward = get_content_of_label(pageRoot, 'Ward')

    # Check to see if the person is reconciled or not
    if memberData['lcc_id'] in lcc_id_map.people_ids:
        memberData['wikidata_id'] = lcc_id_map.people_ids[memberData['lcc_id']]
    else:
        unreconciledPeople.append(memberData['name'] + ' (' + memberData['lcc_id'] + ')')

    # Check to see if the party is reconciled or not
    if party in lcc_id_map.party_names:
        party_id = lcc_id_map.party_names[party]
    elif party is not None:
        unreconciledParties.append(party)
        party_id = None

    # Check to see if the ward is reconciled or not
    if ward in lcc_id_map.ward_names:
        ward_id = lcc_id_map.ward_names[ward]
    elif ward is not None:
        unreconciledPeople.append(ward)
        ward_id = None

    terms = pageRoot.xpath('//h2[contains(text(),\'Terms of Office\')]/following::ul[1]/li')

    # Sometimes this is "Term of Office"
    if not terms:
        terms = pageRoot.xpath('//h2[contains(text(),\'Term of Office\')]/following::ul[1]/li')

    if id in current_member_ids:
        needs_current_term = True
        has_current_term = False
    else:
        needs_current_term = False
        has_current_term = True

    for term in terms:

        # Explode it into two bits
        parts = term.text.split('-')

        if len(parts) == 2:
            startRaw = parse_date(parts[0].strip())
            start = startRaw + 'T00:00:00Z'
            endRaw = parse_date(parts[1].strip())
            if endRaw:
                end = endRaw + 'T00:00:00Z'
            else:
                end = None

            sessionDetails = {
                'id': id + '-' + start,
                'start': start
            }

            end_date = dt.strptime(endRaw, "%Y-%m-%d")
            if end_date >= dt.now():
                print('                Found current term ' + term.text + '.')
                has_current_term = True
                sessionDetails['current'] = True
                sessionDetails['end'] = None
                sessionDetails['party'] = party
                sessionDetails['party_id'] = party_id
                sessionDetails['ward'] = ward
                sessionDetails['ward_id'] = ward_id
            else:
                print('                Found non-current term ' + term.text + '.')
                sessionDetails['current'] = False
                sessionDetails['end'] = end


            memberSessions.append(merge_two_dicts(memberData, sessionDetails))

            print('                Added term ' + term.text + '.')

        else:
            print('                Skipped "' + term.text + '", does not appear to be a date range.')

    # Need a current term but don't yet have one? Inject a fake one!
    if needs_current_term == True and has_current_term == False:
        sessionDetails = {
            'id': id + '-current',
            'current': True,
        }
        memberSessions.append(merge_two_dicts(memberData, sessionDetails))

    return memberSessions


parsedMemberships = []
unreconciledWards = []
unreconciledParties = []
unreconciledPeople = []

print('(i) Scraping from ' + CURRENT_MEMBERS_URL)

# Get the page!
html = scraperwiki.scrape(CURRENT_MEMBERS_URL)
ssRoot = lxml.html.fromstring(html)

rows = ssRoot.cssselect('#mgTable1 tr')

current_member_ids = []

# Skip the header row
for row in rows[1:]:

    nameLink = row.cssselect('a')[0]
    linkHref = nameLink.attrib['href']

    idRegex = re.search('mgUserInfo\.aspx\?UID=([0-9]+)', linkHref)

    current_member_ids.append(idRegex.group(1))

print('(i) Found {} current members'.format(len(current_member_ids)))

ids_to_scrape = set(current_member_ids + list(lcc_id_map.people_ids))

print('(i) Scraping {} members in total'.format(len(ids_to_scrape)))

for id in ids_to_scrape:
    parsedMemberships = parsedMemberships + scrape_member_page(id)

    nameLink = row.cssselect('a')[0]


print('(i) Done.')
print('(i) Counted {} memberships in total'.format(len(parsedMemberships)))
print('<!> {} unreconciled people:'.format(len(unreconciledPeople)))
print(unreconciledPeople)
print('<!> {} unreconciled wards:'.format(len(unreconciledWards)))
print(unreconciledWards)
print('<!> {} unreconciled parties:'.format(len(unreconciledParties)))
print(unreconciledParties)


try:
    scraperwiki.sqlite.execute('DELETE FROM data')
except sqlite3.OperationalError:
    pass
scraperwiki.sqlite.save(
    unique_keys=['id'],
    data=parsedMemberships)
