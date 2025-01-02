import os
import logging
from typing import List

import requests
from crewai.tools import BaseTool
from dotenv import load_dotenv

load_dotenv()

class YoutubeCommentsTool(BaseTool):
    name: str = "youtube_comments"
    description: str = "Use this tool to get the comments of a youtube video"

    def save_comments(self, comments: List[str], start_index: int):
        try:
            with open(f"comments_{start_index}.txt", "w") as file:
                for comment in comments:
                    file.write(comment + "\n")
            return start_index +len(comments)
        except Exception as e:
            logging.error(f"Error saving comments: {e}")
            return start_index
        
    def get_current_comment_count(self):
        try:
            if(os.path.exists("comments.md")):
                with open("comments.md", "r", encoding="utf-8") as file:
                    return len(file.readlines())
            else:
                return 0

        except Exception as e:
            logging.error(f"Error getting current comment count: {e}")
            return 0

    def _run(self, name: str, video_id: str) -> list:
        try:
           #Get API Key
            api_key = os.getenv("YOUTUBE_API_KEY")        
            if not api_key:
               logging.error("YOUTUBE_API_KEY is not set in the environment variables")
               return []

           #Get Comment 
            comments = []
            nextPageToken = None
            total_comments = self.get_current_comment_count();
        
            while True:
                url = f"https://www.googleapis.com/youtube/v3/commentThreads"
                params = {
                    "part": "snippet",
                    "videoId": video_id,
                    "key": api_key,
                    "pageToken": nextPageToken,
                    "textFormat": "plainText",
                    "maxResults": 100
                }

                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                #Process Comments
                for comment in data['items']:
                    comments.append(comment['snippet']['topLevelComment']['snippet']['textDisplay'])

                if(len(comments) >= 100):
                    total_comments = self.save_comments(comments, total_comments)
                    comments = []

                nextPageToken = data.get('nextPageToken')
                if nextPageToken is None:
                    break   

                return comments


        except Exception as e:
            return []


        return comments
