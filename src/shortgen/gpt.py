from src import config
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.chains import create_extraction_chain

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.vectorstores import Pinecone
import pinecone

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
                  model="gpt-3.5-turbo",
                  request_timeout = 180
                )

llm4 = ChatOpenAI(temperature=0,
                  openai_api_key=os.getenv("OPENAI_API_KEY"),
                  model="gpt-4",
                  request_timeout = 180
                )



def gen_cutstamps(transcript_path, num_videos: int = 3):

    with open(transcript_path) as file:
        transcript = file.read()

    # change chunk_size=10000, chunk_overlap=2000 later
    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", " "], chunk_size=10000, chunk_overlap=2000) 

    transcript_subsection_characters = 8000
    docs = text_splitter.create_documents([transcript[:transcript_subsection_characters]])
    print (f"You have {len(docs)} docs. First doc is {llm3.get_num_tokens(docs[0].page_content)} tokens")

    template="""
    You are a helpful assistant that helps retrieve topics talked about in a podcast transcript
    - Your goal is to extract the topic names
    - Topics include:
    - Themes
    - Business Ideas
    - Interesting Stories
    - Quick stories about people
    - Mental Frameworks
    - Stories about an industry
    - Analogies mentioned
    - Advice or words of caution
    - Pieces of news or current events
    - Opinions about certain things
    - Do not respond with anything outside of the podcast. If you don't see any topics, say, 'No Topics'
    - Do not respond with numbers, just bullet points
    - Only pull topics from the transcript. Do not use the examples
    - A topic should be substantial, more than just a one-off comment

    % START OF EXAMPLES
    - Sam's Elisabeth Murdoch Story
    - Wildcard CEOs vs. Prudent CEOs
    - Tate's Chess Business
    - Restaurant Refiller
    - Importance of purpose in life
    - Why Pressure is a privilege
    - Are Winning & Success the same?
    - Using Cynicism as a Safety Blanket
    - How Can Money Buy Happiness?
    - Where Money, Happiness & Success Meet
    - Pros and Cons of Creatine
    % END OF EXAMPLES
    """
    system_message_prompt_map = SystemMessagePromptTemplate.from_template(template)

    human_template="Transcript: {text}" # Simply just pass the text as a human message
    human_message_prompt_map = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt_map = ChatPromptTemplate.from_messages(messages=[system_message_prompt_map, human_message_prompt_map])

    template="""
    You are a helpful assistant that helps retrieve topics talked about in a podcast transcript
    - You will be given a series of bullet topics of topics vound
    - Your goal is to exract the topic names
    - Remove any duplicate bullet points you see
    - No one topic should be repeated, even if worded differently
    - Try to look for big topics instead of 5 smaller topics basically talking about the same thing(they'll usually be bunched around one another because they were talked about around the same time). Although stories should be kept unique.
    - Mainly keep topics that already haven't been listed.
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
    print (topics_found)

    schema = {
        "properties": {
            # The title of the topic
            "topic_name": {
                "type": "string",
                "description" : "The title of the topic listed"
            },
        },
        "required": ["topic"],
    }

    chain = create_extraction_chain(schema, llm3)
    topics_structured = chain.run(topics_found)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=800)
    docs = text_splitter.create_documents([transcript[:transcript_subsection_characters]])

    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

    # initialize pinecone
    pinecone.init(
        api_key = os.getenv("PINECONE_API_KEY"),
        environment = os.getenv("PINECONE_API_ENV")
    )
    
    index_name = "yt-shorts"

    index = pinecone.Index(index_name)
    index.delete(delete_all='true')
    
    docsearch = Pinecone.from_documents(docs, embeddings, index_name=index_name)

    # The system instructions. Notice the 'context' placeholder down below. This is where our relevant docs will go.
    # The 'question' in the human message below won't be a question per se, but rather a topic we want to get relevant information on

    system_template = """
    You are an AI tasked with extracting a single, meaningful shortform clip from a transcript. Your goal: craft a continuous, insightful, and entertaining clip that can span multiple segments but remains within a total duration of 30-90 seconds.
    
    Guidelines:

    1. Strict Duration:
     - Calculate the duration by converting timecodes to seconds. E.g., 00:01:25 is 85 seconds.
     - Subtract the start time from the end time for each segment to find its duration. The combined time of all segments in the clip MUST be between 30 - 90 seconds.
    2. Consolidate Text Segments:
     - Extracted clips should contain no more than 3-5 separate timecodes.
     - Merge consecutive text segments into longer content blocks. Do not list every individual text segment.
     - Segments should be consecutive. If one segment's start time is the end time of the previous segment, combine them.
    3. Context:
     - Chosen segments should provide clear insight or narrative.
     - They should be coherent when put together and not require extra context.
    4. Content Selection: Focus on:
     - Clear explanations or valuable insights.
     - Entertaining or humorous moments, even if slightly off-topic.
    5. Flow & Non-overlapping: The selected segments should flow seamlessly into each other, and there should be no overlaps.
    
    What to Avoid (with examples):

     - Listing Every Minor Segment:
         - Incorrect:
           00:01:32,00:01:45
           00:01:45,00:01:52
         - Correct:
           00:01:32,00:01:52
     - Breaking the narrative.
     - Exceeding or drastically falling short of the duration limit.
    
    Output Format: Provide the start and end timecodes for each segment in the clip in CSV format

    Start Time,End Time
    00:01:30,00:01:45
    00:02:05,00:02:45

    End of example.

    ----------------
    {context}"""

    messages = [
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template("{question}"),
    ]

    # This will pull the two messages together and get them ready to be sent to the LLM through the retriever
    CHAT_PROMPT = ChatPromptTemplate.from_messages(messages)

    # Adjust k for more or less context
    qa = RetrievalQA.from_chain_type(llm=llm4,
                                    chain_type="stuff",
                                    retriever=docsearch.as_retriever(k=5),
                                    chain_type_kwargs = {
                                        'verbose': True,
                                        'prompt': CHAT_PROMPT
                                    })

    # Initializing the counter
    counter = 1

    for topic in topics_structured:
        query = f"""
            {topic['topic_name']}
        """

        expanded_topic = qa.run(query)

        # Saving the DataFrame to a CSV file
        print(f"{topic['topic_name']}")
        print(expanded_topic)
        print ("\n\n")

        abs_cutstamp = os.path.abspath(config.cutstamp_folder)

        with open(os.path.join(abs_cutstamp, f"short_{counter}.csv"), "w") as f:
            f.write(expanded_topic)
            f.flush()
            os.fsync(f.fileno())

        # Incrementing the counter
        counter += 1