import pinecone
import os
from llm_chatter.services.openai_service import get_embeddings

PINECONE_API_KEY=os.environ.get('PINECONE_API_KEY')

pinecone.Pinecone(api_key='PINECONE_API_KEY', environment='gcp-starter')

EMBEDDING_DIMENSION = 1536

def chunks_embed_and_upload_to_pinecone(chunks, index_name):
    if index_name in pinecone.list_indexes():
        pinecone.delete_index(name=index_name)
        pinecone.create_index(name=index_name, dimension=EMBEDDING_DIMENSION, metric='cosine')
        pinecone_index=pinecone.Index(index_name)

        embeddings_with_ids=[]
        for i, chunk in enumerate(chunks):
            embedding=get_embeddings(chunk)
            chunk_id=str(i)
            embeddings_with_ids.append((chunk_id, embedding, chunk))

        upserts=[]
        for id, vectr, text in embeddings_with_ids:
            upserts.append((id, vectr, {'chunk_text':text}))
        pinecone_index.upsert(vectors=upserts)


def get_similar_chunks_for_question(question, index_name):
    question_embedding=get_embeddings(question)
    index=pinecone.Index(index_name)
    question_results=index.query(question_embedding, top_k=4, include_metadata=True)
    context_chunks= [match['metadata']['chunk_text']for match in question_results['matches']]
    return context_chunks

