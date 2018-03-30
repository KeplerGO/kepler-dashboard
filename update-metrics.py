"""Retrieve Kepler/K2 metrics and write them to `kepler-dashboard.json`."""
import json
import collections
import datetime


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
    metrics['nasakepler_followers_count'] = get_twitter_followers('NASAKepler')
    metrics['followers_count'] = (metrics['keplergo_followers_count'] +
                                  metrics['nasakepler_followers_count'])
    return metrics


def get_planet_metrics():
    """Returns a dict containing Kepler/K2 planet discovery metrics."""
    import pandas as pd
    print('Retrieving planet metrics from NEXSCI...')
    NEXSCI_ENDPOINT = 'http://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI'
    metrics = collections.OrderedDict()
    # Count the number of Kepler candidate planets
    df = pd.read_csv(NEXSCI_ENDPOINT +
                     '?table=cumulative&select=count(*)'
                     '&where=koi_pdisposition+like+%27CANDIDATE%27')
    metrics['kepler_candidates_count'] = int(df['count(*)'][0])
    # Count Kepler confirmed planets
    df = pd.read_csv(NEXSCI_ENDPOINT +
                     '?table=exoplanets&select=count(*)&where=pl_kepflag>0')
    metrics['kepler_confirmed_count'] = int(df['count(*)'][0])
    # Count Kepler confirmed planets with mass estimates
    df = pd.read_csv(NEXSCI_ENDPOINT +
                     '?table=exoplanets&select=count(*)&where=pl_kepflag>0+and+pl_masselim=0')
    metrics['kepler_confirmed_with_mass_count'] = int(df['count(*)'][0])

    # Count K2 candidate planets
    df = pd.read_csv(NEXSCI_ENDPOINT +
                     '?table=k2candidates&select=count(*)'
                     '&where=k2c_disp+like+%27C%25%27+and+k2c_recentflag=1')
    metrics['k2_candidates_count'] = int(df['count(*)'][0])
    # Count K2 confirmed planets
    df = pd.read_csv(NEXSCI_ENDPOINT +
                     '?table=exoplanets&select=count(*)&where=pl_k2flag>0')
    metrics['k2_confirmed_count'] = int(df['count(*)'][0])
    # Count K2 confirmed planets with mass estimates
    df = pd.read_csv(NEXSCI_ENDPOINT +
                     '?table=exoplanets&select=count(*)&where=pl_k2flag>0+and+pl_masselim=0')
    metrics['k2_confirmed_with_mass_count'] = int(df['count(*)'][0])
    # Combined planet counts
    metrics['candidates_count'] = metrics['kepler_candidates_count'] + metrics['k2_candidates_count']
    metrics['confirmed_count'] = metrics['kepler_confirmed_count'] + metrics['k2_confirmed_count']
    return metrics


if __name__ == '__main__':
    metrics = collections.OrderedDict()
    metrics['description'] = ("This file contains metrics which quantify "
                              "the success of NASA's Kepler and K2 missions.")
    metrics['last_update'] = datetime.datetime.now().isoformat()
    metrics['planets'] = get_planet_metrics()
    metrics['publications'] = get_publication_metrics()
    metrics['twitter'] = get_twitter_metrics()
    output_fn = 'kepler-dashboard.json'
    with open(output_fn, 'w') as output:
        print('Writing {}'.format(output_fn))
        json.dump(metrics, output, indent=True)
