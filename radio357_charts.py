import os
from bs4 import BeautifulSoup
import requests
import csv


from utils import data_path

#main_path = os.path.abspath(__file__)
#main_path = os.path.dirname(main_path)
def radio357_charts_get():
    charts357_path = os.path.join(data_path,"357chart_html")

    if not os.path.isdir(charts357_path):
        os.mkdir(charts357_path)
        i=1
    elif len(os.listdir(charts357_path)) == 0:
        i=1
    else:
        files_list =  os.listdir(charts357_path)
        i = max([int(f.split("_")[1].replace(".html","")) for f in files_list]) + 1


    url_p1 = r"https://wyniki.radio357.pl/lista/"
    url_p2 = r"?ret=https%3A%2F%2Flista.radio357.pl" 


    res_status_code = 0

    with requests.session() as s:
        while res_status_code <=200:
            url = url_p1 + str(i) + url_p2
            res = s.get(url)
            res_status_code = res.status_code
            if res_status_code == 200:
                with open(charts357_path + "\\chart_" + str(i) + ".html","w",encoding="utf-8") as f:
                    f.write(res.text)
            i = i+1

    charts_data = []
    for f in os.listdir(charts357_path):
        chart_no = f.split("_")[1].replace(".html","")
        with open(os.path.join(charts357_path,f),"r",encoding="utf-8") as f:
            chart_html = f.read()

        soup = BeautifulSoup(chart_html, "html.parser")
        chart_date = soup.find("span", {"id": "chart-published_at"}).text

        artists = [ art.text for art in soup.findAll("span", class_ = "artist")]
        positions = [pos.text for pos in  soup.findAll("div",class_ = "position")]
        artists_track = [ar.text for ar in  soup.find_all("div",class_= "description")]

        chart = list(zip(positions,artists,artists_track))
        chart = [[chart_no,chart_date,z[0],z[1].strip(),z[2].replace(z[1],"").strip()]  for z in chart ]
        for pos in chart:
            charts_data.append(pos)

    with open(os.path.join(data_path,"radio357_charts.csv"),"w",encoding="utf-8",newline="") as f:
        csv_writer = csv.writer(f,delimiter=";")
        csv_writer.writerow(["chart_no","chart_date","position","artist","track"])
        csv_writer.writerows(charts_data)
        