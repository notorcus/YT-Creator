from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.chains import create_extraction_chain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.vectorstores import Pinecone
import pinecone
import json

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

import os
from dotenv import load_dotenv

load_dotenv()

llm3 = ChatOpenAI(temperature=0,
                  openai_api_key=os.getenv("OPENAI_API_KEY"),
                  model="gpt-3.5-turbo-0613",
                  request_timeout = 180
                )

llm4 = ChatOpenAI(temperature=0,
                  openai_api_key=os.getenv("OPENAI_API_KEY"),
                  model="gpt-4-0613",
                  request_timeout = 180,
                  streaming=True,
                  callbacks=[StreamingStdOutCallbackHandler()]
                )



def gen_cutstamps(transcript_path, num_videos: int = 3):

    with open(transcript_path) as file:
        transcript = file.read()

    # change chunk_size=10000, chunk_overlap=2000 later
    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", " "], chunk_size=10000, chunk_overlap=2000) 

    docs = text_splitter.create_documents([transcript])
    print (f"You have {len(docs)} docs. First doc is {llm3.get_num_tokens(docs[0].page_content)} tokens")

    template= """
    Given a transcript of a podcast episode, with timestamps in the HH:MM:SS format and speaker segments, your task is to divide the content into overarching and substantial chapters. Think of these chapters as major sections that encompass key themes and subjects of the podcast.

    Guidelines:
    1. Overarching Thematic Grouping: Create chapters that cover large portions of the conversation, focusing on substantial themes, extended interviews, or major dialogues.
    2. Non-Overlap and Continuity: Ensure that chapter timestamps do not overlap and flow logically from one to the next.
    3. Chapter Naming: Craft chapter titles that encapsulate the broad theme or subject matter.

    What to Avoid:
    - Being too granular: Do not segment the content into many small chapters. Instead, strive for fewer but more substantial chapters that encapsulate significant content and themes.
    - Creating chapters based on short comments, individual points, or minor topic shifts. Aim for broader divisions that each cover a substantial portion of the episode.

    Output Format:
    Provide the timestamps followed by the name of the chapter, such as:
     00:00:00 - 00:02:30 Introduction and Context of Life's Struggles
     00:02:30 - 00:06:04 In-depth Exploration of Success, Hard Work, and Practical Advice
     00:06:04 Emotional Support, Encouragement, and Conclusion

    The chapters should be fewer in number, each covering a significant and comprehensive part of the episode, and reflecting the overarching progression and thematic richness.
    """
    system_message_prompt_map = SystemMessagePromptTemplate.from_template(template)

    human_template="Transcript: {text}" # Simply just pass the text as a human message
    human_message_prompt_map = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt_map = ChatPromptTemplate.from_messages(messages=[system_message_prompt_map, human_message_prompt_map])

    template="""
    You are a helpful assistant that helps remove any duplicate chapters you find and combine their timestamps into one.

    You will standardize the output structure like so in HH:MM:SS format:
     
    Correct: 
     00:00:00 - 00:02:30 Introduction and Context of Life's Struggles
     00:02:30 - 00:06:04 In-depth Exploration of Success, Hard Work, and Practical Advice
     00:06:04 Emotional Support, Encouragement, and Conclusion

    Incorrect: 
     00:00:00 Introduction and Context of Life's Struggles
     00:02:30 In-depth Exploration of Success, Hard Work, and Practical Advice
     00:06:04 Emotional Support, Encouragement, and Conclusion     

    """
    system_message_prompt_map = SystemMessagePromptTemplate.from_template(template)

    human_template="Transcript: {text}" # Simply just pass the text as a human message
    human_message_prompt_map = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt_combine = ChatPromptTemplate.from_messages(messages=[system_message_prompt_map, human_message_prompt_map])

    chain = load_summarize_chain(llm4,
                                chain_type="map_reduce",
                                map_prompt=chat_prompt_map,
                                combine_prompt=chat_prompt_combine,
                                    # verbose=True
                                )

    topics_found = chain.run({"input_documents": docs})

    schema = {
        "type": "object",
        "properties": {
            "topic_name": {
                "type": "string",
                "description": "The name of the topic"
            },
            "timestamps": {
                "type": "object",
                "properties": {
                    "start_time": {
                        "type": "string",
                        "pattern": "^(?:[01]\\d|2[0-3]):(?:[0-5]\\d):(?:[0-5]\\d)$",
                        "description": "The start time of the topic in HH:MM:SS format"
                    },
                    "end_time": {
                        "type": "string",
                        "pattern": "^(?:[01]\\d|2[0-3]):(?:[0-5]\\d):(?:[0-5]\\d)$",
                        "description": "The end time of the topic in HH:MM:SS format"
                    }
                },
                "required": ["start_time", "end_time"]
            }
        },
        "required": ["topic_name", "timestamps"]
    }

    chain = create_extraction_chain(schema, llm3)
    topics_structured = chain.run(topics_found)

    print(topics_structured)

    with open("structured_topics.json", 'w') as outfile:
        json.dump(topics_structured, outfile)

if __name__ == '__main__':
    gen_cutstamps(r"projects\Hormozi\intermediate\transcripts\Hormozi_audio_transcript.txt")