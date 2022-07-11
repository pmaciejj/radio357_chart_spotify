
import os
import requests
import base64
import json
from datetime import datetime
from datetime import timedelta

from utils import *
from utils import log
from utils import remove_forbidden_chars

date = datetime.today()
date = datetime.strftime(date,"%Y%m%d")

spotify_data_path = os.path.join(data_path,"spotify")
if os.path.isdir(spotify_data_path) == False:
    os.mkdir(spotify_data_path)

with open(os.path.join(main_path,"spotify_api.json"),"r") as f:
    config = json.load(f)

client_id = config["clientID"] 
secret = config["secret"]
token = config["token"]
expires = config["expires"]

url = 'https://accounts.spotify.com/api/token'

def auth_string_get():
    s = client_id  + ":" +  secret
    s = s.encode("utf-8")

    s_b64 = base64.b64encode(s)
    return "Basic " + s_b64.decode("utf-8")

def check_token():
    if datetime.strptime(expires,"%Y-%m-%d %H:%M:%S.%f") > datetime.now():
        return True
    return False

def update_config_file(token,expires):
    print("run update_config_file")
    config["token"] = token
    config["expires"] = expires

    with open(os.path.join(main_path,"spotify_api.json"),"w") as f:
        json.dump(config,f,indent=4)


def auth():
    print("run auth")
    auth_string = auth_string_get()
    s = requests.session()

    header={
        "Authorization" : auth_string,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }
    res = s.post(url,data = data, headers=header)
    if res.status_code == 200:
        res = json.loads(res.text)
        global token
        global expires
        token  = res["access_token"]
        expires = str(datetime.now() + timedelta(seconds= int(res["expires_in"])))
        update_config_file(token,expires)
        print("new token gen")



def track_info_get(artist,track):
    if check_token() == False:
        auth()

    url = "https://api.spotify.com/v1/search"
    header = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    }
    param = {
        "q": "artist: " + artist + " track:" + track,
        "type": "track",
        "limit":1
    }

    s = requests.session()
    res = s.get(url, params=param,headers= header)
    if res.status_code == 200:

        #print(res.text)
        with open(spotify_data_path +"\\track " + remove_forbidden_chars(artist)+ "_" + remove_forbidden_chars(track) + " " + date + ".json","w",encoding="utf-8") as f:
            f.write(res.text)

        res = json.loads(res.text)
        try:
            album_name = res["tracks"]["items"][0]["album"]["name"]
        except:
            album_name = ""
            pass
        try:
            album_release_date = res["tracks"]["items"][0]["album"]["release_date"]
        except:
            album_release_date = ""
            pass
        try:
            track_popularity = res["tracks"]["items"][0]["popularity"]
        except:
            track_popularity=""
            pass
        try:
            artist_id =  res["tracks"]["items"][0]["artists"][0]["id"]
        except:
            artist_id = ""
            pass
        # print(album_name)
        # print(album_release_date)
        # print(track_popularity)
        # print(artist_id)
        
        return "|".join(at for at in  [album_name,album_release_date,str(track_popularity),artist_id])
    else:
        log (" ".join([artist, track, res.text]))

def artist_info_get(artist_id):
    if check_token() == False:
        auth()

    url = "https://api.spotify.com/v1/artists/" + artist_id
    header = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    }


    s = requests.session()
    res = s.get(url,headers= header)
   
    if res.status_code == 200:
        res = json.loads(res.text)
        artist_name = res["name"]
        artist_genres = ",".join( g for g in res["genres"])
        artist_popularity = res["popularity"]
        artist_followers = res["followers"]["total"]

        with open(spotify_data_path + "\\artist " + remove_forbidden_chars(artist_name) + " " + date + ".json","w") as f:
            json.dump(res,f,indent=4)
        # print(artist_name)
        # print(artist_genres)
        # print(artist_popularity)
        # print(artist_followers)
        return "|".join(at for at in  [artist_name,artist_genres,str(artist_popularity),str(artist_followers)])
    else:
        log(artist_id + " " + res.text)