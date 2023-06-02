import streamlit as st
from googleapiclient.discovery import build

# YouTube API connection
api_key = "YOUR_API_KEY"
youtube = build('youtube', 'v3', developerKey=api_key)

import streamlit as st
import pandas as pd

def create_sample_dataframe():
    # Define some sample channel IDs and names 
    channel_ids = [
        "UCnz-ZXXER4jOvuED5trXfEA",
        "UCLLw7jmFsvfIVaUFsLs8mlQ",
        "UCiT9RITQ9PW6BhXK0y2jaeg",
        "UC7cs8q-gJRlGwj4A8OmCmXg",
        "UC2UXDak6o7rBm23k3Vv5dww"
    ]
    channel_names = ["techTFQ", "Luke Barousse", "Ken Jee", "Alex the analyst", "Tina Huang"]
    
    # Create a DataFrame
    data = {
        "Channel ID": channel_ids,
        "Channel Name": channel_names
    }
    df = pd.DataFrame(data)
    
    return df

def get_single_inputs():
    
    input_data = st.text_input("Enter a Channel ID")
    stored = st.button("store to mongo",key="storedd")
    
    if input_data and stored:
        store_to_datalake(input_data)
      
    st.write("stote completed")    
         

def get_many_inputs():
    input_list1 = []
    total_inputs = int(st.number_input("Enter total number of Channel IDs", value=0, step=1, format="%d"))

    if total_inputs > 10 :
        st.write(" Channel Id Out of Range")
    else:

        for i in range(total_inputs):
            input_data1 = st.text_input("Enter Channel ID {}".format(i + 1))
            input_list1.append(input_data1)

        go_button = st.button("Go - Multiple Channel IDs", key="multiple_inputs_button")

        if go_button:
            for i in input_list1:
                store_to_datalake(i)
 
def scrape_channel_data(channel_id):
    channel_data = {}

    api_key = "AIzaSyBcfV870sP3uHLDi8UEnTsEQ72Xrpt0Op8"
    youtube = build('youtube', 'v3', developerKey=api_key)    

    # Get channel details
    channel_response = youtube.channels().list(
        part='snippet,statistics,contentDetails',
        id=channel_id
    ).execute()

    print(channel_response)

    if len(channel_response['items']) > 0:
        # print(channel_response)
        channel = channel_response['items'][0]
        # channel_name = channel['snippet']['title']       

        channel_data= {
            'Channel_Name': channel['snippet']['title'],
            'Channel_Id': channel['id'],
            'Subscription_Count': channel['statistics']['subscriberCount'],
            'Channel_Views': channel['statistics']['viewCount'],
            'Channel_Description': channel['snippet']['description'],
            'Playlist_info': scrape_channel_playlists(channel_id),
            'video_info':scrape_vedio_data(channel_id)
        }    
        
        return channel_data
    else:
        st.write("not scraped")
        return None

       
   
def scrape_channel_playlists(channel_id):

    playlist_data = {}

    api_key = "AIzaSyBcfV870sP3uHLDi8UEnTsEQ72Xrpt0Op8"
    youtube = build('youtube', 'v3', developerKey=api_key)


    # Get playlist details
    playlists_response = youtube.playlists().list(
        part='snippet',
        channelId=channel_id,
        maxResults=50
    ).execute()

    for playlist in playlists_response['items']:
        playlist_id = playlist['id']
        playlist_title = playlist['snippet']['title']

        playlist_info = {
            'Playlist_Id': playlist_id,
            'Playlist_Name': playlist_title,
            'Video_Ids': []
        }

        # Get video IDs from the playlist
        playlist_items_response = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50
        ).execute()

        for item in playlist_items_response['items']:
            video_id = item['contentDetails']['videoId']
            playlist_info['Video_Ids'].append(video_id)

        next_page_token = playlist_items_response.get('nextPageToken')

        while next_page_token:
            playlist_items_response = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            for item in playlist_items_response['items']:
                video_id = item['contentDetails']['videoId']
                playlist_info['Video_Ids'].append(video_id)

            next_page_token = playlist_items_response.get('nextPageToken')

        playlist_data[playlist_id] = playlist_info

    return playlist_data


