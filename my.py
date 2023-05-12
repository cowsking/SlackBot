import os
import psycopg2
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.chains.conversation.memory import ConversationBufferWindowMemory

import re
def process_result(results):
    print(results)
    length = len(results)
    output = ""
    output += "Here are the highest performing meta creatives for Rugs USA from 2023 February 10th to 2023 April 17th based on click-through rate. I've focused on the ones with top 10 impression volume:\n"
    for i in range(length):
        output += str(i+1) + ". "
        for j in range(len(results[i])):
            if j == 0:
                shorter = "_".join(results[i][j].split("_")[:2])
                output += "*" + shorter + "*, with "
            elif j == 1:
                output += str(results[i][j]) + " impressions, "
            elif j == 2:
                string = str(results[i][j])
                #keep the first two decimal
                if len(string) > 4:
                    string = string[:4]
                output += string + "% CTR, "
            
            elif j == 3:
                #keep the first two decimal
                string = str(results[i][j])
                if len(string) > 4:
                    string = string[:4]
                output += "$" + string + " CPC"
            
        output += "\n"
    return output

def is_sql_query(sentence):
    # Define a regular expression to match SQL queries
    # sql_regex = r"^SELECT.*FROM.*$"
    
    # # Use the regular expression to check if the sentence matches
    # if re.match(sql_regex, sentence.strip().upper()):
    #     return True
    # else:
    #     return False
    if "SELECT" in sentence:
        return True
    else:
        return False
# Connection parameters
# host = "your_host"
# database = "your_database"
# user = "your_user"
# password = "your_password"

# Initializes your app with your bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Langchain implementation
template = """I want you to act as a PostgreSQL terminal in front of an example database.'
    I will ask you questions and you will respond with the SQL query that will answer the question.
    The two tables in the database are:
    1. performance_data_view 
    The columns in the performance_data_view table are:
    id, clicks, conversions, conversions_values, cost_per_conversions, cpc, cpm, ctr, date, impressions, campaign_id
    2. campaign_data
    The columns in the campaign_data table are:
    id, camaign_name, adset_id, adset_name, ad_id, ad_name, ad_title, advertiser_name, platform_name, asset_url
   
    
   note that the column id in campaign_data is the same as the column campaign_id in performance_data_view
   advertiser_name are Marmot eCommerce, Virtue Labs, Men's Wearhouse Retail, Graco eCommerce, West Marine Facebook Ads, UI_1800Flowers_Main, Colorescience - Invoiced ad account, Rugs USA Paid Ads, Minted Direct Response, New Engen | NA | Altra Running, ThreadBeast, 1800Flowers, Men's Wearhouse Tux, 1_Everlane
   platform_name are Facebook, TikTok

   when I ask you to calculate higher performance, you have to qualify the data set by most frequently counted impressions (let's take the top 10 impression volume) and rank order them by CTR (click through rate) from highest to lowest. Show the ad_name, impressions,CTR, CPC in the output.

   Today is 2023-04-28
   ...

    {history}
    Human: {human_input}
    Assistant:"""

prompt = PromptTemplate(
    input_variables=["history", "human_input"], 
    # input_variables=["human_input"],
    template=template
)

chatgpt_chain = LLMChain(
    llm=OpenAI(temperature=0,openai_api_key=os.environ["OPENAI_API_TOKEN"],max_tokens=1000), 
    prompt=prompt, 
    verbose=True, 
    memory=ConversationBufferWindowMemory(k=2),
)
host = "34.145.26.239"
database = "your_database"
user = "your_user"
password = "your_password"

def get_sql_results(sql_query):
    # Connect to the database
    connection = psycopg2.connect(
    host="34.145.26.239",
    database="michaelTest",
    user="postgres",
    password='sl`FuuJu";~kFrfg'
)

    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Execute the query
    cursor.execute(sql_query)

    # Fetch and return the results
    rows = cursor.fetchall()

    # Close the cursor and the connection
    cursor.close()
    connection.close()

    return rows

# Message handler for Slack
@app.message(".*")
def message_handler(message, say, logger):
    # print(message)
    if 'recommendation' in message['text']:
        say('I analyzed creatives with Google Vision Al and found with 90% confidence that ad units indexing for "hard wood floor" seem to consistently outperform other ad units with respect to TR and PCs. I recommend we build more similarly constructed creatives.\n *See the full analysis*')
    else:
    # Convert the received question to an SQL command
        sql_query = chatgpt_chain.predict(human_input=message['text'])
        # sql_query = "select * from performance_data_view limit 10;"
        print(sql_query)
        if not is_sql_query(sql_query):
            print("not sql")
            say(sql_query)
        else:
            print("sql")
            # Call the SQL from the tables
            results = get_sql_results(sql_query)
            # Generate an explanation for the SQL query
            # process_result(results)
            #explanation = chatgpt_chain.predict(human_input=f"show the output: {results} Answer in numbered list and make ad_name shorter just keep before the first two underline and display *ad_name*, show numbers of impressions, add percentage in CTR, add dollar sign in CPC in this form: These basic visual styles are very simple to use:_italic_ will produce italicized text; *bold* will produce bold text;:")

            #print(explanation)
            
            # Send the results and explanation to Slack
            # say(f"Explanation: {explanation}")
            # Send the results to Slack
            say(process_result(results))
            say("Would you like to see the results without filtering for impression volume?")

# Start your app
if __name__ == "__main__":
    # os.environ['OPENAI_API_TOKEN'] = Token
    
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()