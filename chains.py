import os
import psycopg2
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.chains import SimpleSequentialChain
llm = OpenAI(temperature=0,openai_api_key='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')
template = """You are doing the mutiple choice. Given the question, choose the most similar option and output.

A. Highest Performance
B. other questions

Answer A or B.

Title: {question}
"""
prompt_template = PromptTemplate(input_variables=["question"], template=template)
task_chain = LLMChain(llm=llm, prompt=prompt_template)


overall_chain = SimpleSequentialChain(chains=[task_chain], verbose=True)
overall_chain.run("What were the highest CTR creative for Rugs USA Apr 1 to Apr 7")