from googleapiclient.errors import HttpError


def scrape_vedio_data(channel_id):
               # Set up the YouTube Data API client
    api_key = "AIzaSyBcfV870sP3uHLDi8UEnTsEQ72Xrpt0Op8"
    youtube = build('youtube', 'v3', developerKey=api_key)

    try:
        # Get the uploads playlist ID of the channel
        channels_response = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()

        uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # Get the video information for each video in the uploads playlist
        playlist_items_response = youtube.playlistItems().list(
            part='snippet',
            playlistId=uploads_playlist_id,
            maxResults=50
        ).execute()

        video_data = {}

        for item in playlist_items_response['items']:
            video_id = item['snippet']['resourceId']['videoId']

            # Get the video statistics
            videos_response = youtube.videos().list(
                part='snippet,statistics',
                id=video_id
            ).execute()

            video_info = videos_response['items'][0]['snippet']
            statistics = videos_response['items'][0]['statistics']


            try:
                comments = {}
                import uuid
                comment_idd =  str(uuid.uuid4())
                # Get the video comments
                comments_response = youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=5
                ).execute()           
                # print(comments_response)
                
                if comments_response['items']:

                    for comment in comments_response['items']:

                        
                        comment_id = comment['snippet']['topLevelComment']['id']
                        comment_info = comment['snippet']['topLevelComment']['snippet']
                        comments[comment_id] = {
                            'Comment_Id': comment_id,
                            'Comment_Text': comment_info['textDisplay'],
                            'Comment_Author': comment_info['authorDisplayName'],
                            'Comment_PublishedAt': comment_info['publishedAt']
                        }
            except HttpError as e:
                
                st.write('An HTTP error occurred:')
                st.write(e)   
                                      
            
                comments[comment_idd] = {
                        'Comment_Id': "Disabled",
                        'Comment_Text':"Disabled",
                        'Comment_Author': "Disabled",
                        'Comment_PublishedAt': "Disabled"
                    }
            

            video_data [video_id]= {
                'Video_Id': video_id,
                'Video_Name': video_info['title'],
                'Video_Description': video_info['description'],
                'Tags': video_info.get('tags', []),
                'PublishedAt': video_info['publishedAt'],
                'View_Count': statistics['viewCount'],
                'Like_Count': statistics['likeCount'],
                #'Dislike_Count': statistics.get('dislikeCount', 0),
                'Favorite_Count': statistics.get('favoriteCount', 0),
                'Comment_Count': int(statistics.get('commentCount', 0)),
                #'Duration': video_info['duration'],
                'Thumbnail': video_info['thumbnails']['default']['url'],
                'Caption_Status': video_info.get('caption', 'Not available'),
                'comments':comments

            }
        
        return video_data

    except HttpError as e:
        st.write('An HTTP error occurred:')
        st.write(e)
        return video_data





def get_mongo_channel_names():

    from pymongo import MongoClient
    # MongoDB connection
    mongo_client = MongoClient("mongodb+srv://wes:abc@bookshelf.w0fiuyr.mongodb.net/?retryWrites=true&w=majority")
    mongo_db = mongo_client["youtube_data_lake"]
    mongo_collection = mongo_db["data"]

    documents = mongo_collection.find()
    st.write(documents)
    channel_names = []

    for doc in documents:
        if "Channel_Name" in doc:
            # print(doc)
            channel_names.append(doc["Channel_Name"])
    
    channel_set = set(channel_names)    
    channel_list = list(channel_set) 
    
    return channel_list

     

def store_to_datalake(chid):
        
    # chid = "UCiT9RITQ9PW6BhXK0y2jaeg"  #kenjee
    # chid = "UC7cs8q-gJRlGwj4A8OmCmXg" #alex the analyst
    st.write(chid)
    names = get_mongo_channel_names()

    if chid in names:
        st.write("Data already exists in mongo")

    else:
        st.write("Data storing in mongo")

        c =scrape_channel_data(chid)

        from pymongo import MongoClient
        from googleapiclient.discovery import build

        # MongoDB connection
        mongo_client = MongoClient("mongodb+srv://wes:abc@bookshelf.w0fiuyr.mongodb.net/?retryWrites=true&w=majority")
        mongo_db = mongo_client["youtube_data_lake"]
        mongo_collection = mongo_db["data"]

        # Insert the dictionary into the collection
        result = mongo_collection.insert_one(c)

        # Check if the insertion was successful
        if result.inserted_id:
            print("Dictionary inserted successfully.")
            st.write("Dictionary inserted successfully.")
        else:
            print("Failed to insert the dictionary.")
            st.write("Failed to insert the dictionary.")

        print("Uploaded===========")

        st.write("Data uploaded")

