#!/usr/bin/env python
# coding: utf-8

# In[1]:


from googleapiclient.discovery import build
import pandas as pd
import seaborn as sns


# In[2]:


api_key = 'AIzaSyBPDm8LNmT-uRkWeBCm4JoqAFDYngmZ_R8'
channel_id = 'UCALuqr8BQi_djTbgEL5yeGA'

youtube = build('youtube', 'v3', developerKey=api_key)


# ## Function to get channel statistics

# In[3]:


def get_channel_stats(youtube, channel_id):
    
    request = youtube.channels().list(
               part='snippet, contentDetails, statistics',
               id=channel_id)
    response = request.execute() 
    
    data = dict(Channel_name = response['items'][0]['snippet']['title'],
               Subscribers = response['items'][0]['statistics']['subscriberCount'],
               Views = response['items'][0]['statistics']['viewCount'],
               Total_Videos = response['items'][0]['statistics']['videoCount'],
               playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads'])
    
    return data


# In[7]:


channel_data = get_channel_stats(youtube, channel_id)


# In[8]:


channel_data


# ## Function to get video ids

# In[16]:


playlist_id = channel_data['playlist_id']


# In[34]:


def get_video_ids(youtube, playlist_id):
    
    request = youtube.playlistItems().list(
              part = 'contentDetails',
              playlistId = playlist_id,
              maxResults = 50)
    response = request.execute()
    
    video_ids = []
    
    for i in range(len(response['items'])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])
    
    next_page_token = response.get('nextPageToken')
    more_pages = True
    
    while more_pages:
        if next_page_token is None:
            more_pages = False
        else:
            request = youtube.playlistItems().list(
                      part = 'contentDetails',
                      playlistId = playlist_id,
                      maxResults = 50,
                      pageToken = next_page_token)
            response = request.execute()
            
            for i in range(len(response['items'])):
                video_ids.append(response['items'][i]['contentDetails']['videoId'])
            
            next_page_token = response.get('nextPageToken')
    
    return video_ids


# In[35]:


video_ids = get_video_ids(youtube, playlist_id)


# In[ ]:


video_ids


# # Function to get video details

# In[62]:


def get_video_details(youtube, video_ids):
    
    all_video_stats = []
    
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
              part = 'snippet, statistics',
              id = ','.join(video_ids[i:i+50]))
        response = request.execute()
        
        for video in response ['items']:
            video_stats = dict(Title = video['snippet']['title'],
                              Published_date = video['snippet']['publishedAt'],
                              Views = video['statistics']['viewCount'],
                              Likes = video['statistics']['likeCount'],
                              Favourites = video['statistics']['favoriteCount']
                              )
            all_video_stats.append(video_stats)
   
    return all_video_stats


# In[64]:


video_details = get_video_details(youtube, video_ids)


# In[65]:


video_data = pd.DataFrame(video_details)


# In[67]:


video_data['Published_date'] = pd.to_datetime(video_data['Published_date']).dt.date
video_data['Views'] = pd.to_numeric(video_data['Views'])
video_data['Likes'] = pd.to_numeric(video_data['Likes'])
video_data['Favourites'] = pd.to_numeric(video_data['Favourites'])
video_data


# In[68]:


top10_videos = video_data.sort_values(by='Views', ascending=False).head(10)


# In[69]:


top10_videos


# In[70]:


ax1 = sns.barplot(x='Views', y='Title', data=top10_videos)


# In[71]:


video_data.to_csv('Video_Details(HarvestersTV).csv')


# In[ ]:




