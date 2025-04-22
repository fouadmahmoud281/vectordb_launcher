import streamlit as st
import requests
import json
import numpy as np
import pandas as pd
import time
from utils import EMBED_API, card_container, render_stats

def render_embed_tab():
    """Render the Create Embeddings tab with dark theme styling"""
    st.header("Create Embeddings")
    st.markdown("<p style='opacity: 0.7;'>Generate vector embeddings from text to enable semantic search and similarity matching.</p>", unsafe_allow_html=True)
    
    # Stats cards for embedding info
    if 'total_embeddings' not in st.session_state:
        st.session_state.total_embeddings = 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        render_stats(
            "Total Embeddings Created", 
            st.session_state.total_embeddings,
            "Across all sessions"
        )
    with col2:
        render_stats(
            "Current Model", 
            "Sentence Transformer",
            "384-dimensional vectors"
        )
    with col3:
        render_stats(
            "Processing Rate", 
            "~500 texts/sec",
            "Performance may vary by length"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main embedding card
    card_container(lambda: embedding_card_content())
    
    # Previously generated embeddings
    if 'embeddings_history' in st.session_state and st.session_state.embeddings_history:
        st.subheader("Recent Embeddings")
        for i, item in enumerate(st.session_state.embeddings_history):
            with st.expander(f"Embedding {i+1}: {item['text'][:50]}..."):
                st.markdown(f"**Original Text:** {item['text']}")
                
                # Display embedding preview with heatmap
                st.markdown("**Embedding Visualization:**")
                
                # Create a heatmap of the embedding
                embedding_array = np.array(item['embedding'])
                
                # Reshape for visualization if it's a large embedding
                vis_width = min(16, len(embedding_array))
                vis_height = min(16, len(embedding_array) // vis_width)
                
                if len(embedding_array) > vis_width * vis_height:
                    heatmap_data = embedding_array[:vis_width * vis_height].reshape(vis_height, vis_width)
                else:
                    heatmap_data = embedding_array.reshape(1, -1)
                
                st.markdown("<div style='background-color: #181818; padding: 10px; border-radius: 5px;'>", unsafe_allow_html=True)
                
                # Create a heatmap using a DataFrame
                df = pd.DataFrame(heatmap_data)
                st.dataframe(
                    df.style.background_gradient(cmap="viridis", axis=None),
                    use_container_width=True,
                    height=200
                )
                
                st.markdown("</div>", unsafe_allow_html=True)
                st.caption("Showing a snippet of the embedding values as a heatmap visualization.")
                
                # Download option
                st.download_button(
                    label="Download Full Embedding",
                    data=json.dumps({"text": item['text'], "embedding": item['embedding']}),
                    file_name=f"embedding_{i+1}.json",
                    mime="application/json"
                )

def embedding_card_content():
    """Content for the embedding creation card"""
    # Option to input multiple texts
    text_input_method = st.radio(
        "Input method",
        ["Single text", "Multiple texts (one per line)"],
        horizontal=True
    )
    
    if text_input_method == "Single text":
        input_text = st.text_area("Enter text to embed", height=150, 
                                placeholder="Enter the text you want to convert to a vector embedding...")
        texts_to_embed = [input_text] if input_text else []
    else:
        input_texts = st.text_area("Enter texts to embed (one per line)", height=150,
                                  placeholder="Enter multiple texts, one per line...\nEach line will be converted to a separate embedding.")
        texts_to_embed = [text.strip() for text in input_texts.split('\n') if text.strip()]
    
    col1, col2 = st.columns([3, 1])
    with col1:
        generate_button = st.button(
            "Generate Embeddings", 
            type="primary",
            use_container_width=True,
            disabled=not texts_to_embed
        )
    with col2:
        batch_size = st.number_input("Batch Size", min_value=1, max_value=100, value=10)
    
    if generate_button:
        if texts_to_embed:
            with st.spinner(f"Generating embeddings for {len(texts_to_embed)} text(s)..."):
                # Progress bar
                progress_bar = st.progress(0)
                
                # Use batching for multiple texts
                all_embeddings = []
                total_batches = (len(texts_to_embed) + batch_size - 1) // batch_size
                
                start_time = time.time()
                
                for i in range(0, len(texts_to_embed), batch_size):
                    batch = texts_to_embed[i:i + batch_size]
                    
                    # Update progress
                    progress = (i / len(texts_to_embed)) if len(texts_to_embed) > 0 else 0
                    progress_bar.progress(progress)
                    
                    try:
                        response = requests.post(EMBED_API, json=batch)
                        
                        if response.status_code == 200:
                            result = response.json()
                            batch_embeddings = result.get("embeddings", [])
                            all_embeddings.extend(batch_embeddings)
                        else:
                            st.error(f"Error in batch {i//batch_size + 1}: {response.status_code} - {response.text}")
                            break
                    except Exception as e:
                        st.error(f"Error in batch {i//batch_size + 1}: {str(e)}")
                        break
                
                # Complete progress bar
                progress_bar.progress(1.0)
                
                # Calculate processing time
                total_time = time.time() - start_time
                texts_per_second = len(texts_to_embed) / total_time if total_time > 0 else 0
                
                # Update session state
                if 'embeddings_history' not in st.session_state:
                    st.session_state.embeddings_history = []
                
                # Store only the first few embeddings in history to avoid memory issues
                max_history = 5
                for i, (text, embedding) in enumerate(zip(texts_to_embed[:max_history], all_embeddings[:max_history])):
                    st.session_state.embeddings_history.append({
                        'text': text,
                        'embedding': embedding
                    })
                
                # Keep history at a reasonable size
                if len(st.session_state.embeddings_history) > max_history:
                    st.session_state.embeddings_history = st.session_state.embeddings_history[-max_history:]
                
                # Update total embeddings count
                st.session_state.total_embeddings += len(all_embeddings)
                
                # Show success message
                st.success(f"Successfully generated {len(all_embeddings)} embeddings in {total_time:.2f} seconds ({texts_per_second:.1f} texts/sec)")
                
                # Display embedding info
                if all_embeddings:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        render_stats(
                            "Embeddings Created", 
                            len(all_embeddings),
                            "in this batch"
                        )
                    
                    with col2:
                        embedding_dim = len(all_embeddings[0]) if all_embeddings else 0
                        render_stats(
                            "Vector Dimension", 
                            embedding_dim,
                            "elements per vector"
                        )
                    
                    with col3:
                        render_stats(
                            "Processing Speed", 
                            f"{texts_per_second:.1f} texts/sec",
                            f"Total time: {total_time:.2f}s"
                        )
                    
                    # Option to download all embeddings
                    st.download_button(
                        label="Download All Embeddings",
                        data=json.dumps({"embeddings": all_embeddings, "texts": texts_to_embed}),
                        file_name="embeddings_batch.json",
                        mime="application/json",
                        use_container_width=True
                    )
        else:
            st.warning("Please enter text to embed")