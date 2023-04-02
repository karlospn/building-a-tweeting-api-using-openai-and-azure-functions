import azure.functions as func
import os
import tweepy
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredURLLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts import PromptTemplate

prompt_template = """
You are the author of the source text.
You need to write a tweet that summarizes the source text.
The tweet must not contain any kind of code.
Make sure the tweet is compelling and well-written. 
The tweet must end with the following phrase: 'More details in: www.mytechramblings.com'
The total tweet size must have no more than 270 characters.

SOURCE:
{text}

TWEET IN ENGLISH:"""

app = func.FunctionApp()

@app.function_name(name="TweetApi")
@app.route(route="tweet")
def test_function(req: func.HttpRequest) -> func.HttpResponse:

    try:
        # Get twitter credentials
        twitter_consumer_key = os.environ['TWITTER_CONSUMER_KEY']
        twitter_consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
        twitter_access_token = os.environ['TWITTER_ACCESS_TOKEN']
        twitter_access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

        # Get Azure OpenAi credentials
        az_open_ai_url = os.environ['OPENAI_URL']
        az_open_ai_apikey = os.environ['OPENAI_APIKEY']
        az_open_ai_deployment_name = os.environ['OPENAI_DEPLOYMENT_NAME']

    except KeyError:
        return func.HttpResponse("Something went wrong when trying to retrieve the credentials", status_code=500)
    
    try:
        # Read uri from HTTP request
        req_body = req.get_json()
        uri = req_body.get('uri')
    except ValueError:
        return func.HttpResponse( "The request has a missing body.", status_code=400)
    
    if not uri:
        return func.HttpResponse( "The 'uri' attribute is missing in the request body.",  status_code=400)
    else:
        try:
            
            # Create Azure OpenAI client
            llm = AzureChatOpenAI(
                openai_api_base=az_open_ai_url,
                openai_api_version="2023-03-15-preview",
                deployment_name=az_open_ai_deployment_name,
                openai_api_key=az_open_ai_apikey,
                openai_api_type = "azure",
            ) 

            # Read context from URI
            loader = UnstructuredURLLoader(urls=[uri])
            data = loader.load()

            # Split content into chunks
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
            texts = text_splitter.split_documents(data)
            
            # Run langchain 'map_reduce' chain
            prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
            chain = load_summarize_chain(llm, chain_type="map_reduce", combine_prompt=prompt)
            output = chain.run(texts)

            # Print tweet content
            print(output)

            # Create Twitter client
            client = tweepy.Client(
                consumer_key=twitter_consumer_key, consumer_secret=twitter_consumer_secret,
                access_token=twitter_access_token, access_token_secret=twitter_access_token_secret
            )
      
            # Create tweet using langchain 'map_reduce' chain output
            response = client.create_tweet(
                text=output
            )
            return func.HttpResponse(f"https://twitter.com/user/status/{response.data['id']}")
        
        except tweepy.TweepyException as e:
            return func.HttpResponse(f"Something went wrong when creating the tweet: {e}", status_code=500)
        except Exception as ex:
            return func.HttpResponse(f"Something went wrong: {ex}", status_code=500)

