import re
import fitz  # PyMuPDF
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO


# Download required NLTK data
def download_nltk_data():
    """Download required NLTK data if not present"""
    resources = [
        ('tokenizers/punkt', 'punkt'),
        ('corpora/stopwords', 'stopwords'),
        ('tokenizers/punkt_tab', 'punkt_tab')
    ]

    for resource_path, resource_name in resources:
        try:
            nltk.data.find(resource_path)
        except LookupError:
            print(f"Downloading {resource_name}...")
            nltk.download(resource_name, quiet=True)


# Download NLTK data
download_nltk_data()


class ResumeAnalyzer:
    def __init__(self):
        try:
            self.stop_words = set(stopwords.words('english'))
        except LookupError:
            # Fallback: use basic stopwords if NLTK data not available
            print("Warning: NLTK stopwords not found. Using basic stopwords.")
            self.stop_words = set([
                'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
                'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
                'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them',
                'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this',
                'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
                'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
                'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
                'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
                'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to',
                'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
                'further', 'then', 'once'
            ])

        # Common technical skills and keywords
        self.skill_keywords = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php',
                            'swift', 'kotlin', 'go', 'rust', 'typescript', 'sql', 'r'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'nodejs', 'django',
                    'flask', 'fastapi', 'express', 'next.js', 'bootstrap', 'tailwind'],
            'data_science': ['machine learning', 'deep learning', 'nlp', 'tensorflow',
                             'pytorch', 'pandas', 'numpy', 'scikit-learn', 'data analysis',
                             'statistics', 'matplotlib', 'seaborn', 'tableau', 'power bi'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
                      'terraform', 'ansible', 'cicd', 'devops'],
            'database': ['mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
                         'oracle', 'cassandra', 'dynamodb'],
            'soft_skills': ['leadership', 'communication', 'teamwork', 'problem solving',
                            'analytical', 'creative', 'management', 'agile', 'scrum']
        }

    def extract_text_from_pdf(self, pdf_file):
        """Extract text from PDF file"""
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            return f"Error extracting text: {str(e)}"

    def clean_text(self, text):
        """Clean and preprocess text"""
        # Convert to lowercase
        text = text.lower()
        # Remove special characters and extra spaces
        text = re.sub(r'[^a-zA-Z0-9\s+#.]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_email(self, text):
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else "Not found"

    def extract_phone(self, text):
        """Extract phone number"""
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        return phones[0] if phones else "Not found"

    def extract_skills(self, text):
        """Extract skills from resume"""
        text_lower = text.lower()
        found_skills = {}

        for category, skills in self.skill_keywords.items():
            found = []
            for skill in skills:
                # Look for whole word matches
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    found.append(skill)
            if found:
                found_skills[category] = found

        return found_skills

    def get_word_frequency(self, text, top_n=20):
        """Get most frequent words"""
        cleaned_text = self.clean_text(text)

        try:
            tokens = word_tokenize(cleaned_text)
        except LookupError:
            # Fallback tokenization if NLTK punkt not available
            tokens = cleaned_text.split()

        # Filter tokens
        filtered_tokens = [
            word for word in tokens
            if word not in self.stop_words
               and len(word) > 2
               and word.isalpha()
        ]

        # Get frequency
        word_freq = Counter(filtered_tokens)
        return dict(word_freq.most_common(top_n))

    def generate_wordcloud(self, text):
        """Generate word cloud image"""
        cleaned_text = self.clean_text(text)

        # Remove stopwords
        try:
            tokens = word_tokenize(cleaned_text)
        except LookupError:
            tokens = cleaned_text.split()

        filtered_text = ' '.join([
            word for word in tokens
            if word not in self.stop_words and len(word) > 2
        ])

        # Generate word cloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            colormap='viridis',
            max_words=100
        ).generate(filtered_text)

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        plt.tight_layout(pad=0)

        # Save to bytes
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close()

        return buf

    def calculate_job_match(self, resume_text, job_description):
        """Calculate match percentage between resume and job description"""
        resume_clean = self.clean_text(resume_text)
        job_clean = self.clean_text(job_description)

        # Tokenize
        try:
            resume_tokens = set(word_tokenize(resume_clean))
            job_tokens = set(word_tokenize(job_clean))
        except LookupError:
            resume_tokens = set(resume_clean.split())
            job_tokens = set(job_clean.split())

        # Remove stopwords
        resume_tokens = {w for w in resume_tokens if w not in self.stop_words and len(w) > 2}
        job_tokens = {w for w in job_tokens if w not in self.stop_words and len(w) > 2}

        # Calculate match
        if not job_tokens:
            return 0, set(), set()

        matching_keywords = resume_tokens.intersection(job_tokens)
        missing_keywords = job_tokens - resume_tokens

        match_percentage = (len(matching_keywords) / len(job_tokens)) * 100

        return match_percentage, matching_keywords, missing_keywords

    def analyze_resume(self, pdf_file, job_description=None):
        """Complete resume analysis"""
        # Extract text
        text = self.extract_text_from_pdf(pdf_file)

        # Basic info
        email = self.extract_email(text)
        phone = self.extract_phone(text)

        # Skills
        skills = self.extract_skills(text)

        # Word frequency
        word_freq = self.get_word_frequency(text)

        # Word cloud
        wordcloud_img = self.generate_wordcloud(text)

        # Job match (if provided)
        job_match_data = None
        if job_description:
            match_pct, matching, missing = self.calculate_job_match(text, job_description)
            job_match_data = {
                'percentage': match_pct,
                'matching_keywords': matching,
                'missing_keywords': missing
            }

        return {
            'text': text,
            'email': email,
            'phone': phone,
            'skills': skills,
            'word_frequency': word_freq,
            'wordcloud': wordcloud_img,
            'job_match': job_match_data
        }