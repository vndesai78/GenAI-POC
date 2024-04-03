import json
import os
import sys
import boto3
import streamlit as st
import knowledgeBase_helper as kbh
from io import StringIO
from io import BytesIO
from pypdf import PdfReader

## We will be suing Titan Embeddings Model To generate Embedding

from langchain_community.embeddings import BedrockEmbeddings
from langchain.llms.bedrock import Bedrock

## Data Ingestion

import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader

# Vector Embedding And Vector Store

from langchain.vectorstores import FAISS

## LLm Models
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

## Bedrock Clients
bedrock=boto3.client(service_name="bedrock-runtime")
bedrock_embeddings=BedrockEmbeddings(model_id="amazon.titan-embed-text-v1",client=bedrock)
kb_id = "RZGU5XTEWI" # replace it with the Knowledge base id.


## Data ingestion
def data_ingestion():
    loader=PyPDFDirectoryLoader("data")
    documents=loader.load()

    # - in our testing Character split works better with this PDF data set
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=10000,
                                                 chunk_overlap=1000)
    
    docs=text_splitter.split_documents(documents)
    return docs

## Vector Embedding and vector store

def get_vector_store(docs):
    vectorstore_faiss=FAISS.from_documents(
        docs,
        bedrock_embeddings
    )
    vectorstore_faiss.save_local("faiss_index")

def get_claude_llm():
    ##create the Anthropic Model
    llm=Bedrock(model_id="ai21.j2-mid-v1",client=bedrock,
                model_kwargs={'maxTokens':512})
    
    return llm

def get_llama2_llm():
    ##create the Anthropic Model
    llm=Bedrock(model_id="meta.llama2-70b-chat-v1",client=bedrock,
                model_kwargs={'max_gen_len':512})
    
    return llm

prompt_template = """

Human: Use the following pieces of context to provide a 
concise answer to the question at the end but use atleast summarize with 
1500 words with detailed explaantions. If you don't know the answer, 
just say that you don't know, don't try to make up an answer.
<context>
{context}
</context

Question: {question}

Assistant: """

PROMPT = PromptTemplate(
    template= prompt_template, input_variables=["context", "question"]
)

def get_response_llm(llm,vectorstore_faiss,query):
    qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore_faiss.as_retriever(
        search_type="similarity", search_kwargs={"k": 3}
    ),
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)
    answer=qa({"query":query})
    return answer['result']

def uploadFileToS3(file, bucket, s3_file):
    s3 = boto3.client('s3',
                      region_name='us-east-1',
                      aws_access_key_id='AKIARXGX6HCNDEZ62HF4',
                      aws_secret_access_key='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')
    
    try:
        #s3.upload_file(file, bucket, s3_file)
        #st.write(file)
        file1 = open('temp.pdf', 'a')
        file1.write(file)
        file1.close()
        #s3.put_object()
        #s3.upload_fileobj(file1,bucket,s3_file)
        s3.upload_file('temp.pdf', bucket, s3_file)
        st.success('File Successfully Uploaded')
        return True
    except FileNotFoundError:
        #time.sleep(9)
        st.error('File not found.' + file)
        return False     

def resetText():
    if st.session_state["text1"] is not None :  
        st.session_state["text1"] = ""

def main():

    #st.set_page_config("ChatBot - Tata Motors Annual Reports Insights! 🤖") 
    st.header("Get Insights from Annual Reports 📔 📔")
    user_question = st.text_input("Ask a Question from the PDF Files 🔎 ", key="text1")
    #st.session_state["text1"] = ""
    with st.sidebar:
        st.title("Upload Data Files (PDFs) to KnowledgeBase 📁 ")
        c1, c2 = st.columns(2)
        
        #st.radio('options':['Tata Motors', 'Mahindra', 'Ashok Layland'])
        genre = st.radio(
        "Select Company for Annual Report upload",
        ["***Tata Motors***", "***Mahindra***", "***Ashok Layland***"],
        index=None, 
        )
        st.write("You selected:", genre)
        uploaded_pdf = st.file_uploader("Upload Annual Report PDF", type="pdf" )
        if uploaded_pdf is not None:
            
            if uploaded_pdf.type == "pdf":
                #c1.error('Only pdfs are supported. Please upload a different file')
                c1.balloons()
                
            else:
                st.success(uploaded_pdf.name + ' Selected')
                pdf_reader = PdfReader(uploaded_pdf)
                #data = uploaded_pdf.getvalue().read()
                #bytes_data = uploaded_pdf.getvalue()
                #st.write(bytes_data)
                pdf_text = ""

                for page in pdf_reader.pages :
                    pdf_text += page.extract_text()
                # To convert to a string based IO:
                #stringio = StringIO(uploaded_pdf.getvalue().decode("latin-1"))
                #stringio = BytesIO(uploaded_pdf.getvalue().decode("latin-1"))
                
                #st.write(stringio)
                # To read file as string:
                #string_data = stringio.read()
                #st.write(string_data)
                #uploaded_file.getvalue().decode("utf-8")
                if st.button('Upload'):
                    with st.spinner('Uploading...'):
                        #st.caption("TBD!!")
                        #with open(uploaded_pdf.name, "rb") as data:
                        uploadFileToS3(pdf_text,'tml-genai-poc-annual-reports/Tata Motors/',uploaded_pdf.name)

        #if st.button("Vectors Update"):
         #      docs = data_ingestion()
         #       get_vector_store(docs)
         #       st.success("Done")

    if st.button("Get Response"):
        with st.spinner("Processing..."):
            #faiss_index = FAISS.load_local("faiss_index", bedrock_embeddings, allow_dangerous_deserialization='True')
            #llm=get_claude_llm()
            
            #faiss_index = get_vector_store(docs)
            #st.write(get_response_llm(llm,faiss_index,user_question))
            st.write(kbh.get_response(user_question,kb_id))
            #resetText()
            st.success("Done 💯")

    #if st.button("Llama2 Output"):
    #    with st.spinner("Processing..."):
     #       #faiss_index = FAISS.load_local("faiss_index", bedrock_embeddings, allow_dangerous_deserialization='True')
            #llm=get_llama2_llm()
      #      
      #      #faiss_index = get_vector_store(docs)
      #      #st.write(get_response_llm(llm,faiss_index,user_question))
      #      st.write(user_question)
      #      st.write(kbh.get_response(user_question))
      #      st.success("Done")

if __name__ == "__main__":
    main()