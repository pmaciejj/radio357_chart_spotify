import os
import pandas as pd
from datetime import datetime

from utils import data_path
import spotify_api
from  radio357_charts import radio357_charts_get


### Note
# charts are published ones per week
# spotify data can be downloaded very day (songs/artists popularity and nums of followers does not change very dynn)

# tracks, artist csvs -
#    every rehresh adds new data to files
#    can be refresh only once per day
#    if files get deleted, new will be created


date = datetime.today()
date = datetime.strftime(date,"%Y-%m-%d")

try:
    tracks_ex = pd.read_csv(data_path + "\\tracks.csv",sep = ";")
    artists_ex = pd.read_csv(data_path + "\\artists.csv",sep = ";")
    last_refresh_date = tracks_ex["date"].max()
    csvs_exists = True
except:
    csvs_exists = False
    last_refresh_date = "2000-01-01"
    pass

if date != last_refresh_date:
    radio357_charts_get()

    charts = pd.read_csv(data_path + "\\radio357_charts.csv",delimiter=";")
    tracks = charts[["artist","track"]].drop_duplicates()
    tracks["artist"] = tracks["artist"].str.split("feat.|&",expand=True)[0].str.strip()
    tracks["spotify_data"] = tracks.apply(lambda r: spotify_api.track_info_get(r["artist"],r["track"]),axis=1)

    spotify_data = tracks["spotify_data"].str.split("|",expand=True)
    spotify_data_columns = ["album_name","album_release_date","track_popularity","artist_id"]
    spotify_data.rename(columns=lambda x: spotify_data_columns[x] if isinstance(x,int) else x ,inplace=True)

    tracks = tracks.join(spotify_data)
    tracks.insert(0,"date",date)
    if csvs_exists:
        tracks_all = pd.concat([tracks_ex,tracks])
        tracks_all.to_csv(data_path + "\\tracks.csv",index = False,sep = ";")
    else:
        tracks.to_csv(data_path + "\\tracks.csv",index = False,sep = ";")

    tracks = pd.read_csv(data_path + "\\tracks.csv",sep = ";")

    artists = tracks[["artist","artist_id"]].drop_duplicates()
    artists = artists[artists["artist_id"].notna()]

    artists["spotify_data"] = artists.apply(lambda r:spotify_api.artist_info_get(r["artist_id"] ),axis=1)

    spotify_data = artists["spotify_data"].str.split("|",expand=True)
    spotify_data_columns = ["artist_name","artist_genres","artist_popularity","artist_followers"]
    spotify_data.rename(columns=lambda x: spotify_data_columns[x] if isinstance(x,int) else x ,inplace=True)
    artists = artists.join(spotify_data)
    artists.insert(0,"date",date)
    if csvs_exists:
        artists_all = pd.concat([artists_ex,artists])
        artists_all.to_csv(data_path + "\\artists.csv",index = False,sep = ";")
    else:
        artists.to_csv(data_path + "\\artists.csv",index = False,sep = ";")



