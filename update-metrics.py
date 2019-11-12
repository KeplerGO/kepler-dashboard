"""Retrieve Kepler/K2 metrics and write them to `kepler-dashboard.json`."""
import json
import collections
import datetime
import numpy as np
import pandas as pd
from urllib.request import urlopen

NEXSCI_ENDPOINT = 'http://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI'


def get_publication_metrics():
    """Returns a dict containing Kepler/K2 literature metrics."""
    import kpub
    print('Retrieving publication metrics...')
    return kpub.PublicationDB().get_metrics()


def get_twitter_followers(username):
    """Returns the number of followers of a Twitter username."""
    from bs4 import BeautifulSoup
    import requests
    url = 'https://www.twitter.com/' + username
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml")
    f = soup.find('li', class_="ProfileNav-item--followers")
    title = f.find('a')['title']
    return int(title.split(' ')[0].replace(',', ''))


def get_twitter_metrics():
    """Returns a dict containing Kepler/K2 Twitter metrics."""
    print('Retrieving social media metrics from Twitter...')
    metrics = collections.OrderedDict()
    metrics['keplergo_followers_count'] = get_twitter_followers('KeplerGO')
    metrics['followers_count'] = (metrics['keplergo_followers_count'])
    return metrics


def get_lightkurve_metrics():
    print('Retrieving lightkurve metrics...')
    GITHUB_API = "https://api.github.com/repos/keplergo/lightkurve"
    js = json.loads(urlopen(GITHUB_API).read())
    metrics = collections.OrderedDict()
    metrics['forks_count'] = js['forks_count']
    metrics['watchers_count'] = js['watchers_count']
    metrics['stargazers_count'] = js['stargazers_count']
    metrics['open_issues_count'] = js['open_issues_count']
    metrics['subscribers_count'] = js['subscribers_count']
    return metrics


def get_composite_planet_table():
    """Returns a merge of the NExScI's confirmed and composite planet tables."""
    df_exoplanets = pd.read_csv(NEXSCI_ENDPOINT + '?table=exoplanets&select=*')
    df_composite = pd.read_csv(NEXSCI_ENDPOINT + '?table=compositepars&select=*')
    df = pd.merge(df_exoplanets, df_composite, left_on='pl_name', right_on='fpl_name')
    # Sanity checks
    assert len(df_exoplanets) == len(df_composite)
    assert len(df) == len(df_exoplanets)  # All rows should match
    return df


def get_planet_metrics():
    """Returns a dict containing Kepler/K2 planet discovery metrics."""
    print('Retrieving planet metrics from NEXSCI...')
    df = get_composite_planet_table()
    df.to_csv('data/nexsci-composite-planet-table.csv')
    df.to_hdf('data/nexsci-composite-planet-table.h5', 'planets', mode='w')

    is_kepler = df['pl_facility'] == 'Kepler'
    is_k2 = df['pl_facility'] == 'K2'
    is_earth_size = df['fpl_rade'] < 1.25
    is_super_earth_size = (df['fpl_rade'] >= 1.25) & (df['fpl_rade'] < 2.0)
    is_neptune_size = (df['fpl_rade'] >= 2.0) & (df['fpl_rade'] < 6.0)
    is_jupiter_size = (df['fpl_rade'] >= 6.0) & (df['fpl_rade'] < 15.0)
    is_larger_size = df['fpl_rade'] >= 15.0
    has_mass = (df['fpl_bmassprov'] == 'Mass') & (df['fpl_bmasselim'] != 1)
    has_mass_10percent = has_mass & (((df['fpl_bmasseerr1'] - df['fpl_bmasseerr2']) / df['fpl_bmasse']) < 0.2)
    has_radius_10percent = (((df['fpl_radeerr1'] - df['fpl_radeerr2']) / df['fpl_rade']) < 0.2)

    metrics = collections.OrderedDict()
    metrics['kepler_confirmed_count'] = is_kepler.sum()
    metrics['kepler_confirmed_with_mass_count'] = (is_kepler & has_mass).sum()
    metrics['kepler_confirmed_with_mass_10percent_count'] = (is_kepler & has_mass_10percent).sum()
    metrics['kepler_confirmed_with_radius_10percent_count'] = (is_kepler & has_radius_10percent).sum()
    metrics['kepler_confirmed_with_mass_radius_10percent_count'] = (is_kepler & has_mass_10percent & has_radius_10percent).sum()
    metrics['kepler_earth_size_count'] = (is_kepler & is_earth_size).sum()
    metrics['kepler_super_earth_size_count'] = (is_kepler & is_super_earth_size).sum()
    metrics['kepler_neptune_size_count'] = (is_kepler & is_neptune_size).sum()
    metrics['kepler_jupiter_size_count'] = (is_kepler & is_jupiter_size).sum()
    metrics['kepler_larger_size_count'] = (is_kepler & is_larger_size).sum()
    metrics['k2_confirmed_count'] = is_k2.sum()
    metrics['k2_confirmed_with_mass_count'] = (is_k2 & has_mass).sum()
    metrics['k2_confirmed_with_mass_10percent_count'] = (is_k2 & has_mass_10percent).sum()
    metrics['k2_confirmed_with_radius_10percent_count'] = (is_k2 & has_radius_10percent).sum()
    metrics['k2_confirmed_with_mass_radius_10percent_count'] = (is_k2 & has_mass_10percent & has_radius_10percent).sum()
    metrics['k2_earth_size_count'] = (is_k2 & is_earth_size).sum()
    metrics['k2_super_earth_size_count'] = (is_k2 & is_super_earth_size).sum()
    metrics['k2_neptune_size_count'] = (is_k2 & is_neptune_size).sum()
    metrics['k2_jupiter_size_count'] = (is_k2 & is_jupiter_size).sum()
    metrics['k2_larger_size_count'] = (is_k2 & is_larger_size).sum()

    # Count the number of Kepler candidate planets
    df = pd.read_csv(NEXSCI_ENDPOINT + '?table=cumulative&select=count(*)'
                     '&where=koi_disposition+like+%27CANDIDATE%27')
    metrics['kepler_candidates_count'] = int(df['count(*)'][0])

    # Count K2 candidate planets
    df = pd.read_csv(NEXSCI_ENDPOINT + '?table=k2candidates&select=count(*)'
                     '&where=k2c_disp+like+%27CAN%25%27+and+k2c_recentflag=1')
    metrics['k2_candidates_count'] = int(df['count(*)'][0])

    # Combined planet counts
    for name in ['candidates', 'confirmed', 'confirmed_with_mass', 'earth_size',
                 'super_earth_size', 'neptune_size', 'jupiter_size', 'larger_size']:
        metrics[name + '_count'] = metrics['kepler_' + name + '_count'] + \
                                   metrics['k2_' + name + '_count']

    return metrics


def default(o):
    """Circumvents an issue in Python 3 which prevents np.int64 from being
    serialized to JSON."""
    if isinstance(o, np.int64):
        return int(o)
    raise TypeError


if __name__ == '__main__':
    metrics = collections.OrderedDict()
    metrics['description'] = ("This file contains metrics which quantify "
                              "the success of NASA's Kepler and K2 missions.")
    metrics['last_update'] = datetime.datetime.now().isoformat()
    metrics['planets'] = get_planet_metrics()
    metrics['publications'] = get_publication_metrics()
    metrics['twitter'] = get_twitter_metrics()
    metrics['lightkurve'] = get_lightkurve_metrics()
    output_fn = 'kepler-dashboard.json'
    with open(output_fn, 'w') as output:
        print('Writing {}'.format(output_fn))
        json.dump(metrics, output, indent=True, default=default)
