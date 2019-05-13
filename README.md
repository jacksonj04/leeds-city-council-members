# Leeds City Council Members Scraper

A scraper which looks at the [table of councillors on the Leeds City Council website](https://democracy.leeds.gov.uk/mgMemberIndex.aspx?VW=TABLE&PIC=1&FN=), then at each individual councillor's page in turn to figure out their elected terms.

This scraper [runs on Morph](https://morph.io/jacksonj04/leeds-city-council-members) on a daily basis.

## Why?

The data is used to inform two comparisons with the data in Wikidata, with the aim of keeping Wikidata up to date. These are:

* [A comparison of all _current_ councillors](https://www.wikidata.org/wiki/User:Jacksonj04/Leeds/Prompt)
* [A comparison of _all_ councillor memberships](https://www.wikidata.org/wiki/User:Jacksonj04/Leeds/Prompt/All)

In theory, neither of these pages should highlight any differences.

## Mapping IDs

Leeds City Council IDs need mapping to Wikidata IDs - this is done in [`lcc_id_map.py`](https://github.com/jacksonj04/leeds-city-council-members/blob/master/lcc_id_map.py). Missing IDs are flagged at the end of a scraper run.

All IDs in this list are scraped, even if they are not current councillors. This lets us keep a historic comparison.
