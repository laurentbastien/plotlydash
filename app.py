import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, Event, State
from youtube_videos import youtube_search
from youtube_videos import geo_query
import json
import requests
import pandas as pd
import visdcc

def first_go():
  searchterm = "global warming"
  result = youtube_search(searchterm)

  just_json = result[1]
  just_json[1]

  url1 = "https://www.googleapis.com/youtube/v3/search?part=snippet&relatedToVideoId="
  url2 = "&type=video&key="

  myvideoids = []
  myvideotitles = []
  myrange = 3
  for i in range(myrange):
      myvideotitles.append(just_json[i]["snippet"]["title"])
      myvideoids.append(just_json[i]["id"]["videoId"])

  source,target,videotitles = youtube_spider(myvideoids,url1,url2)
  source2,target2,videotitles2 = youtube_spider(target,url1,url2)
  newsource = convertToNumber(source)
  newsource2 = convertToNumber(source2)
  newtarget = convertToNumber(target)
  newtarget2 = convertToNumber(target2)

  nodes=[]
  data = {}
  for i, b in zip(videotitles+videotitles2,newsource+newsource2):
    nodes.append(dict(id=b,label=i))
  nodes = [i for n, i in enumerate(nodes) if i not in nodes[n + 1:]]
  data["nodes"] = nodes

  targetids = []
  for a, b in zip(newsource+newsource2,newtarget+newtarget2):
    targetids.append(str(a)+"-"+str(b))

  targets=[]
  for a,b,c in zip(targetids,newsource+newsource2,newtarget+newtarget2):
    new_dict = dict(id=a,key=b,to=c)
    new_dict["from"] = new_dict.pop("key")
    targets.append(new_dict)
  targets = [i for n, i in enumerate(targets) if i not in targets[n + 1:]]
  data["edges"] = targets

  return data

def youtube_spider(myvideoids,url1,url2):
  source = []
  target = []
  videotitles = []
  for myid in myvideoids:
    r = requests.get(url1+myid+url2)
    myjson = r.json()
    myrange = len(myjson["items"])
    target.append(myjson['items'][0]["id"]["videoId"])
    videotitles.append(myjson["items"][0]["snippet"]["title"])
    source.append(myid)

  return source,target,videotitles

def convertToNumber (s):
  newsource = []
  for row in s:
    newsource.append(int.from_bytes(row.encode(), 'little'))

  return newsource


data = first_go()
app = dash.Dash()

app.layout = html.Div([  html.Div(
        [
            dcc.Markdown(
                '''
                ### A Look Inside YouTube's Recommendation Algorithm
                Enter a search term to see how videos are linked to each other.
                '''.replace('  ', ''),
                className='eight columns offset-by-two'
            )
        ],
        className='row',
        style={'text-align': 'center', 'margin-bottom': '15px'}
    ),dcc.Input(id='my-id', value='Global warming', type='text'),
    html.Div(id='my-div',style={'text-align': 'center', 'margin-bottom': '15px'}),
      visdcc.Network(id='net',
                     data=data,
                     options=dict(height='500px', width='90%')),
      dcc.RadioItems(id='color',
                     options=[{'label': 'Red'  , 'value': '#ff0000'},
                              {'label': 'Green', 'value': '#00ff00'},
                              {'label': 'Blue' , 'value': '#0000ff'}],
                     value='Red')
,])

@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='my-id', component_property='value')]
)
def update_output_div(input_value):
  searchterm = input_value

  result = youtube_search(searchterm)

  just_json = result[1]
  just_json[1]

  url1 = "https://www.googleapis.com/youtube/v3/search?part=snippet&relatedToVideoId="
  url2 = "&type=video&key="

  myvideoids = []
  myvideotitles = []
  myrange = 3
  for i in range(myrange):
      myvideotitles.append(just_json[i]["snippet"]["title"])
      myvideoids.append(just_json[i]["id"]["videoId"])

  source,target,videotitles = youtube_spider(myvideoids,url1,url2)
  source2,target2,videotitles2 = youtube_spider(target,url1,url2)
  newsource = convertToNumber(source)
  newsource2 = convertToNumber(source2)
  newtarget = convertToNumber(target)
  newtarget2 = convertToNumber(target2)

  nodes=[]
  data = {}
  for i, b in zip(videotitles+videotitles2,newsource+newsource2):
    nodes.append(dict(id=b,label=i))
  nodes = [i for n, i in enumerate(nodes) if i not in nodes[n + 1:]]
  data["nodes"] = nodes

  targetids = []
  for a, b in zip(newsource+newsource2,newtarget+newtarget2):
    targetids.append(str(a)+"-"+str(b))

  targets=[]
  for a,b,c in zip(targetids,newsource+newsource2,newtarget+newtarget2):
    new_dict = dict(id=a,key=b,to=c)
    new_dict["from"] = new_dict.pop("key")
    targets.append(new_dict)
  targets = [i for n, i in enumerate(targets) if i not in targets[n + 1:]]
  data["edges"] = targets

  return visdcc.Network(id='net',
                     data=data,
                     options=dict(height='500px', width='90%'))


if __name__ == '__main__':
    app.run_server(debug=True)

