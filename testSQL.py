from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
import psycopg2
import time
password = 'sl`FuuJu";~kFrfg'
print('start')
#time now
print('time',time.time())
print('-----------')
print('connect to db')
db = SQLDatabase.from_uri(f"postgresql+psycopg2://postgres:{password}@34.145.26.239:5432/michaelTest",include_tables=['campaigns','performance_data'])
print('time',time.time())
llm = OpenAI(temperature=0.5, openai_api_key='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')

# Create query instruction
QUERY = """
Given an input question, first create a syntactically correct postgresql query to run, then look at the results of the query and return the answer.
Use the following format:

Question: "Question here"
SQLQuery: "SQL Query to run"
SQLResult: "Result of the SQLQuery"
Answer: "Final answer here"


The two tables in the database are:
    1. performance_data
    The columns in the performance_data_view table are:
    clicks, conversions, conversions_values, cost_per_conversions, cpc, cpm, ctr, date, impressions, campaign_id
    2. campaigns
    The columns in the campaigns table are:
    id, ad_name
    3.advertiser
    The columns in the advertiser table are:
    name, platform_name
   
   
   advertiser_name are Marmot eCommerce, Virtue Labs, Men's Wearhouse Retail, Graco eCommerce, West Marine Facebook Ads, UI_1800Flowers_Main, Colorescience - Invoiced ad account, Rugs USA Paid Ads, Minted Direct Response, New Engen | NA | Altra Running, ThreadBeast, 1800Flowers, Men's Wearhouse Tux, 1_Everlane
   platform_name are Facebook, TikTok
   
    when I ask you to calculate higher performance in a time period, 
select * from (SELECT campaigns.ad_name, SUM(performance_data.impressions) AS impressions, SUM(performance_data.clicks)/SUM(performance_data.impressions)*100 AS CTR,
CASE WHEN SUM(performance_data.clicks) = 0 THEN Null ELSE SUM(performance_data.cpc * performance_data.clicks) / SUM(performance_data.clicks) END AS CPC
FROM performance_data
INNER JOIN campaigns ON performance_data.campaign_id = campaigns.id
INNER JOIN advertiser ON campaigns.advertiser_id = advertiser.id
WHERE advertiser.name = 'name'
AND performance_data.date BETWEEN 'from' AND 'to'
AND advertiser.platform_name = 'platform_name'
GROUP BY campaigns.ad_name
order by impressions desc LIMIT num) sub order by ctr desc


    
    if the result is not a empty set. If the result is a empty set, show "No result found".
    
    answer the questions with the following format:
    for impressions show numbers, for CTR with %, for CPC show in dollar amount.
    Explain how you calculate the higher performance.
{question}
"""

# Setup the database chain
db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=True)

def get_prompt():
    

    while True:
        prompt = input("Enter a prompt: ")

        if prompt.lower() == 'exit':
            print('Exiting...')
            break
        else:
            try:
                question = QUERY.format(question=prompt)
                print(question)
                print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                print(db_chain.run(question))
            except Exception as e:
                print()


get_prompt()