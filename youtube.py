import httplib2
import argparse
from googleapiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets, AccessTokenRefreshError
from oauth2client.tools import run_flow, argparser

class YouTubeInfo(object):

        @staticmethod
        def auth():
                scope = "https://www.googleapis.com/auth/youtube.readonly"
                storage = Storage("tokens/google.json")
                credentials = storage.get()
                parser = argparse.ArgumentParser(parents=[argparser])
                flags = argparser.parse_args()
                if credentials is None or credentials.invalid:
                        flow = flow_from_clientsecrets("secrets/google_client_secrets.json",scope=scope)
                        credentials = run_flow(flow, storage, flags)
                yt = build("youtube", "v3", http=credentials.authorize(httplib2.Http()))
                return yt

        def getTitle(self,this_id):
                if not self.validate(this_id):
                        return "Invalid ID"
                response = self.yt.videos().list(part="id,snippet,statistics,contentDetails",id=this_id).execute()
                info = response['items'][0]
                snippet = info['snippet']
                title = snippet['title']
                return title

        def __init__(self):
                self.yt = self.auth()

        def validate(self, this_id):
                response = self.yt.videos().list(part="id,snippet,statistics,contentDetails",id=this_id).execute()
                if len(response['items']) != 1:
                        return False
                else:
                        return True


if __name__ == "__main__":
        test_id = "WhBoR_tgXCI"
        youtube = YouTubeInfo()
        print youtube.getTitle(test_id)


