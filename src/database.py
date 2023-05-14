from typing import List, Dict
import logging
import pymongo
import datetime
import urllib.parse


class Database:
    def __init__(self, database_name: str, username: str, password: str):
        try:
            logging.info("Starting database connection...")
            username = urllib.parse.quote(username)
            password = urllib.parse.quote(password)
            uri = f"mongodb+srv://{username}:{password}@gepetocluster.fupqzps.mongodb.net/?retryWrites=true&w=majority"
            client = pymongo.MongoClient(uri)
            self._db = client.get_database(database_name)
            client.admin.command('ping')
            logging.info(
                "Pinged the server, successfully connected to MongoDB!")
        except Exception as e:
            logging.error(f"Error connecting to database: {e}")

    def insert_message(self, user_sid: str, role: str, content: str) -> None:
        try:
            message = {"user_sid": user_sid, "role": role,
                       "content": content, "created_at": datetime.datetime.utcnow().isoformat()}
            self._db['messages'].insert_one(message)
        except Exception as e:
            logging.error(f"Error inserting message: {e}")

    def get_messages_by_user_sid(self, user_sid: str) -> List[Dict[str, str]]:
        try:
            sevenDaysAgoDate = (datetime.datetime.utcnow(
            ) - datetime.timedelta(days=7)).isoformat()

            result = self._db['messages'].find(
                {"user_sid": user_sid, "created_at": {"$gte": sevenDaysAgoDate}}).sort('created_at', pymongo.ASCENDING)
            messages =  list(
                map(lambda x: {"role": x["role"], "content": x["content"]}, result))
            return messages
        except Exception as e:
            logging.error(f"Error retrieving messages: {e}")
