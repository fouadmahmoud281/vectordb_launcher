import streamlit as st
import requests
import json
import pandas as pd
import numpy as np
import time
from utils import SEARCH_API, card_container, render_stats

def render_search_tab():
    """Render the Search Collection tab with dark theme styling"""
    st.header("Search Collection")
    st.markdown("<p style='opacity: 0.7;'>Find semantically similar documents using vector search and similarity matching.</p>", unsafe_allow_html=True)
    
    # Search form in a card container
    card_container(lambda: search_form())
    
    # Results are displayed in the main results_area created in search_form
    if 'search_results' in st.session_state:
        display_search_results(st.session_state.search_results)

def search_form():
    """Render the search form with dark theme styling"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_collection = st.text_input("Collection Name", 
                                          value="my_collection",
                                          placeholder="Enter the collection name to search")
    
    with col2:
        query_input_method = st.radio(
            "Query Input Method",
            ["Text Query", "Vector Query"],
            index=0,
            horizontal=True
        )
    
    # Query input based on selected method
    query_text = None
    query_vector = None
    
    if query_input_method == "Text Query":
        query_text = st.text_area(
            "Search Query", 
            height=100,
            placeholder="Enter your search query here...",
            help="Enter text to search for similar documents in the collection"
        )
    else:
        vector_input = st.text_area(
            "Vector (JSON array format)",
            height=100,
            placeholder="[0.1, 0.2, 0.3, ...]",
            help="Enter a vector as a JSON array of numbers"
        )
        
        if vector_input:
            try:
                query_vector = json.loads(vector_input)
                if not isinstance(query_vector, list) or not all(isinstance(x, (int, float)) for x in query_vector):
                    st.warning("Vector must be a list of numbers")
                    query_vector = None
            except json.JSONDecodeError:
                st.warning("Invalid JSON format for vector")
                query_vector = None
    
    # Search parameters in a cleaner layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        limit = st.slider(
            "Result Limit", 
            min_value=1, 
            max_value=100, 
            value=5,
            help="Maximum number of results to return"
        )
    
    with col2:
        use_native_search = st.checkbox(
            "Use Native Search", 
            value=True,
            help="Use the database's native search instead of custom metrics"
        )
    
    with col3:
        score_all_documents = st.checkbox(
            "Score All Documents", 
            value=False,
            help="Score all documents (slower but more thorough)"
        )
    
    # Advanced search options in an expander
    with st.expander("Advanced Search Options"):
        if use_native_search:
            # HNSW search parameters for native search
            ef_param = st.number_input(
                "EF Search Parameter", 
                min_value=1, 
                value=128,
                help="Query time search scope. Higher values give better recall but slower search."
            )
        else:
            # Custom search options
            col1, col2 = st.columns(2)
            
            with col1:
                vector_space = st.selectbox(
                    "Vector Space",
                    ["cosine", "dot_product", "euclidean", "manhattan", "jaccard", "hamming", "text", "code"],
                    index=0,
                    help="The vector space to use for similarity computation"
                )
                
                # Preprocessing options
                st.subheader("Preprocessing Options")
                normalize = st.checkbox(
                    "Normalize Vectors", 
                    value=True,
                    help="Normalize vectors before computing similarity"
                )
                
                magnitude_weighting = st.checkbox(
                    "Magnitude Weighting", 
                    value=False,
                    help="Apply magnitude weighting to similarity scores"
                )
                
                if magnitude_weighting:
                    scale_factor = st.slider(
                        "Scale Factor", 
                        min_value=0.1, 
                        max_value=10.0, 
                        value=1.0, 
                        step=0.1,
                        help="Scale factor for magnitude weighting"
                    )
            
            with col2:
                # Threshold options
                st.subheader("Threshold Options")
                use_threshold = st.checkbox(
                    "Use Similarity Threshold", 
                    value=False,
                    help="Filter results by similarity threshold"
                )
                
                if use_threshold:
                    threshold_value = st.slider(
                        "Threshold Value", 
                        min_value=0.0, 
                        max_value=1.0, 
                        value=0.7, 
                        step=0.01,
                        help="Minimum similarity score to include in results"
                    )
                
                # Dimension weights
                st.subheader("Dimension Weights")
                use_dimension_weights = st.checkbox(
                    "Use Dimension Weights", 
                    value=False,
                    help="Apply weights to vector dimensions"
                )
                
                if use_dimension_weights:
                    weights_input = st.text_area(
                        "Weights (JSON array format)",
                        placeholder="[1.0, 0.8, 1.2, ...]",
                        help="Enter weights as a JSON array of numbers"
                    )
                    
                    if weights_input:
                        try:
                            weights = json.loads(weights_input)
                            if not isinstance(weights, list) or not all(isinstance(x, (int, float)) for x in weights):
                                st.warning("Weights must be a list of numbers")
                                weights = None
                        except json.JSONDecodeError:
                            st.warning("Invalid JSON format for weights")
                            weights = None
    
    # Search button
    search_button = st.button("Search Collection", type="primary", use_container_width=True)
    
    # Create a placeholder for results
    results_area = st.empty()
    
    if search_button:
        if not search_collection:
            st.warning("Please enter a collection name")
        elif not query_text and not query_vector:
            st.warning("Please provide either a text query or a vector query")
        else:
            with st.spinner("Searching..."):
                try:
                    # Prepare the search payload
                    payload = {
                        "collection_name": search_collection,
                        "limit": limit,
                        "score_all_documents": score_all_documents,
                        "use_native_search": use_native_search
                    }
                    
                    # Add query text or vector
                    if query_text:
                        payload["query_text"] = query_text
                    elif query_vector:
                        payload["query_vector"] = query_vector
                    
                    # Add advanced options based on search mode
                    if use_native_search:
                        # Native search options
                        payload["hnsw"] = {
                            "ef_construction": ef_param
                        }
                    else:
                        # Custom search options
                        payload["vector_space"] = vector_space
                        
                        # Add preprocessing if configured
                        payload["preprocessing"] = {
                            "normalize": normalize
                        }
                        
                        if magnitude_weighting:
                            payload["preprocessing"]["magnitude_weighting"] = magnitude_weighting
                            payload["preprocessing"]["scale_factor"] = scale_factor
                        
                        # Add threshold if configured
                        if use_threshold:
                            payload["threshold"] = {
                                "threshold": threshold_value
                            }
                        
                        # Add dimension weights if configured
                        if use_dimension_weights and weights:
                            payload["dimension_weights"] = {
                                "weights": weights
                            }
                    
                    # Make the API request
                    start_time = time.time()
                    response = requests.post(SEARCH_API, json=payload)
                    request_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.search_results = result
                        st.session_state.search_query = query_text or "Vector Query"
                        st.session_state.search_collection = search_collection
                        st.session_state.search_time = request_time
                        
                        # Rerun to display results in clean state
                        st.rerun()
                    else:
                        # Handle error response
                        error_message = "Unknown error"
                        try:
                            error_detail = response.json().get("detail", response.text)
                            error_message = error_detail
                        except:
                            error_message = response.text
                        
                        with results_area:
                            st.error(f"Error: {response.status_code} - {error_message}")
                            
                            # Suggest fixes based on error type
                            if response.status_code == 404:
                                st.info(f"The collection '{search_collection}' may not exist. Please check the collection name.")
                            elif response.status_code == 400:
                                st.info("Ensure you've provided either a text query or a valid vector query.")
                            elif response.status_code >= 500:
                                st.info("There was a server error. Please try again later or try a simpler query.")
                except Exception as e:
                    with results_area:
                        st.error(f"An error occurred: {str(e)}")
                        st.info("Check your network connection and ensure the API endpoint is accessible.")


def display_search_results(result):
    """Display search results with dark theme styling"""
    # Display search context
    st.markdown(f"""
        <div style="background-color: #1E2129; border-radius: 10px; padding: 15px; margin-bottom: 20px; border: 1px solid rgba(255, 255, 255, 0.05);">
            <div style="font-size: 0.9rem; opacity: 0.7;">Search Query</div>
            <div style="font-size: 1.2rem; font-weight: 500; margin-top: 5px;">"{st.session_state.search_query}"</div>
            <div style="font-size: 0.8rem; opacity: 0.6; margin-top: 10px;">Collection: {st.session_state.search_collection}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Display search statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_stats(
            "Results Found", 
            result.get("total_found", 0),
            "matching documents"
        )
    with col2:
        render_stats(
            "Search Method", 
            result.get("metric_used", "Unknown"),
            "similarity algorithm"
        )
    with col3:
        search_time = result.get("search_time_ms", round(st.session_state.search_time * 1000, 2))
        render_stats(
            "Search Time", 
            f"{search_time} ms",
            "end-to-end processing"
        )
    
    # Display results
    results = result.get("results", [])
    
    if not results:
        st.info("No results found. Try a different query or collection.")
        return
    
    # Create a tabbed view for results
    result_tabs = st.tabs(["Card View", "Table View", "Raw JSON"])
    
    # Card View - Fixed Version
    with result_tabs[0]:
        for i, item in enumerate(results):
            score = item.get("score", 0)
            result_id = item.get("id", "")
            payload = item.get("payload", {})
            
            # Extract text and metadata from payload
            text = payload.get("text", "No text available")
            
            # Create a regular Streamlit container instead of HTML
            with st.container():
                # Header with result number and score
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### Result {i+1}")
                with col2:
                    st.markdown(f"<p style='text-align: right; color: #4B56D2; font-weight: bold; font-size: 1.2rem;'>{score:.4f}</p>", unsafe_allow_html=True)
                
                # Text content
                st.markdown(f"<div style='background-color: #1a1a2e; padding: 10px; border-radius: 5px; border-left: 3px solid #4B56D2;'>{text}</div>", unsafe_allow_html=True)
                
                # ID information
                st.markdown(f"<small>ID: {result_id}</small>", unsafe_allow_html=True)
                
                # Metadata
                metadata = {k: v for k, v in payload.items() if k != "text"}
                if metadata:
                    with st.expander("Metadata"):
                        st.json(metadata)
                
                st.divider()
    
    # Table View
    with result_tabs[1]:
        # Prepare data for table
        table_data = []
        for i, item in enumerate(results):
            score = item.get("score", 0)
            id = item.get("id", "")
            payload = item.get("payload", {})
            
            text = payload.get("text", "No text available")
            # Truncate text for table view
            text_preview = text[:100] + "..." if len(text) > 100 else text
            
            # Get a few key metadata fields
            source = payload.get("source", "")
            category = payload.get("category", "")
            
            table_data.append({
                "Rank": i+1,
                "Score": round(score, 4),
                "ID": id,
                "Text Preview": text_preview,
                "Source": source,
                "Category": category
            })
        
        # Create and display dataframe
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True)
    
    # Raw JSON
    with result_tabs[2]:
        st.json(results)
    
    # Export options
    col1, col2 = st.columns(2)
    with col1:
        # CSV export
        csv_data = pd.DataFrame([{
            "rank": i+1,
            "score": item.get("score", 0),
            "id": item.get("id", ""),
            "text": item.get("payload", {}).get("text", ""),
            **{k: v for k, v in item.get("payload", {}).items() if k != "text"}
        } for i, item in enumerate(results)])
        
        csv = csv_data.to_csv(index=False)
        st.download_button(
            label="Export as CSV",
            data=csv,
            file_name="search_results.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # JSON export
        export_data = json.dumps(results, indent=2)
        st.download_button(
            label="Export as JSON",
            data=export_data,
            file_name="search_results.json",
            mime="application/json",
            use_container_width=True
        )