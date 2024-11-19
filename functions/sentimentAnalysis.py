import nltk
from textblob import TextBlob
from nltk.sentiment import SentimentIntensityAnalyzer

testimonial = TextBlob("Textblob is amazingly simple to use. What great fun!")
testimonial.sentiment
testimonial.sentiment.polarity

# Download VADER lexicon
nltk.download('vader_lexicon')
# Initialize VADER sentiment analyzer
sid = SentimentIntensityAnalyzer()
# Sample text for sentiment analysis
text = "I love this product! It's amazing."
# Perform sentiment analysis
sentiment_score = sid.polarity_scores(text)
# Print sentiment score
print(sentiment_score)