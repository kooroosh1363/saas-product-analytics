import pandas as pd

from src.analytics import clean_inputs, user_metrics, feature_adoption, account_health


def sample_data():
    accounts = pd.DataFrame({'account_id':['a1'], 'account_name':['Acme'], 'industry':['Tech'], 'segment':['SMB']})
    deals = pd.DataFrame({'deal_id':['d1'], 'account_id':['a1'], 'stage':['Won'], 'plan':['Pro'], 'seats':[5], 'amount':[1000], 'created_date':['2025-01-01']})
    users = pd.DataFrame({
        'user_id':['u1','u2'], 'account_id':['a1','a1'], 'email':['a@x.com','b@x.com'], 'job_title':['Analyst','Manager'],
        'is_marketing_opted_in':[1,0], 'created_at':['2025-01-01','2025-01-01'],
        'first_logged_in_at':['2025-01-02', None], 'latest_logged_in_at':['2025-01-10', None]
    })
    tracks = pd.DataFrame({
        'user_id':['u1','u1','u1'], 'event_id':['e1','e2','e3'],
        'event_name':['login_successful','report_generated','report_generated'],
        'event_timestamp':['2025-01-02','2025-01-03','2025-01-05']
    })
    return clean_inputs(accounts, deals, users, tracks)


def test_non_activated_users_are_preserved():
    _, _, users, tracks = sample_data()
    m = user_metrics(users, tracks)
    assert len(m) == 2
    assert m['activated'].sum() == 1
    assert m.loc[m.user_id == 'u2', 'total_events'].iloc[0] == 0


def test_feature_adoption_denominator_is_activated_users():
    _, _, users, tracks = sample_data()
    f = feature_adoption(users, tracks)
    report = f.loc[f.event_name == 'report_generated'].iloc[0]
    assert report.users == 1
    assert report.adoption_pct_of_activated == 100.0


def test_account_join_does_not_multiply_deal_value():
    accounts, deals, users, tracks = sample_data()
    m = user_metrics(users, tracks)
    a = account_health(accounts, deals, m)
    assert a.loc[0, 'deal_value'] == 1000
    assert a.loc[0, 'users'] == 2
