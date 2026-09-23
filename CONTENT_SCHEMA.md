# Content schema

Pages CMS reads `.pages.yml`, which is authoritative for editor-visible fields.

## Shared conventions

- `*_en` and `*_zh` are independent formal content, never machine translations.
- `display` controls whether a record is rendered.
- `order` / `display_order` is ascending; lower values appear first.
- Images use repository-root public paths such as `/images/uploads/file.webp`.
- Dates use ISO `YYYY-MM-DD` strings.
- Site-wide descriptions are bilingual (`description_en` / `description_zh`) and are
  used as the fallback for member profiles and other pages without a page description.

## Publications

`_data/sources.yaml` is the only manually maintained publication source. Each `id` must
be `doi:<DOI>`. `_cite/cite.py` resolves metadata into `_data/citations.yaml`. Titles,
authors, journal names, and dates remain in the publication's original language.
`member_ids` connects citations to team profiles; Research records reference the same
work through `doi_list`.

The checked-in citation seed must use real, verified bibliographic metadata. Placeholder
members must not be assigned as authors of a real DOI merely to demonstrate linkage.

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

Team category IDs and bilingual display labels are maintained in
`_data/team_roles.yaml`. Pages CMS exposes that file as **Team Role Labels**, so a
maintainer can add Postdoctoral Researchers, Visiting Students, or a future category
without editing a template. A member's `role` must match one of those stable IDs.

Member cards use compact circular portraits and a two-line research summary. Profiles
show Email and optional academic links, Research Interests, Education, and the optional
plain-text `personal_note_en` / `personal_note_zh`. Biography, phone/office display, and
member-specific publication lists are intentionally absent.

## Homepage introduction

`_data/homepage.yaml` contains an `introduction` object rendered above Highlights. Its
bilingual section label, slogan, and short introduction are followed by a restrained
carousel. Each slide has an image, localized alt text, optional localized caption,
display order, and one of two editorial types:

- `graphical-abstract`: A - Graphical Abstract
- `lab-photo`: B - Lab / Group Photo

The type is maintenance metadata and a small visual label, not a separate page layout.
Images use `object-fit: contain` so scientific annotations are not cropped. Autoplay is
limited to 5–12 seconds, pauses during hover/focus, supports touch swiping and manual
controls, and is disabled when the visitor requests reduced motion.

## Collection summaries

- `_research`: bilingual title, graphical abstract and alt text, short introduction,
  DOI list, display, order.
- `_news`: one of Publication, Award, Member, Academic Achievement, Funding,
  Announcement; bilingual title/summary, date, optional image/link.
- `_events`: Academic or Group type plus category, bilingual title/location/description,
  dates, cover, gallery, external link.
- `_members`: role ID, bilingual profile fields, personal note, email/academic links,
  and state flags.
- `_opportunities`: bilingual title/body, category, links, date window, tri-state active
  override, display order.

## CMS round-trip evidence

`_news/2026-09-15-placeholder-publication.md` was edited through the hosted CMS on
2026-09-23. Commit `2c85add` passed CI, deployed, and rendered distinct validation
markers in both EN and ZH. Revert commit `4205075` restored the original values; its CI
and deployment passed and both language routes were verified clean.
