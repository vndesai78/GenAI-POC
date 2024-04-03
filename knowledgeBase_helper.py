import boto3
import pprint
from botocore.client import Config

pp = pprint.PrettyPrinter(indent=2)

bedrock_config = Config(connect_timeout=120, read_timeout=120, retries={'max_attempts': 0})
bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
bedrock_agent_client = boto3.client("bedrock-agent-runtime",config=bedrock_config, region_name='us-east-1')
#bedrock_agent_client.synch()

#model_id = "anthropic.claude-instant-v1" # try with both claude instant as well as claude-v2. for claude v2 - "anthropic.claude-v2"
modelid = "anthropic.claude-v2:1"
regionid = "us-east-1" # replace it with the region you're running sagemaker notebook
#kb_id = "JIKY1KUYAK" # replace it with the Knowledge base id.

def retrieveAndGenerate(input, kbId, sessionId=None, model_id = modelid, region_id = regionid):
    model_arn = f'arn:aws:bedrock:{region_id}::foundation-model/{model_id}'
    if sessionId:
        return bedrock_agent_client.retrieve_and_generate(
            input={
                'text': input
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': kbId,
                    'modelArn': model_arn
                }
            },
            sessionId=sessionId
        )
    else:
        return bedrock_agent_client.retrieve_and_generate(
            input={
                'text': input
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': kbId,
                    'modelArn': model_arn
                }
            }
        )
#query = "What is Amazon's doing in the field of generative AI?"
Template = ""

def get_response(query, KnowldgeBaseID):
        #final_query = Template + custom_prompt + query
        final_query = query
        kb_id = KnowldgeBaseID
        
        pp.pprint("+++++++++++++++++++++++++++++++++++++++++++++++++++\n")
        pp.pprint("Final Query : " + final_query)
        pp.pprint("+++++++++++++++++++++++++++++++++++++++++++++++++++\n")
        
        response = retrieveAndGenerate(final_query, kb_id,model_id=modelid,region_id=regionid)
        generated_text = response['output']['text']
        pp.pprint("Genarated Response : +++++++++++++++++++++++++++++++++++++++++++++++++++\n")
        pp.pprint(generated_text)
        pp.pprint("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
        
        citations = response["citations"]
        contexts = []
        for citation in citations:
            retrievedReferences = citation["retrievedReferences"]
            for reference in retrievedReferences:
                contexts.append(reference["content"]["text"])

        #pp.pprint(contexts)
        return generated_text

    
#question = "retrieve total number of vehical delivered in first 3 quarters of 2023 ?"
#response = get_response(question)

#response = retrieveAndGenerate(query, kb_id,model_id=modelid,region_id=regionid)
#generated_text = response['output']['text']
#pp.pprint(generated_text)

#citations = response["citations"]
#contexts = []
#for citation in citations:
#    retrievedReferences = citation["retrievedReferences"]
#    for reference in retrievedReferences:
#         contexts.append(reference["content"]["text"])

#pp.pprint(contexts)
