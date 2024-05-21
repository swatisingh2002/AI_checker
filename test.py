import streamlit as st
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch
import nltk
from nltk.probability import FreqDist
import plotly.express as px
from collections import Counter
from nltk.corpus import stopwords
import string

# Ensure necessary NLTK data packages are downloaded
nltk.download('punkt')
nltk.download('stopwords')

# Load GPT-2 tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')

def calculate_perplexity(text):
    # Tokenize the text and convert to input IDs
    encoded_input = tokenizer.encode(text, add_special_tokens=True, return_tensors='pt')

    # Move input and model to the appropriate device (CPU or GPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    encoded_input = encoded_input.to(device)
    model.to(device)

    with torch.no_grad():
        outputs = model(encoded_input, labels=encoded_input)
        loss = outputs.loss
        perplexity = torch.exp(loss)
    return perplexity.item()

def calculate_burstiness(text):
    tokens = nltk.word_tokenize(text.lower())
    word_freq = FreqDist(tokens)
    repeated_count = sum(count > 1 for count in word_freq.values())
    burstiness_score = repeated_count / len(word_freq)
    return burstiness_score

def plot_top_repeated_words(text):
    # Tokenize the text and remove stopwords and special characters
    tokens = text.split()
    stop_words = set(stopwords.words('english'))
    tokens = [token.lower() for token in tokens if token.lower() not in stop_words and token.lower() not in string.punctuation]

    # Count the occurrence of each word
    word_counts = Counter(tokens)

    # Get the top 15 most repeated words
    top_words = word_counts.most_common(15)

    # Extract the words and their counts for plotting
    words = [word for word, count in top_words]
    counts = [count for word, count in top_words]

    # Plot the bar chart using Plotly
    fig = px.bar(x=words, y=counts, labels={'x': 'Words', 'y': 'Counts'}, title='Top 15 Most Repeated Words')
    st.plotly_chart(fig, use_container_width=True)

st.set_page_config(layout="wide")

st.title("GPT Checker: AI Plagiarism Detector")
text_area = st.text_area("Enter the text you want to analyze", "")

if text_area is not None:
    if st.button("Analyze"):
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.info("Your Input Text")
            st.success(text_area)
        
        with col2:
            st.info("Detection Score (Perplexity Score and Burstiness Score)")
            perplexity = calculate_perplexity(text_area)
            burstiness_score = calculate_burstiness(text_area)

            st.write("Perplexity Score for the given text:", perplexity)
            st.write("Burstiness Score for the given text:", burstiness_score)

            if perplexity > 25000 and burstiness_score < 0.5:
                st.error("Text Analysis Result: AI generated content")
                st.error("The perplexity score is more than 25000 for this content and the burstiness score is less than 0.2")
            else:
                st.success("Text Analysis Result: Likely not generated by AI")
            
            st.warning("Disclaimer: AI plagiarism detector apps can assist in identifying potential instances of plagiarism; however, it is important to note that their results may not be entirely flawless or completely reliable. These tools employ advanced algorithms, but they can still produce false positives or false negatives. Therefore, it is recommended to use AI plagiarism detectors as a supplementary tool alongside human judgment and manual verification for accurate and comprehensive plagiarism detection.")
            
        with col3:
            st.info("Basic Details")
            plot_top_repeated_words(text_area)