##########################################################

import mysql.connector
from pymongo import MongoClient
def create_db_schema(database_name, table_name1,table_name2,table_name3,table_name4):
    
    import mysql.connector
    # MySQL connection
    mysql_db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password"
    )
    mysql_cursor = mysql_db.cursor()

    # Create a new database
    mysql_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
    mysql_cursor.execute(f"USE {database_name}")

    query1 = f"""CREATE TABLE IF NOT EXISTS {table_name1} (
        Channel_Name TEXT,
        Channel_Id VARCHAR(300) PRIMARY KEY,
        Subscription_Count TEXT,
        Channel_Views TEXT,
        Channel_Description TEXT,
        UNIQUE (Channel_Id)
    );"""
    query2 = f"""CREATE TABLE IF NOT EXISTS {table_name2} (
        Playlist_Id TEXT,
        Playlist_Name TEXT,
        Video_Ids TEXT,
        Channel_Id VARCHAR(300),
        Channel_Name TEXT
        
    );"""

  
    query3 = f"""
            CREATE TABLE IF NOT EXISTS {table_name3} (
                Video_Id TEXT,
                Video_Name TEXT,
                Video_Description TEXT,
                PublishedAt DATETIME,
                View_Count TEXT,
                Like_Count TEXT,
                Favorite_Count TEXT,
                Comment_Count TEXT,
                Thumbnail TEXT,
                Caption_Status TEXT,
                Channel_Id VARCHAR(300),
                FOREIGN KEY (Channel_Id) REFERENCES Channels(Channel_Id)
            );
        """
    query4 = f"""CREATE TABLE IF NOT EXISTS {table_name4} (
        Comment_Id TEXT,
        Comment_Text TEXT,
        Comment_Author TEXT,
        Comment_PublishedAt TEXT,
        Video_Id TEXT

        
    );"""
    mysql_cursor.execute(query1)
    mysql_cursor.execute(query2)
    mysql_cursor.execute(query3)
    mysql_cursor.execute(query4)


def channel_table(database_name, table_name,channel_name):

    print("come to cannels")
    # MySQL connection
    mysql_db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password"
    )
    mysql_cursor = mysql_db.cursor()   
    mysql_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
    mysql_cursor.execute(f"USE {database_name}")
   

    # MongoDB connection
    mongo_client = MongoClient("mongodb+srv://wes:abc@bookshelf.w0fiuyr.mongodb.net/?retryWrites=true&w=majority")
    mongo_db = mongo_client["youtube_data_lake"]
    mongo_collection = mongo_db["data"]

    query = {"Channel_Name": channel_name}
    video_cursor = mongo_collection.find(query)


    for document in video_cursor:
        # print(document)
        Channel_Name = document['Channel_Name']
        Channel_Id = document['Channel_Id']
        Subscription_Count = document['Subscription_Count']
        Channel_Views = document['Channel_Views']
        Channel_Description = document['Channel_Description']

        query1 = f"INSERT INTO {table_name} (Channel_Name, Channel_Id, Subscription_Count, Channel_Views, Channel_Description) VALUES (%s, %s, %s, %s, %s)"
        values = (Channel_Name, Channel_Id, Subscription_Count, Channel_Views, Channel_Description)

        mysql_cursor.execute(query1, values)        

    mysql_db.commit()  # Commit the changes to the database

    mysql_cursor.close()
    mysql_db.close()



