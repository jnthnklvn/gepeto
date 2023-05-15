# Gepeto Chatbot

This project implements a chatbot using the OpenAI GPT-3 model and integrates it with a Telegram bot. The chatbot can carry on conversations with users and generate responses based on the OpenAI model's predictions.

## Prerequisites

Before setting up the project, make sure you have completed the following steps:

1. Create a MongoDB Atlas Account:
   - Sign up for an account at [MongoDB Atlas](https://cloud.mongodb.com/)
   - Follow the instructions in the [MongoDB Atlas Tutorial](https://www.mongodb.com/docs/atlas/tutorial/create-atlas-account/) to create a cluster, a database named `gepeto_db`, and a collection. Here's an example document for the collection:

```json
{
    "_id": { "$oid": "65312d8ebedsadcxzb15b0ee" },
    "user_sid": "24723231213",
    "role": "user",
    "content": "Olá",
    "created_at": "2023-05-14T20:21:44.360479"
}
```

2. Create an App Service and Activate the GraphQL API:

    * Follow the instructions in the [MongoDB Atlas App Services Introduction](https://www.mongodb.com/docs/atlas/app-services/introduction/) to create an app service and activate the GraphQL API using the autogeneration schema.

3. Create a Telegram Bot:

    * Create a Telegram bot by following the instructions in the [Python Telegram Bot API Introduction](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-API). Note down the bot token.

4. Create an OpenAI Account:

    * Sign up for an account at [OpenAI](https://openai.com/) and obtain your API Key from the account dashboard.


## Setup

To set up the project, follow these steps:

1. Clone the repository:

```dotenv
git clone https://github.com/jnthnklvn/gepeto.git
cd gepeto
```

2. Create a `.env` file in the project root directory and provide the necessary environment variables:

```dotenv
[CHAT_GPT]
API_KEY = YOUR_CHAT_GPT_API_KEY

[TELEGRAM]
TOKEN = YOUR_TELEGRAM_BOT_TOKEN

[MONGO]
API_KEY = YOUR_MONGO_API_KEY
API_URL = MONGO_GRAPHQL_API_URL
```

Replace `YOUR_CHAT_GPT_API_KEY` with your actual OpenAI GPT API key, `YOUR_TELEGRAM_BOT_TOKEN` with your Telegram bot token, `YOUR_MONGO_API_KEY` with your MongoDB API key, and `MONGO_GRAPHQL_API_URL` with the URL of your MongoDB GraphQL API.

3. Build and run the Docker container:

```
docker build -t chatbot .
docker run -d chatbot
```

This will build the Docker image and run the container. Make sure you have Docker installed and running on your system.

4. The chatbot is now running and ready to respond to messages on Telegram. Start a conversation with your Telegram bot using the provided bot token.

## Dependencies

The project requires the following Python packages. They are listed in the `requirements.txt` file:
```
openai==0.27.6
pyTelegramBotAPI==4.11.0
gql==3.4.1
```

These dependencies will be installed automatically when building the Docker container.