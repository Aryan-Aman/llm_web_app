from . import api_blueprint
from flask import request, jsonify
from llm_chatter.services import openai_service, pinecone_service, scraping_service
from llm_chatter.utils.helper_functions import chunk_text, build_prompt

PINECONE_INDEX_NAME='my_index'

@api_blueprint.route('/embed-and-store', methods=['POST'])
def embed_and_store():
    url = request.json['url']
    url_text = scraping_service.scrape_url(url)
    chunks = chunk_text(url_text)
    pinecone_service.chunks_embed_and_upload_to_pinecone(chunks, PINECONE_INDEX_NAME)

    response ={
        'message':'chunks embedded and uploaded to pinecone successfully'
    }
    return jsonify(response)


@api_blueprint.route('/handle-query', methods=['POST'])
def handle_query():
    question = request.json['question']
    context_chunks = pinecone_service.get_most_similar_chunks_for_query(question, PINECONE_INDEX_NAME)
    prompt = build_prompt(question, context_chunks)
    answer = openai_service.get_llm_answer(prompt)
    return jsonify({ "question": question, "answer": answer })
