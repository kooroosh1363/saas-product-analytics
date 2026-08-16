from pathlib import Path
import pandas as pd

from .analytics import clean_inputs, user_metrics, feature_adoption, monthly_activity, account_health, retention_by_signup_month

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
OUT = ROOT / 'outputs'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    accounts = pd.read_csv(RAW / 'accounts_raw.csv')
    deals = pd.read_csv(RAW / 'deals_raw.csv')
    users = pd.read_csv(RAW / 'users_raw.csv')
    tracks = pd.read_csv(RAW / 'tracks_raw.csv')
    accounts, deals, users, tracks = clean_inputs(accounts, deals, users, tracks)

    um = user_metrics(users, tracks)
    fa = feature_adoption(users, tracks)
    ma = monthly_activity(tracks)
    ah = account_health(accounts, deals, um)
    rt = retention_by_signup_month(users, tracks)

    # Never export upstream email/PII-like fields in analytical deliverables.
    um.drop(columns=['email'], errors='ignore').to_csv(OUT / 'user_metrics.csv', index=False)
    fa.to_csv(OUT / 'feature_adoption.csv', index=False)
    ma.to_csv(OUT / 'monthly_activity.csv', index=False)
    ah.to_csv(OUT / 'account_health.csv', index=False)
    rt.to_csv(OUT / 'cohort_retention.csv', index=False)

    executive = pd.DataFrame([{
        'accounts': accounts['account_id'].nunique(),
        'users': users['user_id'].nunique(),
        'activated_users': int(um['activated'].sum()),
        'engaged_users': int(um['engaged_user'].sum()),
        'activation_rate_pct': round(100 * um['activated'].mean(), 2),
        'total_product_events': tracks['event_id'].nunique(),
        'unique_features': tracks['event_name'].nunique(),
    }])
    executive.to_csv(OUT / 'executive_summary.csv', index=False)
    print(executive.to_string(index=False))


if __name__ == '__main__':
    main()
