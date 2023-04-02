# **Building a serverless API that tweets about my blog posts using Azure OpenAI and LangChain**

This repository contains a serverless API (Azure Function) that creates tweets from a given blog post.

The API reads the content of a web page and summarizes it into a 280-character text using Azure OpenAI, this resulting text is then used to create a tweet.

# **How it works**

The following diagram shows how the API works.

![api-diagram](https://raw.githubusercontent.com/karlospn/building-a-tweeting-api-using-openai-and-azure-functions/main/docs/tweetapi-process-diagram.png)

The principle is really simple:

1. The API must be called with a parameter called `uri` in the Http request body, here's an example:

```bash
curl -X POST https://func-openai-azfunc-dev.azurewebsites.net/api/tweet?code=hoZ6u8lIMlhu7-Zs8gvDb04R2fXvYeapijR3YYRlgiwmAzFulsiRMA== \
     -H "Content-Type: application/json" \
     -d '{"uri": "https://www.mytechramblings.com/posts/deploy-az-resources-when-not-available-on-azurerm/"}'
```
The parameter `uri` indicates the website from where to obtain the content.

2. The API fetches the text content from the `uri` website.
3. The text content is split into multiple chunks, the reason is that the text tends to be too long to be summarized by a single request to Azure OpenAI.
4. Every chunk gets summarized independently using Azure OpenAI.
5. All the summarized chunks are put together in a single text and summarized again using Azure OpenAI to obtain the tweet.
6. The tweet gets posted to Twitter.

# **Application**

- The serverless API is an Azure Function with an HTTP trigger.
- The API is built using Python and it uses [LangChain](https://github.com/hwchase17/langchain) alongside with Azure OpenAI to summarize the content of the blog post.
- You can use whatever LLM model Azure OpenAI offers, those values are set via configuration. 
- The API uses [tweepy](https://www.tweepy.org/) to post the tweet to Twitter.

# **Package dependencies**

The following Python packages are needed: 

```text
azure-functions
tweepy
langchain
openai
tiktoken
unstructured
```
# **How to run the app**

You can find the Azure Function source code at the repository root level.

The function needs the following configuration values to run properly:

- ``TWITTER_CONSUMER_KEY``: Twitter API consumer key.
- ``TWITTER_CONSUMER_SECRET``: Twitter API consumer secret.
- ``TWITTER_ACCESS_TOKEN``: Twitter API access token.
- ``TWITTER_ACCESS_TOKEN_SECRET``: Twitter API access token secret.
- ``OPENAI_URL``: The URL of your Azure OpenAI service. 
     - It has the following format: ``https://{base}.openai.azure.com``
- ``OPENAI_DEPLOYMENT_NAME``: The Azure OpenAI model deployment name.
- ``OPENAI_APIKEY``: The Azure OpenAI api key.

The Twitter API values can be found in the [Twitter developer portal](https://developer.twitter.com/en/portal/dashboard), meanwhile the Azure OpenAI values can be retrieved from the [Azure Portal](https://portal.azure.com).

If you want to run the Azure Function locally, then you can put those values on the ``local.settings.json``. If you want to deploy the function into Azure, then put the configuration values in the Function App configuration section.


# **How to test the app**

- You can use any tool you want (``cURL``, ``Postman``, ``Insomnia``, etc.), you just have to make an HTTP call to the ``/tweet`` endpoint of the API.

Here's an example using ``cURL`` to call the API running in Azure:

```bash
curl -X POST https://func-openai-azfunc-dev.azurewebsites.net/api/tweet?code=hoZ6u8lIMlhu7-Zs8gvDb04R2fXvYeapijR3YYRlgiwmAzFulsiRMA== \
     -H "Content-Type: application/json" \
     -d '{"uri": "https://www.mytechramblings.com/posts/deploy-az-resources-when-not-available-on-azurerm/"}'
```

And here's another example using ``cURL`` to call the API running locally:

```bash
curl -X POST http://localhost:7071/api/tweet \
     -H "Content-Type: application/json" \  
     -d '{"uri": "https://www.mytechramblings.com/posts/how-to-integrate-your-roslyn-analyzers-with-sonarqube"}'
```


- If you want to test it locally, but don't want to install everything required to run an Azure Function, **there is also a Jupyter Notebook in the ``/notebook`` folder**.    

# **Output**

If you want to see the end result, you can visit the following Twitter account:
- https://twitter.com/CarlosPons34994

This Twitter account has no purpose at all, I have created it specially for this demo.

Here's a screenshot showing how a couple of the created tweets look like:

![api-diagram](https://raw.githubusercontent.com/karlospn/building-a-tweeting-api-using-openai-and-azure-functions/main/docs/tweetapi-tweet-results.png)