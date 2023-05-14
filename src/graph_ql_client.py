import datetime
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from typing import List, Dict


class GraphQLClient:
    def __init__(self, url: str, api_key: str):
        self.transport = AIOHTTPTransport(url=url, headers={'apiKey': api_key})
        self.client = Client(transport=self.transport,
                             fetch_schema_from_transport=True)

    def insert_message(self, user_sid: str, role: str, content: str):
        insert_query = gql('''
        mutation ($data: MessageInsertInput!) {
          insertOneMessage(data: $data) {
            _id
            user_sid
            role
            content
            created_at
          }
        }
        ''')

        variables = {
            'data': {
                'user_sid': user_sid,
                'role': role,
                'content': content,
                'created_at': datetime.datetime.utcnow().isoformat()
            }
        }

        response = self.client.execute(insert_query, variable_values=variables)
        return response['insertOneMessage']

    def get_messages(self, user_sid: str) -> List[Dict[str, str]]:
        get_query = gql('''
        query ($query: MessageQueryInput!) {
          messages(query: $query, sortBy: CREATED_AT_ASC) {
            role
            content
          }
        }
        ''')
        sevenDaysAgoDate = (datetime.datetime.utcnow(
        ) - datetime.timedelta(days=7))

        variables = {'query': {'user_sid': user_sid,
                               'created_at_gt': sevenDaysAgoDate.isoformat()}}

        response = self.client.execute(get_query, variable_values=variables)
        return response['messages']
