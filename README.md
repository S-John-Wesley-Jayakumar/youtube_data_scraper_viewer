# youtube_data_scraper_viewer

  This is a streamlit application that allows you to scrape YouTube channel data and perform various operations such scraping youtube channel details using its channel id , migrating scrapped datas to a MongoDB Datalake, migrating selected data to SQL data warehouse, and searching and viewing retrieved SQL data.
The application uses Google and YouTube API to perform scraping

# Usage
The application can be used if you want to analyze YouTube channel data , the app will start and display a graphical user interface (GUI) with different options.
# Scrape Data & Migrate to MongoDB Datalake
This option allows you to scrape data from YouTube channels and migrate it to a MongoDB Datalake. You can choose to scrape data for a single channel ID or multiple channel IDs (up to 10) and migrate it to mongo db by click of a button. 
# Migrate to SQL
With this option, you can migrate the data from the MongoDB Datalake to a SQL database. If there is data present in the MongoDB Datalake, you will be able to select a channel name and move its data to the SQL DataLake. The available channels in mongo db will be displayed as radio buttons. Select a channel and Click the "Move to SQL " button to initiate the migration.
# Search and View Retrieved SQL Data
This option allows you to search and view the data that has been migrated to the SQL database. If the database exists and contains data, you will be able to select a question from a dropdown list. The application will retrieve the data based on the selected question and display it as a DataFrame.

