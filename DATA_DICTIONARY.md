# Data Dictionary

DA-05 uses four upstream entities from the Lightdash SaaS Demo dataset.

## `accounts_raw.csv` — account grain

| Field | Meaning |
|---|---|
| `account_id` | Unique company/account identifier |
| `account_name` | Organization name |
| `industry` | Business industry |
| `segment` | Account size segment such as SMB, Midmarket, Enterprise |

## `deals_raw.csv` — deal grain

| Field | Meaning |
|---|---|
| `deal_id` | Unique deal identifier |
| `account_id` | Account foreign key |
| `stage` | Deal stage/outcome |
| `plan` | SaaS plan associated with the deal |
| `seats` | Licensed seats |
| `amount` | Deal value |
| `created_date` | Deal creation timestamp |

## `users_raw.csv` — user grain

| Field | Meaning |
|---|---|
| `user_id` | Unique user identifier |
| `account_id` | Account foreign key |
| `email` | User email in upstream demo data; excluded from analytical outputs |
| `job_title` | User role/title |
| `is_marketing_opted_in` | Marketing preference flag |
| `created_at` | User creation timestamp |
| `first_logged_in_at` | First observed login |
| `latest_logged_in_at` | Most recent observed login |

## `tracks_raw.csv` — event grain

| Field | Meaning |
|---|---|
| `user_id` | User foreign key |
| `event_id` | Unique product event identifier |
| `event_name` | Product action/event type |
| `event_timestamp` | Event timestamp |

Examples documented upstream include `login_successful`, `report_generated`, `file_downloaded`, `workspace_created`, `api_call_made`, and `integration_failed`.

## Analytical grains

The project deliberately keeps grain explicit:

- **event grain** for feature adoption and activity trends;
- **user grain** for activation and engagement;
- **account grain** for B2B SaaS product health and plan/segment comparisons.

Metrics must not join deal, user, and event tables naively because one-to-many relationships can multiply rows and inflate counts or revenue.
