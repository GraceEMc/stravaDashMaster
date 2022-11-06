import pandas as pd
import requests
from datetime import datetime
import os
from stravaio import StravaIO
import urllib3
from dateutil.relativedelta import relativedelta
from collections import defaultdict


class StravaAPI:
    """Responsible for querying the Strava API."""


    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
    ):
        
        if client_id is None:
            client_id = os.getenv('STRAVA_CLIENT_ID')
        if client_secret is None:
            client_secret = os.getenv('STRAVA_CLIENT_SECRET')
        if refresh_token is None:
            refresh_token = os.getenv('STRAVA_REFRESH_TOKEN')
            
        auth_url = "https://www.strava.com/oauth/token"
        activites_url = "https://www.strava.com/api/v3/athlete/activities"
    
        payload = {
            'client_id': client_id, 
            'client_secret': client_secret, 
            'refresh_token': refresh_token,
            'grant_type': "refresh_token",
            'f': 'json'
        }
    
        print("Requesting Refresh Token...\n")
        res = requests.post(auth_url, data=payload, verify=False)
        TOKEN = res.json()['access_token']
        print("Access Token = {}\n".format(TOKEN))

    # header = {'Authorization': 'Bearer ' + access_token}
    # param = {'per_page': 200, 'page': 1}
    # my_dataset = requests.get(activites_url, headers=header, params=param).json()

    # print(my_dataset[0]["name"])
    # print(my_dataset[0]["map"]["summary_polyline"])
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    #strava_oauth2(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        if 'client'  not in locals():
            self.stravaclient = StravaIO(access_token=TOKEN)
            
        # with few added data-handling methods
        # athlete = stravaclient.get_logged_in_athlete()

    def get(self,date=(datetime.now() - relativedelta(years=1))) -> pd.DataFrame:
        """Download and tidy Strava data.

        Parameters
        ----------
        data_type : str
            the type of Strava data to download, must be "activities".

        Returns
        -------
        pd.DataFrame
            contains tidy Strava data.
        """

        
        activities = self.stravaclient.get_logged_in_athlete_activities(date)
        df_data = defaultdict(list)

        for activity in activities:
            for k, v in activity.to_dict().items():
                df_data[k].append(v)
        
        activities = pd.DataFrame(df_data)

        
        
        
        activities["elapsed_min"] = round(activities["elapsed_time"] / 60, 2)
        activities["distance_km"] = round(activities["distance"] / 1000, 2)
        activities["speed_mins_per_km"] = round(
            (activities["elapsed_min"] / activities["distance_km"]), 2
        )

        activities["date"] = pd.to_datetime(activities["start_date_local"])

        self.data = activities
        
        return activities
