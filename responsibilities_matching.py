from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from extract_responsiblity import extract_responsibilities

# Used TF-IDF Method
def responsiblity_matcher(resume_text, JD): #JD refers to Job_Description
    if not resume_text or not JD:
        return 0

    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,2))

    tfidf = vectorizer.fit_transform([resume_text, JD])

    similarity = cosine_similarity(tfidf[0], tfidf[1])
    score = similarity[0][0]
    return score * 100
# Testing Purposes
# jd_responsibilities = extract_responsibilities(
#     job_description
# )


# responsibility_score = responsiblity_matcher(
#     resume_experience,
#    job_description
# )

# print(
#     "Responsibilities score:",
#     round(responsibility_score, 2),
#     "%"
# )