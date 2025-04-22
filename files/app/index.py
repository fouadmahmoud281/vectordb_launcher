import streamlit as st
import requests
import json
import numpy as np
from utils import INDEX_API

def render_index_tab():
    """Render the Index Documents tab"""
    st.header("Index Documents")
    
    collection_name = st.text_input("Collection Name", "my_collection")
    
    # Optional parameters with descriptions from the API endpoint
    with st.expander("Advanced Indexing Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            m_param = st.number_input(
                "M (connections per node)",
                min_value=0, max_value=64, value=0,
                help="Number of connections per node in the HNSW graph. Leave at 0 for auto-optimization. Valid range: 8-64."
            )
            
            ef_construction = st.number_input(
                "EF Construction",
                min_value=0, max_value=500, value=200,
                help="Construction time search scope. Higher values lead to better recall but slower indexing. Default: 200"
            )
        
        with col2:
            tune_parameters = st.checkbox(
                "Tune Parameters",
                value=False,
                help="Enable parameter tuning before indexing"
            )
            
            if tune_parameters:
                tune_vector_space = st.selectbox(
                    "Vector Space for Tuning",
                    ["cosine", "dot_product", "euclidean", "manhattan", "jaccard", "hamming", "text", "code"],
                    index=0,
                    help="Select the vector space to use for parameter tuning"
                )
                
                tune_sample_size = st.number_input(
                    "Tuning Sample Size",
                    min_value=10, max_value=1000, value=100,
                    help="Number of documents to sample for parameter tuning"
                )
                
                apply_best_params = st.checkbox(
                    "Apply Best Parameters",
                    value=False,
                    help="Apply the best parameters found during tuning"
                )
                
                store_tuning_results = st.checkbox(
                    "Store Tuning Results",
                    value=False,
                    help="Store the tuning results for later use"
                )
    
    # Document input
    st.subheader("Add Documents")
    
    # Initialize documents in session state if not exists
    if 'documents' not in st.session_state:
        st.session_state.documents = []
    
    # Stats dashboard for current documents
    if st.session_state.documents:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Documents Ready", len(st.session_state.documents))
        with col2:
            categories = set()
            for doc in st.session_state.documents:
                if doc.get('metadata', {}).get('category'):
                    categories.add(doc['metadata']['category'])
            st.metric("Categories", len(categories))
        with col3:
            avg_length = sum(len(doc.get('text', '')) for doc in st.session_state.documents) / len(st.session_state.documents) if st.session_state.documents else 0
            st.metric("Avg. Document Length", f"{avg_length:.0f} chars")
    
    # Form for adding a document
    with st.form("add_document_form"):
        doc_text = st.text_area("Document Text", height=100, 
                               help="The text content of the document to be indexed")
        
        # Metadata fields
        col1, col2 = st.columns(2)
        with col1:
            source = st.text_input("Source", help="The source of the document (e.g., article, book)")
            doc_id = st.text_input("ID", help="A unique identifier for the document")
        with col2:
            category = st.text_input("Category", help="The category or topic of the document")
            
            # Option to add custom metadata fields
            custom_metadata = st.text_area(
                "Custom Metadata (JSON format, optional)", 
                placeholder='{"field1": "value1", "field2": "value2"}',
                height=80,
                help="Additional metadata in JSON format"
            )
            
        # Add document button
        if st.form_submit_button("Add Document"):
            if doc_text:
                # Validate text content
                if not doc_text.strip():
                    st.warning("Document text cannot be empty or contain only whitespace")
                else:
                    metadata = {
                        "source": source,
                        "category": category,
                        "id": doc_id
                    }
                    
                    # Remove empty metadata fields
                    metadata = {k: v for k, v in metadata.items() if v}
                    
                    # Add custom metadata if provided
                    if custom_metadata:
                        try:
                            custom_fields = json.loads(custom_metadata)
                            metadata.update(custom_fields)
                        except json.JSONDecodeError:
                            st.warning("Invalid JSON format for custom metadata. Using only standard fields.")
                    
                    document = {
                        "text": doc_text,
                        "metadata": metadata
                    }
                    st.session_state.documents.append(document)
                    st.success("Document added!")
            else:
                st.warning("Document text is required")
    
    # Bulk upload option
    with st.expander("Bulk Upload Documents"):
        st.write("Upload a JSON file with documents in the format:")
        st.code('''
        [
          {
            "text": "Document text here",
            "metadata": {
              "source": "Source name",
              "category": "Category name",
              "id": "doc_id"
            }
          },
          ...
        ]
        ''')
        
        sample_data = [
            {
                "text": "The solar system consists of the Sun and everything that orbits around it, including planets, dwarf planets, moons, asteroids, comets, and meteoroids.",
                "metadata": {
                    "source": "Astronomy Textbook",
                    "category": "Astronomy",
                    "id": "astro-001"
                }
            },
            {
                "text": "Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize foods with carbon dioxide and water.",
                "metadata": {
                    "source": "Biology Journal",
                    "category": "Biology",
                    "id": "bio-001"
                }
            }
        ]
        
        if st.button("Load Sample Data"):
            st.session_state.documents.extend(sample_data)
            st.success(f"Added {len(sample_data)} sample documents!")
            st.rerun()
        
        uploaded_file = st.file_uploader("Choose a JSON file", type="json")
        if uploaded_file is not None:
            try:
                documents = json.load(uploaded_file)
                if isinstance(documents, list):
                    valid_docs = []
                    invalid_docs = []
                    
                    for doc in documents:
                        if isinstance(doc, dict) and "text" in doc and doc["text"].strip() and isinstance(doc.get("metadata", {}), dict):
                            valid_docs.append(doc)
                        else:
                            invalid_docs.append(doc)
                    
                    if valid_docs:
                        if st.button(f"Add {len(valid_docs)} valid documents from file"):
                            st.session_state.documents.extend(valid_docs)
                            st.success(f"Added {len(valid_docs)} documents from file!")
                            
                            if invalid_docs:
                                st.warning(f"Skipped {len(invalid_docs)} invalid documents")
                            
                            st.rerun()
                    else:
                        st.warning("No valid documents found in the file")
                else:
                    st.warning("The uploaded file does not contain a list of documents")
            except json.JSONDecodeError:
                st.error("Invalid JSON file")
    
    # Document management
    if st.session_state.documents:
        st.subheader("Document Management")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Add filtering options
            if len(st.session_state.documents) > 5:
                filter_options = ["All"]
                # Get unique categories
                categories = set()
                for doc in st.session_state.documents:
                    cat = doc['metadata'].get('category', 'Uncategorized')
                    categories.add(cat)
                
                filter_options.extend(sorted(categories))
                selected_filter = st.selectbox("Filter by category", filter_options)
            else:
                selected_filter = "All"
        
        with col2:
            # Document management buttons
            if st.button("Clear All Documents"):
                st.session_state.documents = []
                st.rerun()
            
            # Export documents option
            if st.download_button(
                "Export Documents",
                data=json.dumps(st.session_state.documents, indent=2),
                file_name="documents.json",
                mime="application/json"
            ):
                st.success(f"Exported {len(st.session_state.documents)} documents")
        
        # Display documents
        for i, doc in enumerate(st.session_state.documents):
            category = doc['metadata'].get('category', 'Uncategorized')
            if selected_filter == "All" or selected_filter == category:
                with st.expander(f"Document {i+1}: {doc['text'][:50]}..." + (f" ({category})" if category else "")):
                    st.write(f"**Text**: {doc['text']}")
                    st.write("**Metadata**:")
                    st.json(doc['metadata'])
                    
                    col1, col2 = st.columns([4, 1])
                    with col2:
                        if st.button(f"Remove", key=f"remove_{i}"):
                            st.session_state.documents.pop(i)
                            st.rerun()
    
    # Index documents button and options
    st.subheader("Index Documents")
    
    if st.button("Index Documents", type="primary"):
        if not collection_name:
            st.warning("Please enter a collection name")
        elif not st.session_state.documents:
            st.warning("Please add at least one document")
        else:
            with st.spinner(f"Indexing {len(st.session_state.documents)} documents to collection '{collection_name}'..."):
                try:
                    # Build the URL with parameters
                    url = INDEX_API.format(collection_name=collection_name)
                    params = {}
                    
                    if m_param > 0:
                        # Validate M parameter range as per API
                        if 8 <= m_param <= 64:
                            params["m"] = m_param
                        else:
                            st.warning("M parameter must be between 8 and 64. Using auto-optimization instead.")
                    
                    if ef_construction > 0:
                        params["ef_construction"] = ef_construction
                    
                    # Prepare the payload
                    payload = {
                        "documents": st.session_state.documents,
                        "tune_parameters": tune_parameters
                    }
                    
                    # Add tuning parameters if enabled
                    if tune_parameters:
                        payload["tune_vector_space"] = tune_vector_space
                        payload["tune_sample_size"] = tune_sample_size
                        payload["apply_best_params"] = apply_best_params
                        payload["store_tuning_results"] = store_tuning_results
                        
                        # Add a minimal param grid for tuning (can be expanded)
                        payload["tune_param_grid"] = [{
                            "name": tune_vector_space,
                            "parameters": {}  # Let the API use defaults
                        }]
                    
                    # Make the API request
                    response = requests.post(url, params=params, json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Display success message with details
                        st.success(f"Successfully indexed documents in collection '{collection_name}'!")
                        
                        # Create detailed result display
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Documents Indexed", result.get("indexed_count", 0))
                            st.write(f"**Message**: {result.get('message', 'Indexing completed')}")
                        
                        with col2:
                            # Display any tuning results if available
                            if "tuning_results" in result:
                                st.write("**Tuning Results**:")
                                st.json(result["tuning_results"])
                            
                            if "parameter_note" in result:
                                st.info(result["parameter_note"])
                            
                            if "tuning_file" in result:
                                st.write(f"**Tuning File**: {result['tuning_file']}")
                        
                        # Option to clear documents after successful indexing
                        if st.button("Clear Indexed Documents"):
                            st.session_state.documents = []
                            st.rerun()
                    else:
                        error_message = "Unknown error"
                        try:
                            error_detail = response.json().get("detail", response.text)
                            error_message = error_detail
                        except:
                            error_message = response.text
                        
                        st.error(f"Error: {response.status_code} - {error_message}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")