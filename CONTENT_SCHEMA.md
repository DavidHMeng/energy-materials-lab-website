# Content schema

Pages CMS reads `.pages.yml`, which is authoritative for editor-visible fields.

## Shared conventions

- `*_en` and `*_zh` are independent formal content, never machine translations.
- `display` controls whether a record is rendered.
- `order` / `display_order` is ascending; lower values appear first.
- Images use repository-root public paths such as `/images/uploads/file.webp`.
- Dates use ISO `YYYY-MM-DD` strings.

## Publications

`_data/sources.yaml` is the only manually maintained publication source. Each `id` must
be `doi:<DOI>`. `_cite/cite.py` resolves metadata into `_data/citations.yaml`. Titles,
authors, journal names, and dates remain in the publication's original language.
`member_ids` connects citations to team profiles; Research records reference the same
work through `doi_list`.

## Opportunity active override

`active_override` is intentionally a three-state string rather than a boolean:

- `auto`: show from `opening_date` through `closing_date`; missing bounds are open.
- `force_show`: show regardless of dates.
- `force_hide`: hide regardless of dates.

`display: false` is a global editorial kill switch and always hides the record. This
prevents an unset value from being confused with explicit `false`.

## Team state

Both `active: true` and `display: true` are required for list/profile visibility.
Leaving members are retained in Git history or source with either field false; there is
no Alumni route.

## Collection summaries

- `_research`: bilingual title, graphical abstract and alt text, short introduction,
  DOI list, display, order.
- `_news`: one of Publication, Award, Member, Academic Achievement, Funding,
  Announcement; bilingual title/summary, date, optional image/link.
- `_events`: Academic or Group type plus category, bilingual title/location/description,
  dates, cover, gallery, external link.
- `_members`: fixed role, bilingual profile fields, contact/research links, state flags.
- `_opportunities`: bilingual title/body, category, links, date window, tri-state active
  override, display order.