def playlist_table(database_name, table_name,channel_name):
    # MySQL connection
    mysql_db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password"
    )
    mysql_cursor = mysql_db.cursor()

    # Create a new database
    mysql_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
    mysql_cursor.execute(f"USE {database_name}")
    
    # MongoDB connection
    mongo_client = MongoClient("mongodb+srv://wes:abc@bookshelf.w0fiuyr.mongodb.net/?retryWrites=true&w=majority")
    mongo_db = mongo_client["youtube_data_lake"]
    mongo_collection = mongo_db["data"]

    query = {"Channel_Name": channel_name}
    video_cursor = mongo_collection.find(query)


    for document in video_cursor:
        
        Id = document["Channel_Id"]
        Name = document["Channel_Name"]

        plylist_ids = list(document["Playlist_info"])
     
        print("-----------------------------------------------")
       
        for item in plylist_ids:

            Channel_Id =str(Id)
            Channel_Name =str(Name)

            Playlist_Id = document['Playlist_info'][f"{item}"]["Playlist_Id"]
            Playlist_Name = document['Playlist_info'][f"{item}"]["Playlist_Name"]
            Video_Ids = ",".join(document['Playlist_info'][f"{item}"]["Video_Ids"])
         
            query1 = f"INSERT INTO {table_name} (Playlist_Id, Playlist_Name, Video_Ids,Channel_Id,Channel_Name) VALUES (%s, %s,%s,%s, %s)"
            values = (Playlist_Id, Playlist_Name, Video_Ids,Channel_Id,Channel_Name)

            mysql_cursor.execute(query1, values)
            
    mysql_db.commit()  # Commit the changes to the database

    mysql_cursor.close()
    mysql_db.close()



def Video_table(database_name, table_name,channel_name):
    
        # MySQL connection
    mysql_db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password"
    )
    mysql_cursor = mysql_db.cursor()

    # Create a new database
    mysql_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
    mysql_cursor.execute(f"USE {database_name}")
   
    mongo_client = MongoClient("mongodb+srv://wes:abc@bookshelf.w0fiuyr.mongodb.net/?retryWrites=true&w=majority")
    mongo_db = mongo_client["youtube_data_lake"]
    mongo_collection = mongo_db["data"]

    query = {"Channel_Name": channel_name}  
    
    vedio_cursur = mongo_collection.find(query) 

    for document in vedio_cursur:

        vedioid = list(document['video_info'])
        
        for vedioids in vedioid:

            Video_id = str(document['video_info'][f'{vedioids}']['Video_Id'])  # Convert to string
            Video_Name = document['video_info'][f'{vedioids}']['Video_Name']
            video_description = document['video_info'][f'{vedioids}']['Video_Description']
            published_at = document['video_info'][f'{vedioids}']['PublishedAt']            
            view_count = document['video_info'][f'{vedioids}']['View_Count']
            like_count = document['video_info'][f'{vedioids}']['Like_Count']
            favorite_count = document['video_info'][f'{vedioids}']['Favorite_Count']
            comment_count = document['video_info'][f'{vedioids}']['Comment_Count']
            thumbnail = document['video_info'][f'{vedioids}']['Thumbnail']
            caption_status = document['video_info'][f'{vedioids}']['Caption_Status']         
            published_at = document['video_info'][f'{vedioids}']['PublishedAt']
            Channel_Id = document["Channel_Id"]


            import datetime
            published_at_datetime = datetime.datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ')
            formatted_published_at = published_at_datetime.strftime('%Y-%m-%d %H:%M:%S')
            
            query1 = f"""
                INSERT INTO {table_name} (Video_Id, Video_Name, Video_Description, PublishedAt,
                View_Count, Like_Count, Favorite_Count, Comment_Count, Thumbnail, Caption_Status,Channel_Id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s);
            """
            values = (Video_id, Video_Name, video_description, formatted_published_at, view_count, like_count,
                    favorite_count, comment_count, thumbnail, caption_status,Channel_Id)
            mysql_cursor.execute(query1, values)

    mysql_db.commit()  # Commit the changes to the database
    print("Data Moved Successfully !!")
    
    mysql_cursor.close()
    mysql_db.close()


