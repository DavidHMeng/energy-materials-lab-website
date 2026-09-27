# Translation coverage report

Updated: 2026-09-26  
Registry: `_translation/registry.yml`

Status definitions:

- **TRANSLATABLE**: asynchronous academic-English generation when English is blank.
- **MANUAL EN ONLY**: no machine generation; English routes fall back to Chinese until official English is entered.
- **TRANSLATION EXCLUDED**: never sent to a translation provider.

All listed English fields are optional in Pages CMS. Existing manual English always wins.

| Collection | ZH field | EN field | Status | Auto? | Fallback? | Manual override? | Excluded reason | QA |
|---|---|---|---|---:|---:|---:|---|---|
| Homepage Settings | `eyebrow_zh` | `eyebrow_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Homepage Settings | `title_zh` | `title_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Homepage Settings | `text_zh` | `text_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Homepage Settings | `alt_zh` | `alt_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Homepage Settings | `caption_zh` | `caption_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Homepage Settings | `highlights_heading_zh` | `highlights_heading_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Homepage Settings | `events_heading_zh` | `events_heading_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Highlights / News | `title_zh` | `title_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Highlights / News | `summary_zh` | `summary_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Highlights / News | `alt_zh` | `alt_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Events | `title_zh` | `title_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Events | `location_zh` | `location_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Events | `alt_zh` | `alt_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Events | `description_zh` | `description_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Research | `title_zh` | `title_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Research | `alt_zh` | `alt_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Research | `short_intro_zh` | `short_intro_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Publications | `description_zh` | `description_en` | TRANSLATION EXCLUDED | No | No | Yes | Publication content stays in its maintained original language | PASS |
| Team | `name_zh` | `name_en` | MANUAL EN ONLY | No | Yes | Yes | Names must not be guessed or romanized | PASS |
| Team | `position_zh` | `position_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Team | `portrait_alt_zh` | `portrait_alt_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Team | `research_summary_zh` | `research_summary_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Team | `affiliation_zh` | `affiliation_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Team | `profile_summary_zh` | `profile_summary_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Team | `address_zh` | `address_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Team | `research_interests_zh` | `research_interests_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Team | `personal_note_zh` | `personal_note_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Team | `education_zh` | `education_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Team Role Labels | `label_zh` | `label_en` | MANUAL EN ONLY | No | Yes | Yes | Official role wording | PASS |
| Opportunities | `title_zh` | `title_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Opportunities | `content_zh` | `content_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Opportunities | `label_zh` | `label_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Site Settings | `lab_name_zh` | `lab_name_en` | MANUAL EN ONLY | No | Yes | Yes | Official laboratory name | PASS |
| Site Settings | `school_zh` | `school_en` | MANUAL EN ONLY | No | Yes | Yes | Official university name | PASS |
| Site Settings | `college_zh` | `college_en` | MANUAL EN ONLY | No | Yes | Yes | Official school/college name | PASS |
| Site Settings | `address_zh` | `address_en` | TRANSLATABLE | Yes | Yes | Yes | Official English may replace generated text | PASS |
| Site Settings | `copyright_zh` | `copyright_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |
| Site Settings | `description_zh` | `description_en` | TRANSLATABLE | Yes | Yes | Yes | — | PASS |

## Non-bilingual exclusions

Email, URL, ORCID, Google Scholar URL, GitHub URL, dates, IDs, slugs, image paths,
filenames, raw DOI values, chemical formulae, citation metadata and all publication
bibliography fields are not translation candidates.

## QA summary

- 38 CMS bilingual pairs classified; zero unregistered pairs and zero required English fields.
- Auto fields were exercised with absent English, a successful translator, missing credentials and a simulated timeout.
- Manual-only fields never enter machine rules and receive Chinese fallback during the Jekyll build.
- Publication source/citation data never enter machine translation rules.
