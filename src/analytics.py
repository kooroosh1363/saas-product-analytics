from __future__ import annotations

import pandas as pd


def clean_inputs(accounts: pd.DataFrame, deals: pd.DataFrame, users: pd.DataFrame, tracks: pd.DataFrame):
    """Normalize types, remove duplicate keys, and preserve explicit analytical grains."""
    accounts = accounts.drop_duplicates('account_id').copy()
    deals = deals.drop_duplicates('deal_id').copy()
    users = users.drop_duplicates('user_id').copy()
    tracks = tracks.drop_duplicates('event_id').copy()

    for col in ['created_date']:
        if col in deals:
            deals[col] = pd.to_datetime(deals[col], errors='coerce', utc=True)
    for col in ['created_at', 'first_logged_in_at', 'latest_logged_in_at']:
        if col in users:
            users[col] = pd.to_datetime(users[col], errors='coerce', utc=True)
    tracks['event_timestamp'] = pd.to_datetime(tracks['event_timestamp'], errors='coerce', utc=True)
    deals['amount'] = pd.to_numeric(deals['amount'], errors='coerce')
    deals['seats'] = pd.to_numeric(deals['seats'], errors='coerce')
    return accounts, deals, users, tracks


def user_metrics(users: pd.DataFrame, tracks: pd.DataFrame) -> pd.DataFrame:
    """Build one row per user with activation and engagement features."""
    event_agg = tracks.groupby('user_id').agg(
        total_events=('event_id', 'nunique'),
        active_days=('event_timestamp', lambda s: s.dt.date.nunique()),
        first_event=('event_timestamp', 'min'),
        last_event=('event_timestamp', 'max'),
        unique_features=('event_name', 'nunique'),
    ).reset_index()
    out = users.merge(event_agg, on='user_id', how='left')
    for col in ['total_events', 'active_days', 'unique_features']:
        out[col] = out[col].fillna(0).astype(int)
    out['activated'] = out['first_logged_in_at'].notna()
    out['time_to_activation_hours'] = (
        (out['first_logged_in_at'] - out['created_at']).dt.total_seconds() / 3600
    )
    out['engaged_user'] = (out['active_days'] >= 3) & (out['unique_features'] >= 2)
    return out


def feature_adoption(users: pd.DataFrame, tracks: pd.DataFrame) -> pd.DataFrame:
    """Feature reach and usage intensity among activated users."""
    activated = users.loc[users['first_logged_in_at'].notna(), 'user_id'].nunique()
    g = tracks.groupby('event_name').agg(
        users=('user_id', 'nunique'),
        events=('event_id', 'nunique'),
    ).reset_index()
    g['adoption_pct_of_activated'] = (100 * g['users'] / activated).round(2) if activated else 0.0
    g['events_per_adopter'] = (g['events'] / g['users']).round(2)
    return g.sort_values(['users', 'events'], ascending=False)


def monthly_activity(tracks: pd.DataFrame) -> pd.DataFrame:
    """Monthly active users and product event volume."""
    x = tracks.dropna(subset=['event_timestamp']).copy()
    x['month'] = x['event_timestamp'].dt.to_period('M').astype(str)
    return x.groupby('month').agg(
        mau=('user_id', 'nunique'),
        events=('event_id', 'nunique'),
        features_used=('event_name', 'nunique'),
    ).reset_index()


def account_health(accounts: pd.DataFrame, deals: pd.DataFrame, user_m: pd.DataFrame) -> pd.DataFrame:
    """Create account-level adoption and commercial context without row multiplication."""
    user_agg = user_m.groupby('account_id').agg(
        users=('user_id', 'nunique'),
        activated_users=('activated', 'sum'),
        engaged_users=('engaged_user', 'sum'),
        total_events=('total_events', 'sum'),
    ).reset_index()
    deal_agg = deals.groupby('account_id').agg(
        deals=('deal_id', 'nunique'),
        deal_value=('amount', 'sum'),
        licensed_seats=('seats', 'sum'),
    ).reset_index()
    out = accounts.merge(user_agg, on='account_id', how='left').merge(deal_agg, on='account_id', how='left')
    numeric = ['users', 'activated_users', 'engaged_users', 'total_events', 'deals', 'deal_value', 'licensed_seats']
    out[numeric] = out[numeric].fillna(0)
    out['activation_rate_pct'] = (100 * out['activated_users'] / out['users'].replace(0, pd.NA)).astype('Float64').round(2)
    out['engagement_rate_pct'] = (100 * out['engaged_users'] / out['activated_users'].replace(0, pd.NA)).astype('Float64').round(2)
    out['seat_adoption_proxy_pct'] = (100 * out['activated_users'] / out['licensed_seats'].replace(0, pd.NA)).astype('Float64').round(2)
    return out


def retention_by_signup_month(users: pd.DataFrame, tracks: pd.DataFrame) -> pd.DataFrame:
    """First-login cohort retention using active product-event months."""
    cohort = users.loc[users['first_logged_in_at'].notna(), ['user_id', 'first_logged_in_at']].copy()
    cohort['cohort_month'] = cohort['first_logged_in_at'].dt.to_period('M')
    activity = tracks.dropna(subset=['event_timestamp'])[['user_id', 'event_timestamp']].copy()
    activity['activity_month'] = activity['event_timestamp'].dt.to_period('M')
    x = activity.merge(cohort[['user_id', 'cohort_month']], on='user_id', how='inner')
    x = x[x['activity_month'] >= x['cohort_month']]
    x['month_number'] = (
        (x['activity_month'].dt.year - x['cohort_month'].dt.year) * 12
        + x['activity_month'].dt.month - x['cohort_month'].dt.month
    )
    active = x.groupby(['cohort_month', 'month_number'])['user_id'].nunique().rename('active_users').reset_index()
    sizes = cohort.groupby('cohort_month')['user_id'].nunique().rename('cohort_size').reset_index()
    out = active.merge(sizes, on='cohort_month')
    out['retention_pct'] = (100 * out['active_users'] / out['cohort_size']).round(2)
    out['cohort_month'] = out['cohort_month'].astype(str)
    return out