def comments_table(database_name, table_name,channel_name):
    # MySQL connection
    mysql_db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password"
    )
    mysql_cursor = mysql_db.cursor()

    # Create a new database
    mysql_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
    mysql_cursor.execute(f"USE {database_name}")
  
    # MongoDB connection
    mongo_client = MongoClient("mongodb+srv://wes:abc@bookshelf.w0fiuyr.mongodb.net/?retryWrites=true&w=majority")
    mongo_db = mongo_client["youtube_data_lake"]
    mongo_collection = mongo_db["data"]

    query = {"Channel_Name": f"{channel_name}"}
    video_cursor = mongo_collection.find(query)
    

    for document in video_cursor:
        # get all vedio ids
        vedioid = list(document['video_info'])

        for items in vedioid:     
                       
              for i in vedioid:
                #get comment ids of a vedio id
                Comment_id = list(document["video_info"][f"{i}"]["comments"])

                for item in Comment_id:

                    v = str(i)                 

                    Comment_Id = document['video_info'][f"{i}"]["comments"][f"{item}"]["Comment_Id"]
                    Video_Id = v
                    Comment_Text = document['video_info'][f"{i}"]["comments"][f"{item}"]["Comment_Text"]
                    Comment_Author = document['video_info'][f"{i}"]["comments"][f"{item}"]["Comment_Author"]
                    Comment_PublishedAt = document['video_info'][f"{i}"]["comments"][f"{item}"]["Comment_PublishedAt"]
                    # import datetime
                    # Comment_PublishedAt_datetime = datetime.datetime.strptime(Comment_PublishedAt, '%Y-%m-%dT%H:%M:%SZ')
                    # formatted_Comment_PublishedAt = Comment_PublishedAt_datetime.strftime('%Y-%m-%d %H:%M:%S')

                    
                    query1 = f"INSERT INTO {table_name} (Comment_Id, Comment_Text, Comment_Author,Comment_PublishedAt,Video_Id) VALUES (%s,%s, %s,%s,%s)"
                    values = (Comment_Id,Comment_Text, Comment_Author,Comment_PublishedAt,Video_Id)

                    mysql_cursor.execute(query1, values)                    

                    mysql_db.commit() 

        mysql_cursor.close()
        mysql_db.close()


def sql_check_channel_names(channel_name):

        #Create Schema
        database_name = "youtube"
        table_name1 = "Channels"
        table_name2 = "playlist"
        table_name3 = "vedio"
        table_name4 = "comment"
        
        create_db_schema(database_name, table_name1,table_name2,table_name3,table_name4)

        print("table created")

        #Check if channel name data exist by counting number of rows in the table

        mysql_db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password"
        )
        mysql_cursor = mysql_db.cursor()   
        mysql_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        mysql_cursor.execute(f"USE {database_name}")   


        q = f"""SELECT COUNT(*) AS channel_count
            FROM Channels
            WHERE Channel_Name = '{channel_name}';
            """

        mysql_cursor.execute(q)
        result = mysql_cursor.fetchone()

        channel_count = int(result[0])
        print(type(channel_count))
        print(f"The channel count is: {channel_count}")

        if channel_count > 0:
            print("data already exist")
            st.write("data already exist")

        else:

            #insert that record

            database_name = "youtube"
            table_name1 = "Channels"
            table_name2 = "playlist"
            table_name3 = "vedio"
            table_name4 = "comment"

            print("elseeee")
            st.write("Data loading in progress")

            channel_table(database_name, table_name1,channel_name)
            st.write("Channel data loaded")

            playlist_table(database_name, table_name2,channel_name)
            st.write("playlist data loaded")

            Video_table(database_name, table_name3,channel_name)
            st.write("vedio data loaded")

            comments_table(database_name, table_name4,channel_name)
            st.write("Comments data loaded")

            st.write("Data loading complete")



def retrieve(question):


    import mysql.connector
    import pandas as pd
    # MySQL connection
    mysql_db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="youtube"  # Specify the database name you wabt to reterive information from 
    )
    mysql_cursor = mysql_db.cursor()

    if question == "What are the names of all the videos and their corresponding channels?":
    

            mysql_cursor.execute(f"USE youtube")


            query1 = """SELECT v.Video_Name, c.Channel_Name
                        FROM vedio AS v
                        JOIN channels AS c ON v.Channel_Id = c.Channel_Id;"""
           
            print("Question:",question)
            st.write("Question:",question)
            print("Query:", query1)
            st.write("Query:", query1)

            mysql_cursor.execute(query1)

            results = mysql_cursor.fetchall()     

            # Convert results to dataframe
            df = pd.DataFrame(results, columns=['Video_Name', 'Channel_Name'])
            print("\nDataFrame:")
            print(df)

            mysql_cursor.close()
            mysql_db.close()

    

    elif question == "Which channels have the most number of videos, and how many videos do they have?":
            mysql_cursor.execute(f"USE youtube")

            query1 = """SELECT c.Channel_Name, COUNT(v.Video_Id) AS Video_Count
                        FROM channels AS c
                        JOIN vedio AS v ON c.Channel_Id = v.Channel_Id
                        GROUP BY c.Channel_Name
                        ORDER BY Video_Count DESC;"""

            mysql_cursor.execute(query1)
            results = mysql_cursor.fetchall()

            # Convert results to dataframe
            df = pd.DataFrame(results, columns=['Channel_Name', 'Video_Count'])
            print("\nDataFrame:")
            print(df)

    elif question == "What are the top 10 most viewed videos and their respective channels?":
        mysql_cursor.execute(f"USE youtube")

        query1 = """SELECT v.Video_Name, c.Channel_Name, v.View_Count
                    FROM vedio AS v
                    JOIN channels AS c ON v.Channel_Id = c.Channel_Id
                    ORDER BY v.View_Count DESC
                    LIMIT 10;"""

        mysql_cursor.execute(query1)
        results = mysql_cursor.fetchall()

        # Convert results to dataframe
        df = pd.DataFrame(results, columns=['Video_Name', 'Channel_Name', 'View_Count'])
        print(df)

        mysql_cursor.close()
        mysql_db.close()

    elif question == "How many comments were made on each video, and what are their corresponding video names?":
        mysql_cursor.execute(f"USE youtube")

        query1 = """SELECT v.Video_Name, v.Comment_Count
                    FROM vedio AS v;"""

        mysql_cursor.execute(query1)
        results = mysql_cursor.fetchall()

        # Convert results to dataframe
        df = pd.DataFrame(results, columns=['Video_Name', 'Comment_Count'])
        print(df)

        mysql_cursor.close()
        mysql_db.close()
    elif question == "Which videos have the highest number of likes, and what are their corresponding channel names?":
        mysql_cursor.execute(f"USE youtube")

        query1 = """SELECT v.Video_Name, c.Channel_Name, v.Like_Count
                    FROM vedio AS v
                    JOIN channels AS c ON v.Channel_Id = c.Channel_Id
                    ORDER BY v.Like_Count DESC
                    LIMIT 10;"""

        mysql_cursor.execute(query1)
        results = mysql_cursor.fetchall()

        # Convert results to dataframe
        df = pd.DataFrame(results, columns=['Video_Name', 'Channel_Name', 'Like_Count'])
        print(df)

        mysql_cursor.close()
        mysql_db.close()

 

    elif question == "What is the total number of views for each channel, and what are their corresponding channel names?":
        mysql_cursor.execute(f"USE youtube")

        query1 = """SELECT c.Channel_Name, SUM(v.View_Count) AS Total_Views
                    FROM channels AS c
                    JOIN vedio AS v ON c.Channel_Id = v.Channel_Id
                    GROUP BY c.Channel_Name;"""

        mysql_cursor.execute(query1)
        results = mysql_cursor.fetchall()

        # Convert results to dataframe
        df = pd.DataFrame(results, columns=['Channel_Name', 'Total_Views'])
        print(df)

        mysql_cursor.close()
        mysql_db.close()

    elif question == "What are the names of all the channels that have published videos in the year 2022?":
        mysql_cursor.execute(f"USE youtube")

        query1 = """SELECT DISTINCT c.Channel_Name,v.Video_Name,v.PublishedAt
                    FROM channels AS c
                    JOIN vedio AS v ON c.Channel_Id = v.Channel_Id
                    WHERE YEAR(v.PublishedAt) = 2022;"""

        mysql_cursor.execute(query1)
        results = mysql_cursor.fetchall()

        # Convert results to dataframe
        df = pd.DataFrame(results, columns=['Channel_Name','Video_Name','PublishedAt'])
        print(df)

        mysql_cursor.close()
        mysql_db.close()

    elif question == "Which videos have the highest number of comments, and what are their corresponding channel names?":
        mysql_cursor.execute(f"USE youtube")

        query1 = """SELECT v.Video_Name, c.Channel_Name, v.Comment_Count
                    FROM vedio AS v
                    JOIN channels AS c ON v.Channel_Id = c.Channel_Id
                    WHERE v.Comment_Count = (
                        SELECT MAX(Comment_Count) FROM vedio
                    );"""

        mysql_cursor.execute(query1)
        results = mysql_cursor.fetchall()

        # Convert results to dataframe
        df = pd.DataFrame(results, columns=['Video_Name', 'Channel_Name', 'Comment_Count'])
        print(df)

        mysql_cursor.close()
        mysql_db.close()

    return df

def main():

    st.title("YouTube Channel Data Scraper and Viewer")

    # Define the options for the navigation bar
    options = ["Scrape Data & Migrate to MongoDB Datalake", "Migrate to SQL", "Search and View Retrieved SQL Data"]

    # Create a radio button nav bar to select the option
    nav_bar_option = st.sidebar.radio("Select an option", options,key="sidebar")


    # Display content based on the selected option
    if nav_bar_option == "Scrape Data & Migrate to MongoDB Datalake":
        df = create_sample_dataframe()
        # Display the sample DataFrame
        st.write(df)

        option = ["Scrape single channel id", "Scrape multiple channel ids (up to 10)"]
        input_choice = st.selectbox("Select an option", options=option)

        if input_choice == "Scrape single channel id":
            get_single_inputs()
     
        if input_choice == "Scrape multiple channel ids (up to 10)":
            get_many_inputs()
           

    elif nav_bar_option == "Migrate to SQL":
        
           
        channel_options = get_mongo_channel_names()       

        if len(channel_options) >0:
        
            channel_option = st.radio("Select an option", options=channel_options ,key="radio1")

            move_button = st.button("Move to SQL DataLake", key= "move_to_sql")

            if move_button:            
                sql_check_channel_names(channel_option)  

        else:                

            st.write("No Data present in Mongo DB Datalake")


    elif nav_bar_option == "Search and View Retrieved SQL Data":

        
        mysql_db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="password"
        )
        mysql_cursor = mysql_db.cursor()  
        # Execute the query
        mysql_cursor.execute("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'youtube'")

        # Fetch the result
        result = mysql_cursor.fetchone()

        if result is None:
            print("The database does not exist.")
            st.write("The database does not exist, Scrape data and migrate to mongo and sql to proceed")
        else:
            print("The database exists.") 
            
            
            mysql_cursor.execute(f"USE youtube")


            q = """SELECT COUNT(*) AS row_count
                FROM Channels
                ;
                """

            mysql_cursor.execute(q)
            result = mysql_cursor.fetchone()

            channel_count = int(result[0])

            print(type(channel_count))

            print(f"The channel count is: {channel_count}")

            if channel_count > 0:
                
                question_list = [
            
                        "What are the names of all the videos and their corresponding channels?",
                        "Which channels have the most number of videos, and how many videos do they have?",
                        "What are the top 10 most viewed videos and their respective channels?",
                        "How many comments were made on each video, and what are their corresponding video names?",
                        "Which videos have the highest number of likes, and what are their corresponding channel names?",                 
                        "What is the total number of views for each channel, and what are their corresponding channel names?",
                        "What are the names of all the channels that have published videos in the year 2022?",
                        "Which videos have the highest number of comments, and what are their corresponding channel names?"
                        
                        ]
                x = st.selectbox("select your question",options=question_list)     

                df = retrieve(x)

                st.write(df)
            else:
            
                st.write("No Data Available in database, Scrape data and migrate to mongo and sql to proceed")


       

if __name__ == "__main__":
    main()

