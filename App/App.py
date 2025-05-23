# Developed by Parth Sarthi & Machint Sethi

###### Packages Used ######
import streamlit as st # core package used in this project
import pandas as pd
import base64, random
import time,datetime
import pymysql
import os
import socket
import platform
import geocoder
import secrets
import io,random
import plotly.express as px # to create visualisations at the admin session
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
import spacy
import textstat
import re
import pdfplumber

# libraries used to parse the pdf files
from sklearn.feature_extraction.text import TfidfVectorizer
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from streamlit_tags import st_tags
from PIL import Image
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos
import nltk
nltk.download('stopwords')
from spellchecker import SpellChecker
from collections import Counter
from fuzzywuzzy import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer()
nlp = spacy.load("en_core_web_sm")
spell = SpellChecker()




###### Setting Page Configuration (favicon, Logo, Title) ######

st.set_page_config(
   page_title="Resume Analyzer",
   page_icon='./Logo/recommend.png',
)


from streamlit_lottie import st_lottie
import json
import requests

############ Top Page Animation ############
def load_lottieurl_Top(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

if "top_loaded" not in st.session_state:
    st.session_state.top_loaded = False

if not st.session_state.top_loaded:
    lottie_animation = load_lottieurl_Top("https://lottie.host/da5c87bf-30c8-4031-8023-7f7b60e2bab1/wyaiQq7tdQ.json")
    animation_placeholder_top = st.empty()
    with animation_placeholder_top:
        st_lottie(lottie_animation, height=300, key="loading_top")
        time.sleep(3)
    animation_placeholder_top.empty()
    st.session_state.top_loaded = True




############ Default Animation Function ############
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_animation1 = load_lottieurl("https://lottie.host/d69cae00-01a6-4467-8ee2-6bafe5ce0cbb/iiGconSyqF.json")

def show_loading_animation():
    animation_placeholder_mid = st.empty()
    with animation_placeholder_mid:
        st_lottie(lottie_animation1, height=300, key="loading_mid")  # ✅ DIFFERENT KEY
        time.sleep(3)
    animation_placeholder_mid.empty()

# show_loading_animation()




###### Preprocessing functions ######

def extract_text_from_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.lower()

# Generates a link allowing the data in a given panda dataframe to be downloaded in csv format 
def get_csv_download_link(df,filename,text):
    csv = df.to_csv(index=False)
    ## bytes conversions
    b64 = base64.b64encode(csv.encode()).decode()      
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


# Reads Pdf file and check_extractable
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    ## close open handles
    converter.close()
    fake_file_handle.close()
    return text


# show uploaded file path to view pdf_display
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# # course recommendations which has data already loaded from Courses.py
# def course_recommender(course_list):
#     st.subheader("**Courses & Certificates Recommendations 👨‍🎓**")
#     c = 0
#     rec_course = []
#     ## slider to choose from range 1-10
#     no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
#     random.shuffle(course_list)
#     for c_name, c_link in course_list:
#         c += 1
#         st.markdown(f"({c}) [{c_name}]({c_link})")
#         rec_course.append(c_name)
#         if c == no_of_reco:
#             break
#     return rec_course


###### Database Stuffs ######


# sql connector
connection = pymysql.connect(host='localhost',user='root',password='Parth@123',db='cv')
cursor = connection.cursor()


# inserting miscellaneous data, fetched results, prediction and recommendation into user_data table
def insert_data(sec_token,ip_add,host_name,dev_user,os_name_ver,latlong,city,state,country,act_name,act_mail,act_mob,name,email,res_score,timestamp,no_of_pages,reco_field,cand_level,skills,recommended_skills,courses,pdf_name):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (str(sec_token),str(ip_add),host_name,dev_user,os_name_ver,str(latlong),city,state,country,act_name,act_mail,act_mob,name,email,str(res_score),timestamp,str(no_of_pages),reco_field,cand_level,skills,recommended_skills,courses,pdf_name)
    cursor.execute(insert_sql, rec_values)
    connection.commit()


# inserting feedback data into user_feedback table
def insertf_data(feed_name,feed_email,feed_score,comments,Timestamp):
    DBf_table_name = 'user_feedback'
    insertfeed_sql = "insert into " + DBf_table_name + """
    values (0,%s,%s,%s,%s,%s)"""
    rec_values = (feed_name, feed_email, feed_score, comments, Timestamp)
    cursor.execute(insertfeed_sql, rec_values)
    connection.commit()

#############################################################################
job_roles = {
    'Data Science': {
        'python': 0.9, 'machine learning': 0.9, 'data analysis': 0.8, 'pandas': 0.7, 'numpy': 0.7,
        'sql': 0.8, 'tensorflow': 0.9, 'keras': 0.8, 'pytorch': 0.8, 'scikit-learn': 0.8,
        'matplotlib': 0.6, 'seaborn': 0.6, 'statistics': 0.7, 'data visualization': 0.7,
        'deep learning': 0.9
    },
    'Web Development': {
        'html': 0.8, 'css': 0.8, 'javascript': 0.9, 'react': 0.9, 'angular': 0.8, 'vue.js': 0.8,
        'node.js': 0.9, 'express.js': 0.8, 'php': 0.7, 'laravel': 0.8, 'django': 0.8,
        'flask': 0.7, 'sql': 0.7, 'mongodb': 0.7, 'git': 0.6
    },
    'Mobile App Development': {
        'java': 0.9, 'kotlin': 0.9, 'swift': 0.9, 'objective-c': 0.8, 'flutter': 0.8,
        'react native': 0.8, 'xcode': 0.7, 'android studio': 0.7, 'firebase': 0.7,
        'dart': 0.7, 'ui/ux design': 0.6
    },
    'UI/UX Design': {
        'adobe xd': 0.9, 'figma': 0.9, 'sketch': 0.8, 'invision': 0.7, 'photoshop': 0.8,
        'illustrator': 0.8, 'prototyping': 0.8, 'wireframing': 0.8, 'user research': 0.7,
        'usability testing': 0.7, 'interaction design': 0.7
    },
    'Cybersecurity': {
        'network security': 0.9, 'information security': 0.9, 'penetration testing': 0.8,
        'ethical hacking': 0.8, 'firewalls': 0.7, 'encryption': 0.7, 'vulnerability assessment': 0.8,
        'incident response': 0.8, 'security protocols': 0.7, 'siem': 0.7
    },
    'Cloud Computing': {
        'aws': 0.9, 'azure': 0.9, 'google cloud': 0.9, 'devops': 0.8, 'docker': 0.8,
        'kubernetes': 0.8, 'terraform': 0.7, 'ci/cd': 0.8, 'cloud architecture': 0.8,
        'serverless': 0.7
    },
    'DevOps': {
        'jenkins': 0.8, 'ansible': 0.8, 'docker': 0.9, 'kubernetes': 0.9, 'terraform': 0.8,
        'ci/cd': 0.9, 'git': 0.8, 'linux': 0.7, 'monitoring': 0.7, 'scripting': 0.7
    },
    'Digital Marketing': {
        'seo': 0.9, 'sem': 0.9, 'google analytics': 0.8, 'content marketing': 0.8,
        'social media marketing': 0.8, 'email marketing': 0.7, 'ppc': 0.7, 'adwords': 0.7,
        'marketing automation': 0.7, 'crm': 0.6
    },
    'Project Management': {
        'project planning': 0.9, 'agile': 0.9, 'scrum': 0.8, 'kanban': 0.7, 'jira': 0.7,
        'risk management': 0.8, 'budgeting': 0.7, 'stakeholder management': 0.8,
        'communication': 0.8, 'leadership': 0.8
    },
    'Business Analysis': {
        'business process modeling': 0.8, 'requirement gathering': 0.9, 'data analysis': 0.8,
        'sql': 0.7, 'excel': 0.7, 'power bi': 0.7, 'tableau': 0.7, 'stakeholder communication': 0.8,
        'documentation': 0.7, 'problem-solving': 0.8
    },
    'Graphic Design': {
        'photoshop': 0.9, 'illustrator': 0.9, 'indesign': 0.8, 'coreldraw': 0.7, 'creativity': 0.8,
        'typography': 0.8, 'branding': 0.8, 'layout design': 0.7, 'color theory': 0.7,
        'visual communication': 0.8
    },
    'Accounting & Finance': {
        'accounting principles': 0.9, 'financial analysis': 0.9, 'budgeting': 0.8, 'forecasting': 0.8,
        'quickbooks': 0.7, 'excel': 0.8, 'taxation': 0.8, 'auditing': 0.8, 'payroll': 0.7,
        'compliance': 0.8
    },
    'Human Resources': {
        'recruitment': 0.9, 'employee relations': 0.8, 'performance management': 0.8,
        'training and development': 0.8, 'hr policies': 0.7, 'compliance': 0.8, 'payroll': 0.7,
        'benefits administration': 0.7, 'hr software': 0.7, 'onboarding': 0.8
    },
    'Sales': {
        'lead generation': 0.9, 'crm': 0.8, 'negotiation': 0.8, 'sales strategy': 0.8,
        'customer relationship management': 0.8, 'market research': 0.7, 'cold calling': 0.7,
        'product knowledge': 0.8, 'salesforce': 0.7, 'closing deals': 0.9
    },
    'Customer Service': {
        'communication': 0.9, 'problem-solving': 0.8, 'crm': 0.8, 'customer support': 0.9,
        'conflict resolution': 0.8, 'empathy': 0.8, 'product knowledge': 0.8,
        'ticketing systems': 0.7, 'multitasking': 0.7, 'feedback handling': 0.7
    },
    'Content Writing': {
        'seo': 0.9, 'copywriting': 0.9, 'editing': 0.8, 'proofreading': 0.8, 'content strategy': 0.8,
        'wordpress': 0.7, 'research': 0.8, 'grammar': 0.9, 'creativity': 0.8, 'storytelling': 0.8
    },
    'Data Entry': {
        'typing': 0.9, 'data accuracy': 0.9, 'excel': 0.8, 'attention to detail': 0.9,
        'database management': 0.8, 'time management': 0.8, 'ms office': 0.8,
        'data validation': 0.8, 'organization': 0.8, 'confidentiality': 0.8
    },
    'Teaching & Education': {
        'lesson planning': 0.9, 'classroom management': 0.9, 'curriculum development': 0.8,
        'assessment': 0.8, 'communication': 0.9, 'patience': 0.8, 'subject expertise': 0.9,
        'technology integration': 0.7, 'student engagement': 0.8, 'adaptability': 0.8
    },
    'Healthcare': {
        'patient care': 0.9, 'medical terminology': 0.9, 'clinical skills': 0.9, 'emr': 0.8,
        'vital signs monitoring': 0.8, 'infection control': 0.8, 'medication administration': 0.8,
        'communication': 0.8, 'compassion': 0.9, 'teamwork': 0.8
    }
}
# Count skill frequency from resume text
# def count_skill_frequency(resume_text, job_keywords):
#     resume_text = resume_text.lower()
#     return sum(1 for skill in job_keywords if skill.lower() in resume_text)
def count_skill_weighted_frequency(resume_text, job_keywords_with_weights):
    resume_text = resume_text.lower()
    score = 0
    for skill, weight in job_keywords_with_weights.items():
        score += resume_text.count(skill.lower()) * weight
    return score

# Predict most likely job role based on keyword match
def predict_job_role(resume_text):
    max_score = 0
    predicted_role = None
    for role, keywords in job_roles.items():
        score = count_skill_weighted_frequency(resume_text, keywords)
        if score > max_score:
            max_score = score
            predicted_role = role
    return predicted_role, max_score

# Recommend missing skills for a given role
def recommend_missing_skills(resume_text, predicted_role):
    resume_text = resume_text.lower()
    role_keywords = job_roles.get(predicted_role, [])
    return [skill for skill in role_keywords if skill.lower() not in resume_text]



#########################################################################

course_catalog = {
    # Data Science
    "python": "https://www.coursera.org/specializations/python",
    "machine learning": "https://www.coursera.org/learn/machine-learning",
    "data analysis": "https://www.coursera.org/specializations/data-analysis",
    "pandas": "https://www.datacamp.com/courses/pandas-foundations",
    "numpy": "https://www.datacamp.com/courses/intro-to-python-for-data-science",
    "sql": "https://www.coursera.org/learn/sql-for-data-science",
    "tensorflow": "https://www.coursera.org/learn/introduction-tensorflow",
    "keras": "https://www.coursera.org/learn/deep-neural-networks-with-keras",
    "pytorch": "https://www.udacity.com/course/deep-learning-pytorch--ud188",
    "scikit-learn": "https://www.datacamp.com/courses/supervised-learning-with-scikit-learn",
    "matplotlib": "https://www.datacamp.com/courses/introduction-to-data-visualization-with-python",
    "seaborn": "https://www.datacamp.com/courses/introduction-to-data-visualization-with-seaborn",
    "statistics": "https://www.coursera.org/learn/basic-statistics",
    "data visualization": "https://www.coursera.org/specializations/data-visualization",
    "deep learning": "https://www.coursera.org/specializations/deep-learning",

    # Web Development
    "html": "https://www.freecodecamp.org/learn/responsive-web-design/",
    "css": "https://www.codecademy.com/learn/learn-css",
    "javascript": "https://www.codecademy.com/learn/introduction-to-javascript",
    "react": "https://www.codecademy.com/learn/react-101",
    "angular": "https://www.coursera.org/learn/single-page-web-apps-with-angularjs",
    "vue.js": "https://www.udemy.com/course/vuejs-2-the-complete-guide/",
    "node.js": "https://www.coursera.org/learn/server-side-nodejs",
    "express.js": "https://www.udemy.com/course/the-complete-nodejs-developer-course-2/",
    "php": "https://www.codecademy.com/learn/learn-php",
    "laravel": "https://www.udemy.com/course/php-with-laravel-for-beginners-become-a-master-in-laravel/",
    "django": "https://www.coursera.org/learn/django",
    "flask": "https://www.udemy.com/course/python-and-flask-bootcamp-create-websites-using-flask/",
    "mongodb": "https://www.mongodb.com/learn/mongodb-university",
    "git": "https://www.codecademy.com/learn/learn-git",

    # Mobile App Development
    "java": "https://www.udemy.com/course/java-the-complete-java-developer-course/",
    "kotlin": "https://www.udacity.com/course/kotlin-for-android-developers--ud888",
    "swift": "https://www.udacity.com/course/ios-developer-nanodegree--nd003",
    "objective-c": "https://www.udemy.com/course/objective-c-for-beginners/",
    "flutter": "https://www.udemy.com/course/flutter-bootcamp-with-dart/",
    "react native": "https://www.coursera.org/learn/react-native",
    "xcode": "https://developer.apple.com/xcode/",
    "android studio": "https://developer.android.com/studio",
    "firebase": "https://firebase.google.com/docs",
    "dart": "https://dart.dev/codelabs",
    "ui/ux design": "https://www.coursera.org/specializations/ui-ux-design",

    # UI/UX Design
    "adobe xd": "https://www.udemy.com/course/ui-ux-web-design-using-adobe-xd/",
    "figma": "https://www.udemy.com/course/learn-figma/",
    "sketch": "https://www.udemy.com/course/sketch-app-course/",
    "invision": "https://www.udemy.com/course/invision-course/",
    "photoshop": "https://www.udemy.com/course/adobe-photoshop-cc-essentials-training-course/",
    "illustrator": "https://www.udemy.com/course/adobe-illustrator-course/",
    "prototyping": "https://www.coursera.org/learn/prototyping-and-design",
    "wireframing": "https://www.coursera.org/learn/wireframing",
    "user research": "https://www.coursera.org/learn/user-research",
    "usability testing": "https://www.coursera.org/learn/usability-testing",
    "interaction design": "https://www.coursera.org/specializations/interaction-design",

    # Cybersecurity
    "network security": "https://www.coursera.org/learn/network-security",
    "information security": "https://www.coursera.org/learn/information-security-data",
    "penetration testing": "https://www.udemy.com/course/penetration-testing/",
    "ethical hacking": "https://www.udemy.com/course/learn-ethical-hacking-from-scratch/",
    "firewalls": "https://www.coursera.org/learn/firewalls",
    "encryption": "https://www.coursera.org/learn/cryptography",
    "vulnerability assessment": "https://www.udemy.com/course/vulnerability-assessment/",
    "incident response": "https://www.coursera.org/learn/incident-response",
    "security protocols": "https://www.coursera.org/learn/security-protocols",
    "siem": "https://www.udemy.com/course/siem-security-information-event-management/",
    
    # Cloud Computing
    "aws": "https://www.coursera.org/specializations/aws-fundamentals",
    "azure": "https://www.coursera.org/learn/introduction-to-azure",
    "google cloud": "https://www.coursera.org/specializations/gcp-fundamentals",
    "devops": "https://www.coursera.org/specializations/devops",
    "docker": "https://www.udemy.com/course/docker-mastery/",
    "kubernetes": "https://www.udemy.com/course/kubernetes-mastery/",
    "terraform": "https://www.udemy.com/course/terraform-beginner-to-advanced/",
    "ci/cd": "https://www.coursera.org/learn/continuous-integration",
    "cloud architecture": "https://www.coursera.org/learn/cloud-architecture",
    "serverless": "https://www.coursera.org/learn/serverless-applications",

    # DevOps
    "jenkins": "https://www.udemy.com/course/jenkins-from-zero-to-hero/",
    "ansible": "https://www.udemy.com/course/ansible-for-the-absolute-beginner/",
    "linux": "https://www.udemy.com/course/linux-for-beginners/",
    "monitoring": "https://www.coursera.org/learn/monitoring-and-logging",
    "scripting": "https://www.udemy.com/course/shell-scripting-tutorial-for-beginners/",

    # Digital Marketing
    "seo": "https://www.coursera.org/learn/seo-fundamentals",
    "sem": "https://www.coursera.org/learn/sem",
    "google analytics": "https://analytics.google.com/analytics/academy/",
    "content marketing": "https://www.coursera.org/learn/content-marketing",
    "social media marketing": "https://www.coursera.org/specializations/social-media-marketing",
    "email marketing": "https://www.coursera.org/learn/email-marketing",
    "ppc": "https://www.udemy.com/course/ppc-advertising/",
    "adwords": "https://skillshop.withgoogle.com/",
    "marketing automation": "https://www.coursera.org/learn/marketing-automation",
    "crm": "https://www.coursera.org/learn/crm",

    # Project Management
    "project planning": "https://www.coursera.org/learn/project-planning",
    "agile": "https://www.coursera.org/learn/agile-methodology",
    "scrum": "https://www.coursera.org/learn/scrum-methodology",
    "kanban": "https://www.coursera.org/learn/kanban",
    "jira": "https://www.udemy.com/course/jira-tutorial-a-complete-guide-for-beginners/",
    "risk management": "https://www.coursera.org/learn/risk-management",
    "budgeting": "https://www.coursera.org/learn/project-budgeting",
    "stakeholder management": "https://www.coursera.org/learn/stakeholder-management",
    "communication": "https://www.coursera.org/learn/communication-skills",
    "leadership": "https://www.coursera.org/learn/leadership-skills",

    # Business Analysis
    "business process modeling": "https://www.coursera.org/learn/business-process-modeling",
    "requirement gathering": "https://www.coursera.org/learn/requirement-gathering",
    "excel": "https://www.coursera.org/learn/excel",
    "power bi": "https://www.coursera.org/learn/power-bi",
    "tableau": "https://www.coursera.org/learn/tableau",
    "stakeholder communication": "https://www.coursera.org/learn/stakeholder-communication",
    "documentation": "https://www.coursera.org/learn/documentation",
    "problem-solving": "https://www.coursera.org/learn/problem-solving",

# Graphic Design
    "photoshop": "https://www.udemy.com/course/adobe-photoshop-cc-essentials-training-course/",
    "illustrator": "https://www.udemy.com/course/adobe-illustrator-course/",
    "indesign": "https://www.udemy.com/course/indesign-course/",
    "coreldraw": "https://www.udemy.com/course/coreldraw-course/",
    "creativity": "https://www.coursera.org/learn/creative-thinking",
    "typography": "https://www.coursera.org/learn/typography",
    "branding": "https://www.coursera.org/learn/branding",
    "layout design": "https://www.coursera.org/learn/layout-design",
    "color theory": "https://www.coursera.org/learn/color-theory",
    "visual communication": "https://www.coursera.org/learn/visual-communication",

    # Accounting & Finance
    "accounting principles": "https://www.coursera.org/learn/accounting-basics",
    "financial analysis": "https://www.coursera.org/learn/financial-analysis",
    "budgeting": "https://www.coursera.org/learn/project-budgeting",
    "forecasting": "https://www.coursera.org/learn/forecasting",
    "quickbooks": "https://www.udemy.com/course/quickbooks-online/",
    "excel": "https://www.coursera.org/learn/excel",
    "taxation": "https://www.udemy.com/course/taxation-fundamentals/",
    "auditing": "https://www.coursera.org/learn/auditing",
    "payroll": "https://www.udemy.com/course/payroll-accounting/",
    "compliance": "https://www.coursera.org/learn/compliance",

    # Human Resources
    "recruitment": "https://www.coursera.org/learn/recruitment",
    "employee relations": "https://www.coursera.org/learn/employee-relations",
    "performance management": "https://www.coursera.org/learn/performance-management",
    "training & development": "https://www.coursera.org/learn/training-development",
    "hr policies": "https://www.udemy.com/course/hr-policies-for-beginners/",
    "compliance": "https://www.coursera.org/learn/compliance",
    "payroll": "https://www.udemy.com/course/payroll-accounting/",
    "benefits administration": "https://www.coursera.org/learn/benefits-administration",
    "hr software": "https://www.udemy.com/course/hr-information-systems/",
    "onboarding": "https://www.coursera.org/learn/onboarding",

    # Sales
    "lead generation": "https://www.udemy.com/course/lead-generation-for-beginners/",
    "crm": "https://www.coursera.org/learn/crm",
    "negotiation": "https://www.coursera.org/learn/negotiation-skills",
    "sales strategy": "https://www.coursera.org/learn/sales-strategy",
    "customer relationship management": "https://www.coursera.org/learn/crm",
    "market research": "https://www.coursera.org/learn/market-research",
    "cold calling": "https://www.udemy.com/course/cold-calling-mastery/",
    "product knowledge": "https://www.udemy.com/course/product-knowledge/",
    "salesforce": "https://trailhead.salesforce.com/en/content/learn/modules/starting-with-salesforce",
    "closing deals": "https://www.udemy.com/course/sales-closing-techniques/",

    # Customer Service
    "communication": "https://www.coursera.org/learn/communication-skills",
    "problem-solving": "https://www.coursera.org/learn/problem-solving",
    "crm": "https://www.coursera.org/learn/crm",
    "customer support": "https://www.udemy.com/course/customer-service-excellence/",
    "conflict resolution": "https://www.coursera.org/learn/conflict-resolution-skills",
    "empathy": "https://www.coursera.org/learn/empowering-empathy",
    "product knowledge": "https://www.udemy.com/course/product-knowledge/",
    "ticketing systems": "https://www.udemy.com/course/help-desk-software-training/",
    "multitasking": "https://www.udemy.com/course/multitasking-tips/",
    "feedback handling": "https://www.udemy.com/course/handling-customer-feedback/",

    # Content Writing
    "seo": "https://www.coursera.org/learn/seo-fundamentals",
    "copywriting": "https://www.udemy.com/course/copywriting-for-beginners/",
    "editing": "https://www.coursera.org/learn/copy-editing",
    "proofreading": "https://www.udemy.com/course/proofreading-masterclass/",
    "content strategy": "https://www.coursera.org/learn/content-strategy",
    "wordpress": "https://www.udemy.com/course/wordpress-for-beginners-course/",
    "research": "https://www.coursera.org/learn/research-methods",
    "grammar": "https://www.udemy.com/course/english-grammar-bootcamp/",
    "creativity": "https://www.coursera.org/learn/creative-thinking",
    "storytelling": "https://www.coursera.org/learn/storytelling",

    # Data Entry
    "typing": "https://www.typingclub.com/",
    "data accuracy": "https://www.udemy.com/course/data-accuracy-and-data-quality/",
    "excel": "https://www.coursera.org/learn/excel",
    "attention to detail": "https://www.udemy.com/course/attention-to-detail-training/",
    "database management": "https://www.coursera.org/learn/database-management",
    "time management": "https://www.coursera.org/learn/work-smarter-not-harder",
    "ms office": "https://www.udemy.com/course/microsoft-office-training-course/",
    "data validation": "https://www.udemy.com/course/excel-data-validation/",
    "organization": "https://www.coursera.org/learn/organization-skills",
    "confidentiality": "https://www.udemy.com/course/data-privacy-and-confidentiality/",

    # Teaching & Education
    "lesson planning": "https://www.coursera.org/learn/lesson-planning",
    "classroom management": "https://www.coursera.org/learn/classroom-management",
    "curriculum development": "https://www.coursera.org/learn/curriculum-development",
    "assessment": "https://www.coursera.org/learn/educational-assessment",
    "communication": "https://www.coursera.org/learn/communication-skills",
    "patience": "https://www.udemy.com/course/patience-training/",
    "subject expertise": "https://www.coursera.org/learn/subject-specific-teaching",
    "technology integration": "https://www.coursera.org/learn/educational-technology",
    "student engagement": "https://www.coursera.org/learn/student-engagement",
    "adaptability": "https://www.udemy.com/course/adaptability-and-flexibility/",

    # Healthcare
    "patient care": "https://www.coursera.org/learn/patient-care",
    "medical terminology": "https://www.udemy.com/course/medical-terminology-course/",
    "clinical skills": "https://www.coursera.org/learn/clinical-skills",
    "emr": "https://www.udemy.com/course/electronic-medical-records-emr-training/",
    "vital signs monitoring": "https://www.coursera.org/learn/vital-signs",
    "infection control": "https://www.coursera.org/learn/infection-control",
    "medication administration": "https://www.udemy.com/course/medication-administration/",
    "communication": "https://www.coursera.org/learn/communication-skills",
    "compassion": "https://www.udemy.com/course/compassion-in-healthcare/",
    "teamwork": "https://www.coursera.org/learn/teamwork-skills",
}

# Recommend up to 5 courses for missing skills
def course_recommender(course_catalog, missing_skills):
    recommended = []
    for skill in missing_skills:
        if skill.lower() in course_catalog:
            recommended.append((skill, course_catalog[skill.lower()]))
        if len(recommended) >= 5:
            break
    return recommended
#################################################################################################################

#Scoring

# 🚀 Powerful action verbs
ACTION_WORDS = {
    "led", "developed", "created", "built", "managed", "designed", "increased", "reduced",
    "launched", "optimized", "streamlined", "implemented", "executed", "initiated", "improved",
    "deployed", "architected", "engineered", "automated", "formulated", "facilitated",
    "achieved", "enhanced", "resolved", "supervised", "orchestrated", "coordinated",
    "monitored", "analyzed", "proposed", "revamped"
}

# 💬 Real-world soft skills
SOFT_SKILLS = {
    "teamwork", "communication", "leadership", "collaboration", "adaptability", "problem-solving",
    "critical thinking", "time management", "creativity", "decision making", "emotional intelligence",
    "negotiation", "conflict resolution", "presentation", "attention to detail", "multitasking"
}

# 🧠 Top hard skills across tech domains
HARD_SKILLS = {
    "python", "java", "c++", "javascript", "sql", "html", "css", "node.js", "react", "angular",
    "django", "flask", "spring", "git", "github", "docker", "kubernetes", "aws", "azure", "gcp",
    "machine learning", "deep learning", "nlp", "data analysis", "data visualization",
    "pandas", "numpy", "matplotlib", "tensorflow", "pytorch", "linux", "bash", "power bi", "tableau"
}

# 📌 Advanced headers
HEADERS = {
    "experience", "professional experience", "work experience", "education", "skills", "technical skills",
    "projects", "certifications", "summary", "profile", "contact", "contact information",
    "achievements", "publications", "interests", "languages", "extracurricular", "volunteering"
}

# 🚫 Avoid informal tone
BAD_PRONOUNS = {
    "i", "me", "my", "mine", "we", "us", "our", "ours", "your", "you're", "you", "am"
}

# 📧 Regex patterns for contact info
EMAIL_REGEX = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
PHONE_REGEX = r"\b(\+?\d{1,3}[-.\s]?)?(\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{4}\b"
LINKEDIN_REGEX = r"\b(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/[a-zA-Z0-9-_%]+\b"
GITHUB_REGEX = r"\b(?:https?:\/\/)?(?:www\.)?github\.com\/[a-zA-Z0-9-]+\b"
PORTFOLIO_REGEX = r"\b(?:https?:\/\/)?[a-zA-Z0-9.-]+\.(dev|tech|me|xyz|site|portfolio|com)\b"

# 💼 Recognize job titles for bonus scoring
COMMON_JOB_TITLES = {
    "software engineer", "data analyst", "data scientist", "web developer", "backend engineer",
    "frontend developer", "ml engineer", "ai engineer", "product manager", "research intern",
    "cloud engineer", "full stack developer", "devops engineer", "qa engineer", "ui/ux designer"
}

# 🔑 Extra keywords from JD matching (optional)
EXTRA_KEYWORDS = {
    "agile", "scrum", "jira", "rest api", "graphql", "oop", "microservices", "design patterns",
    "unit testing", "ci/cd", "postman", "swagger", "firebase", "mongodb", "postgresql", "redis"
}


# Thresholds & weights
FUZZY_HEADER_THRESHOLD = 80
MAX_HEADER_SCORE = 10
MAX_ACTION_VERB_SCORE = 15
MAX_SKILLS_SCORE = 20
MAX_CONTACT_SCORE = 12
MAX_READABILITY_SCORE = 10
MAX_SPELLING_SCORE = 10
MAX_PRONOUN_SCORE = 5
MAX_WORDCOUNT_SCORE = 10
MAX_JOBTITLE_SCORE = 8
MAX_NEGATIVE_PENALTY = 10
def fuzzy_header_found(header, text):
    # Check if header is fuzzy-matched in text with threshold
    # e.g. "Work experience" might appear as "Work Experience:", "Experience", "Professional Experience"
    return any(fuzz.partial_ratio(header, line) >= FUZZY_HEADER_THRESHOLD for line in text.split('\n'))

def count_action_verbs_in_bullets(bullets):
    count = 0
    for b in bullets:
        words = b.lower().split()
        # Check first 3 words for an action verb
        if any(word in ACTION_WORDS for word in words[:3]):
            count += 1
    return count

def count_skills(text_tokens, skills_set):
    # Skills may be multiword; we'll do phrase matching over tokens (lemmatized)
    count = 0
    text_str = ' '.join(text_tokens)
    for skill in skills_set:
        # For multi-word skill, check phrase presence
        if skill in text_str:
            count += 1
    return count

def detect_job_titles(text):
    # Using NER plus keyword matching to detect job titles
    doc = nlp(text)
    found_titles = set()
    # Check for exact phrase in lowercase text
    lowered = text.lower()
    for title in COMMON_JOB_TITLES:
        if title in lowered:
            found_titles.add(title)
    # Also check entities of type ORG/WORK_OF_ART might sometimes catch job titles, but let's keep it simple
    return len(found_titles)

def detect_informal_or_filler(text_tokens):
    # Penalize if informal words or overused buzzwords appear
    informal_words = {"basically", "actually", "just", "very", "really", "stuff", "things"}
    buzzwords = {"synergy", "leverage", "streamline", "pivot", "bandwidth", "disrupt", "ecosystem"}
    count = 0
    for t in text_tokens:
        if t.lower_ in informal_words or t.lower_ in buzzwords:
            count += 1
    return count

def get_resume_score(resume_text):
    score = 0
    text_lower = resume_text.lower()
    doc = nlp(resume_text)
    text_tokens = [token.lemma_ for token in doc if not token.is_punct and not token.is_space]

    # 1. Headers detection with fuzzy matching
    headers_found = sum(1 for h in HEADERS if fuzzy_header_found(h, text_lower))
    score += min(headers_found * 2, MAX_HEADER_SCORE)

    # 2. Action verbs in bullets
    bullet_points = re.findall(r"(?:•|-|\*)\s?(.*)", resume_text)
    action_verb_count = count_action_verbs_in_bullets(bullet_points)
    score += min(action_verb_count * 2, MAX_ACTION_VERB_SCORE)

    # 3. Skills detection
    soft_skill_count = count_skills(text_lower.split(), SOFT_SKILLS)
    hard_skill_count = count_skills(text_lower.split(), HARD_SKILLS)
    total_skills = soft_skill_count + hard_skill_count
    import math
    skills_score = min(MAX_SKILLS_SCORE, int(5 * math.log1p(total_skills)))
    score += skills_score

    # 4. Contact info detection
    contact_points = 0
    if re.search(EMAIL_REGEX, resume_text): contact_points += 3
    if re.search(PHONE_REGEX, resume_text): contact_points += 3
    contact_points += 2 if re.search(LINKEDIN_REGEX, resume_text) else 0
    contact_points += 2 if re.search(GITHUB_REGEX, resume_text) else 0
    contact_points += 2 if re.search(PORTFOLIO_REGEX, resume_text) else 0
    score += min(contact_points, MAX_CONTACT_SCORE)

    # 5. Readability
    flesch = textstat.flesch_reading_ease(resume_text)
    avg_sent_len = textstat.avg_sentence_length(resume_text)
    passive_ratio = textstat.passive_voice_percentage(resume_text) if hasattr(textstat, "passive_voice_percentage") else 0
    if flesch > 65 and avg_sent_len < 20 and passive_ratio < 5:
        score += MAX_READABILITY_SCORE
    elif flesch > 50:
        score += int(MAX_READABILITY_SCORE * 0.7)
    else:
        score += int(MAX_READABILITY_SCORE * 0.4)

    # 6. Spelling
    words = [token.text for token in doc if token.is_alpha]
    errors = spell.unknown(words)
    error_counts = Counter(errors)
    error_ratio = len(errors) / max(len(words), 1)
    repeated_errors = sum(1 for err, cnt in error_counts.items() if cnt > 1)
    if error_ratio < 0.01 and repeated_errors == 0:
        score += MAX_SPELLING_SCORE
    elif error_ratio < 0.02:
        score += int(MAX_SPELLING_SCORE * 0.7)
    elif error_ratio < 0.04:
        score += int(MAX_SPELLING_SCORE * 0.4)

    # 7. No personal pronouns
    if not any(p in text_lower.split() for p in BAD_PRONOUNS):
        score += MAX_PRONOUN_SCORE

    # 8. Word count
    wc = len(resume_text.split())
    if 350 <= wc <= 700:
        score += MAX_WORDCOUNT_SCORE
    elif 250 <= wc < 350 or 700 < wc <= 900:
        score += int(MAX_WORDCOUNT_SCORE * 0.5)
    else:
        score += int(MAX_WORDCOUNT_SCORE * 0.2)

    # 9. Job title detection
    job_title_count = detect_job_titles(text_lower)
    score += min(job_title_count * 3, MAX_JOBTITLE_SCORE)

    # 10. Filler word penalty
    informal_count = detect_informal_or_filler(doc)
    penalty = min(informal_count * 2, MAX_NEGATIVE_PENALTY)
    score -= penalty

    return max(0, min(100, score))



###### Main function run() ######

def run():
    
    # (Logo, Heading, Sidebar etc)
    img = Image.open('./Logo/RESUM.png')
    # img = Image.open('App/Logo/RESUM.png')
 # Add your credit link
    st.markdown(
        '<p style="text-align: right;"><b>Created by '
        '<a href="https://www.linkedin.com/in/parth-sarthi-037b90258/" '
        'style="text-decoration: none; color: #021659;">Parth Sarthi</a> &nbsp;& '
        '<a href="https://www.linkedin.com/in/machint-sethi-9573b6254/" '
        'style="text-decoration: none; color: #021659;"> Machint Sethi</a></b></p>',
        unsafe_allow_html=True
    )

    activities = ["-- Select --", "User", "Feedback", "About", "Admin"]
    st.image(img)
    st.markdown("## Select The Options - ")  # Header at the top

    choice = st.selectbox("Choose among the given options:", activities)

    if choice != "-- Select --":
        st.write(f"You selected: {choice}")


   

   

    ###### Creating Database and Table ######


    # Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS CV;"""
    cursor.execute(db_sql)


    # Create table user_data and user_feedback
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                    sec_token varchar(20) NOT NULL,
                    ip_add varchar(50) NULL,
                    host_name varchar(50) NULL,
                    dev_user varchar(50) NULL,
                    os_name_ver varchar(50) NULL,
                    latlong varchar(50) NULL,
                    city varchar(50) NULL,
                    state varchar(50) NULL,
                    country varchar(50) NULL,
                    act_name varchar(50) NOT NULL,
                    act_mail varchar(50) NOT NULL,
                    act_mob varchar(20) NOT NULL,
                    Name varchar(500) NOT NULL,
                    Email_ID VARCHAR(500) NOT NULL,
                    resume_score VARCHAR(8) NOT NULL,
                    Timestamp VARCHAR(50) NOT NULL,
                    Page_no VARCHAR(5) NOT NULL,
                    Predicted_Field BLOB NOT NULL,
                    User_level BLOB NOT NULL,
                    Actual_skills BLOB NOT NULL,
                    Recommended_skills BLOB NOT NULL,
                    Recommended_courses BLOB NOT NULL,
                    pdf_name varchar(50) NOT NULL,
                    PRIMARY KEY (ID)
                    );
                """
    cursor.execute(table_sql)


    DBf_table_name = 'user_feedback'
    tablef_sql = "CREATE TABLE IF NOT EXISTS " + DBf_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                        feed_name varchar(50) NOT NULL,
                        feed_email VARCHAR(50) NOT NULL,
                        feed_score VARCHAR(5) NOT NULL,
                        comments VARCHAR(100) NULL,
                        Timestamp VARCHAR(50) NOT NULL,
                        PRIMARY KEY (ID)
                    );
                """
    cursor.execute(tablef_sql)


    ###### CODE FOR CLIENT SIDE (USER) ######
    

    if choice == 'User':
        
        
        show_loading_animation()
        
        # Collecting Miscellaneous Information
        # act_name = st.text_input('Name*')
        # act_mail = st.text_input('Mail*')
        # act_mob  = st.text_input('Mobile Number*')
        sec_token = secrets.token_urlsafe(12)
        host_name = socket.gethostname()
        ip_add = socket.gethostbyname(host_name)
        dev_user = os.getlogin()
        os_name_ver = platform.system() + " " + platform.release()
        g = geocoder.ip('me')
        latlong = g.latlng
        geolocator = Nominatim(user_agent="http")
        location = geolocator.reverse(latlong, language='en')
        address = location.raw['address']
        cityy = address.get('city', '')
        statee = address.get('state', '')
        countryy = address.get('country', '')  
        city = cityy
        state = statee
        country = countryy


        # Upload Resume
        st.markdown('''<h5 style='text-align: left; color: #021659;'> Upload Your Resume, And Get Smart Recommendations</h5>''',unsafe_allow_html=True)
        
        ## file upload in pdf format
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            with st.spinner('Hang On While We Cook Magic For You...'):
                time.sleep(4)
        
            ### saving the uploaded resume to folder
            # save_image_path = './Uploaded_Resumes/'+pdf_file.name
            save_image_path = r'D:\TRY_RESUME_ANN\AI-Resume-Analyzer\App\Uploaded_Resumes\\' + pdf_file.name

            # save_image_path = os.path.join(upload_folder, pdf_file.name)

            pdf_name = pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)

            ### parsing and extracting whole resume 
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                
                ## Get the whole resume data into resume_text
                resume_text = pdf_reader(save_image_path)

                ## Showing Analyzed data from (resume_data)
                st.header("**Resume Analysis 🤘**")
                st.success("Hello "+ resume_data['name'])
                st.subheader("**Your Basic info 👀**")
                try:
                    st.text('Name: '+resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Degree: '+str(resume_data['degree']))                    
                    st.text('Resume pages: '+str(resume_data['no_of_pages']))

                except:
                    pass
                ## Predicting Candidate Experience Level 

                ### Trying with different possibilities
                cand_level = ''
                if resume_data['no_of_pages'] < 1:                
                    cand_level = "NA"
                    st.markdown( '''<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>''',unsafe_allow_html=True)
                
                #### if internship then intermediate level
                elif 'INTERNSHIP' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'INTERNSHIPS' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'Internship' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'Internships' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                
                #### if Work Experience/Experience then Experience level
                elif 'EXPERIENCE' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'WORK EXPERIENCE' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'Experience' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'Work Experience' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                else:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at Fresher level!!''',unsafe_allow_html=True)


#############################################################################################################################################################                
                ## Skills Analyzing and Recommendation
                
                st.subheader("**Skills Recommendation 💡**")

                # Current Analyzed Skills
                keywords = st_tags(
                    label='### Your Current Skills',
                    text='See our skills recommendation below',
                    value=resume_data['skills'],
                    key='1'
                )

                # Join skills into mock resume text for matching
                resume_text = " ".join(resume_data['skills'])

                # Predict job role
                predicted_role, score = predict_job_role(resume_text)
                if predicted_role:
                   st.success(f"***Our analysis says, you should prepare `{predicted_role.upper()}` jobs.*** (Confidence Score: {score:.2f}/10)")

                else:
                    st.warning("We couldn't determine a target job role. Try adding more technical skills to your resume.")

                # Recommend missing skills
                missing_skills = recommend_missing_skills(resume_text, predicted_role)

                if missing_skills:
                    st.warning("You're missing some key skills for this role:")
                    recommended_keywords = st_tags(
                        label='### Recommended skills for you.',
                        text='Recommended skills generated from the system',
                        value=missing_skills,
                        key='2'
                    )
                    st.markdown(
                        '''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of landing the job.</h5>''',
                        unsafe_allow_html=True
                    )
                else:
                    st.success("Your resume includes all key skills for this role!")

                # Recommend courses for missing skills
                recommended_courses = {}
                for skill in missing_skills:
                    if skill.lower() in course_catalog:
                        recommended_courses[skill] = course_catalog[skill.lower()]

                if recommended_courses:
                    st.subheader("🎓 Recommended Courses to Learn Missing Skills")
                    for skill, course in recommended_courses.items():
                        st.markdown(f"- **{skill.title()}**: [{course}]({course})")
                else:
                    st.info("No specific course recommendations available at the moment.")



###########################################################################################################
                ## Resume Scorer & Resume Writing Tips
                st.subheader("**Resume Tips & Ideas 🥂**")
                resume_text = extract_text_from_pdf(save_image_path)

                
                # ### Predicting Whether these key points are added to the resume
                resume_text_lower = resume_text.lower()

                # Tips
                sections = [
                    {
                        "keywords": ["objective", "summary"],
                        "score": 6,
                        "success": "[+] Awesome! You have added Objective/Summary",
                        "fail": "[-] Please add your career objective, it will give your career intention to the recruiters."
                    },
                    {
                        "keywords": ["education", "school", "college"],
                        "score": 12,
                        "success": "[+] Awesome! You have added Education Details",
                        "fail": "[-] Please add Education. It will give your qualification level to the recruiter."
                    },
                    {
                        "keywords": ["experience"],
                        "score": 16,
                        "success": "[+] Awesome! You have added Experience",
                        "fail": "[-] Please add Experience. It will help you stand out from the crowd."
                    },
                    {
                        "keywords": ["internship", "internships"],
                        "score": 6,
                        "success": "[+] Awesome! You have added Internships",
                        "fail": "[-] Please add Internships. It will help you stand out from the crowd."
                    },
                    {
                        "keywords": ["skills", "skill"],
                        "score": 7,
                        "success": "[+] Awesome! You have added Skills",
                        "fail": "[-] Please add Skills. It will help you a lot."
                    },
                    {
                        "keywords": ["extra-curricular"],
                        "score": 4,
                        "success": "[+] Awesome! You have added your Extra-Curricular Activities",
                        "fail": "[-] Please add Hobbies. It will show your personality to recruiters."
                    },
                    {
                        "keywords": ["interests"],
                        "score": 5,
                        "success": "[+] Awesome! You have added your Interests",
                        "fail": "[-] Please add Interests. It will show your interest beyond just the job."
                    },
                    {
                        "keywords": ["achievements"],
                        "score": 13,
                        "success": "[+] Awesome! You have added your Achievements",
                        "fail": "[-] Please add Achievements. It will show that you are capable for the required position."
                    },
                    {
                        "keywords": ["certifications", "certification", "certificate", "link", "links"],
                        "score": 12,
                        "success": "[+] Awesome! You have added your Certifications",
                        "fail": "[-] Please add Certifications. It will show specialization for the required position."
                    },
                    {
                        "keywords": ["projects", "project"],
                        "score": 19,
                        "success": "[+] Awesome! You have added your Projects",
                        "fail": "[-] Please add Projects. It will show relevant work for the required position."
                    }
                ]

                # Score initialization
                resume_score = 0

                # Iterate and evaluate each section
                for section in sections:
                    found = any(keyword in resume_text_lower for keyword in section["keywords"])
                    if found:
                        resume_score += section["score"]
                        st.markdown(f'''<h5 style='text-align: left; color: #1ed760;'>{section["success"]}</h5>''', unsafe_allow_html=True)
                    else:
                        st.markdown(f'''<h5 style='text-align: left; color: #000000;'>{section["fail"]}</h5>''', unsafe_allow_html=True)

                # Optionally show the score
                # st.markdown(f"<h4 style='color: #1ed760;'>Total Resume Score: {resume_score}</h4>", unsafe_allow_html=True)



                st.subheader("**Resume Score 📝**")
                
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )
                
                ats_score = get_resume_score(resume_text)


                ### Score Bar
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(ats_score):
                    score +=1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)

                ### Score
                st.success('** Your Resume Writing Score: ' + str(ats_score)+'**')
                st.warning("** Note: This score is calculated based on the content that you have in your Resume. **")

                # print(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)


                ### Getting Current Date and Time
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date+'_'+cur_time)


                ## Calling insert_data to add all the data into user_data                
                insert_data(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (resume_data['name']), (resume_data['email']), (resume_data['mobile_number']), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), predicted_role, cand_level, str(resume_data['skills']), str(missing_skills), str(recommended_courses), pdf_name)

                
                ## Recommending Resume Writing Video
                st.header("**Bonus Video for Resume Writing Tips💡**")
                resume_vid = random.choice(resume_videos)
                st.video(resume_vid)

                ## Recommending Interview Preparation Video
                st.header("**Bonus Video for Interview Tips💡**")
                interview_vid = random.choice(interview_videos)
                st.video(interview_vid)

                ## On Successful Result 
                st.balloons()

            else:
                st.error('Something went wrong..')                


    ###### CODE FOR FEEDBACK SIDE ######
    elif choice == 'Feedback':   
        show_loading_animation()

        # timestamp 
        ts = time.time()
        cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        timestamp = str(cur_date+'_'+cur_time)

        # Feedback Form
        with st.form("my_form"):
            st.write("Feedback form")            
            feed_name = st.text_input('Name')
            feed_email = st.text_input('Email')
            feed_score = st.slider('Rate Us From 1 - 5', 1, 5)
            comments = st.text_input('Comments')
            Timestamp = timestamp        
            submitted = st.form_submit_button("Submit")
            if submitted:
                ## Calling insertf_data to add dat into user feedback
                insertf_data(feed_name,feed_email,feed_score,comments,Timestamp)    
                ## Success Message 
                st.success("Thanks! Your Feedback was recorded.") 
                ## On Successful Submit
                st.balloons()    


        # query to fetch data from user feedback table
        query = 'select * from user_feedback'        
        plotfeed_data = pd.read_sql(query, connection)                        


        # fetching feed_score from the query and getting the unique values and total value count 
        labels = plotfeed_data.feed_score.unique()
        values = plotfeed_data.feed_score.value_counts()


        # plotting pie chart for user ratings
        st.subheader("**Past User Rating's**")
        fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5", color_discrete_sequence=px.colors.sequential.Aggrnyl)
        st.plotly_chart(fig)


        #  Fetching Comment History
        cursor.execute('select feed_name, comments from user_feedback')
        plfeed_cmt_data = cursor.fetchall()

        st.subheader("**User Comment's**")
        dff = pd.DataFrame(plfeed_cmt_data, columns=['User', 'Comment'])
        st.dataframe(dff, width=1000)

    
    ###### CODE FOR ABOUT PAGE ######
    elif choice == 'About':   
        show_loading_animation()

        st.subheader("**RESUME ANALYZER**")

        st.markdown('''

        <p align='justify'>
            A tool which parses information from a resume using natural language processing and finds the keywords, cluster them onto sectors based on their keywords. And lastly show recommendations, predictions, analytics to the applicant based on keyword matching.
        </p>

        <p align="justify">
            <b>How to use it: -</b> <br/><br/>
            <b>User -</b> <br/>
            In the Dropdown Bar, choose yourself as user and upload your resume in pdf format.<br/>
            Just sit back and relax our tool will do the magic on it's own.<br/><br/>
            <b>Feedback -</b> <br/>
            A place where user can suggest some feedback about the tool.<br/><br/>
        </p><br/><br/>

        <p align="justify">
            Built with 🤍 by </br>
            Parth Sarthi & Machint Sethi
            
        </p>

        ''',unsafe_allow_html=True)  


    ###### CODE FOR ADMIN SIDE (ADMIN) ######
    elif choice == 'Admin':
        show_loading_animation()

        st.success('Welcome to Admin Side')

        #  Admin Login
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')

        if st.button('Login'):
            
            ## Credentials 
            if ad_user == 'admin' and ad_password == 'admin':
                
                ### Fetch miscellaneous data from user_data(table) and convert it into dataframe
                cursor.execute('''SELECT ID, ip_add, resume_score, convert(Predicted_Field using utf8), convert(User_level using utf8), city, state, country from user_data''')
                datanalys = cursor.fetchall()
                plot_data = pd.DataFrame(datanalys, columns=['Idt', 'IP_add', 'resume_score', 'Predicted_Field', 'User_Level', 'City', 'State', 'Country'])
                
                ### Total Users Count with a Welcome Message
                values = plot_data.Idt.count()
                st.success("Welcome Boisss ! :-)")                
                
                ### Fetch user data from user_data(table) and convert it into dataframe
                cursor.execute('''SELECT ID, sec_token, ip_add, act_name, act_mail, act_mob, convert(Predicted_Field using utf8), Timestamp, Name, Email_ID, resume_score, Page_no, pdf_name, convert(User_level using utf8), convert(Actual_skills using utf8), convert(Recommended_skills using utf8), convert(Recommended_courses using utf8), city, state, country, latlong, os_name_ver, host_name, dev_user from user_data''')
                data = cursor.fetchall()                

                st.header("**User's Data**")
                df = pd.DataFrame(data, columns=['ID', 'Token', 'IP Address', 'Name', 'Mail', 'Mobile Number', 'Predicted Field', 'Timestamp',
                                                 'Predicted Name', 'Predicted Mail', 'Resume Score', 'Total Page',  'File Name',   
                                                 'User Level', 'Actual Skills', 'Recommended Skills', 'Recommended Course',
                                                 'City', 'State', 'Country', 'Lat Long', 'Server OS', 'Server Name', 'Server User',])
                
                ### Viewing the dataframe
                st.dataframe(df)
                
                ### Downloading Report of user_data in csv file
                st.markdown(get_csv_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)

                ### Fetch feedback data from user_feedback(table) and convert it into dataframe
                cursor.execute('''SELECT * from user_feedback''')
                data = cursor.fetchall()

                st.header("**User's Feedback Data**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Feedback Score', 'Comments', 'Timestamp'])
                st.dataframe(df)

                ### query to fetch data from user_feedback(table)
                query = 'select * from user_feedback'
                plotfeed_data = pd.read_sql(query, connection)                        

                ### Analyzing All the Data's in pie charts

                # fetching feed_score from the query and getting the unique values and total value count 
                labels = plotfeed_data.feed_score.unique()
                values = plotfeed_data.feed_score.value_counts()
                
                # Pie chart for user ratings
                st.subheader("**User Rating's**")
                fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5 🤗", color_discrete_sequence=px.colors.sequential.Aggrnyl)
                st.plotly_chart(fig)

                # fetching Predicted_Field from the query and getting the unique values and total value count                 
                labels = plot_data.Predicted_Field.unique()
                values = plot_data.Predicted_Field.value_counts()

                # Pie chart for predicted field recommendations
                st.subheader("**Pie-Chart for Predicted Field Recommendation**")
                fig = px.pie(df, values=values, names=labels, title='Predicted Field according to the Skills 👽', color_discrete_sequence=px.colors.sequential.Aggrnyl_r)
                st.plotly_chart(fig)

                # fetching User_Level from the query and getting the unique values and total value count                 
                labels = plot_data.User_Level.unique()
                values = plot_data.User_Level.value_counts()

                # Pie chart for User's👨‍💻 Experienced Level
                st.subheader("**Pie-Chart for User's Experienced Level**")
                fig = px.pie(df, values=values, names=labels, title="Pie-Chart 📈 for User's 👨‍💻 Experienced Level", color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig)

                # fetching resume_score from the query and getting the unique values and total value count                 
                labels = plot_data.resume_score.unique()                
                values = plot_data.resume_score.value_counts()

                # Pie chart for Resume Score
                st.subheader("**Pie-Chart for Resume Score**")
                fig = px.pie(df, values=values, names=labels, title='From 1 to 100 💯', color_discrete_sequence=px.colors.sequential.Agsunset)
                st.plotly_chart(fig)

                # fetching IP_add from the query and getting the unique values and total value count 
                labels = plot_data.IP_add.unique()
                values = plot_data.IP_add.value_counts()

                # Pie chart for Users
                st.subheader("**Pie-Chart for Users App Used Count**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based On IP Address 👥', color_discrete_sequence=px.colors.sequential.matter_r)
                st.plotly_chart(fig)

                # fetching City from the query and getting the unique values and total value count 
                labels = plot_data.City.unique()
                values = plot_data.City.value_counts()

                # Pie chart for City
                st.subheader("**Pie-Chart for City**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based On City 🌆', color_discrete_sequence=px.colors.sequential.Jet)
                st.plotly_chart(fig)

                # fetching State from the query and getting the unique values and total value count 
                labels = plot_data.State.unique()
                values = plot_data.State.value_counts()

                # Pie chart for State
                st.subheader("**Pie-Chart for State**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based on State 🚉', color_discrete_sequence=px.colors.sequential.PuBu_r)
                st.plotly_chart(fig)

                # fetching Country from the query and getting the unique values and total value count 
                labels = plot_data.Country.unique()
                values = plot_data.Country.value_counts()

                # Pie chart for Country
                st.subheader("**Pie-Chart for Country**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based on Country 🌏', color_discrete_sequence=px.colors.sequential.Purpor_r)
                st.plotly_chart(fig)

            ## For Wrong Credentials
            else:
                st.error("Wrong ID & Password Provided")

# Calling the main (run()) function to make the whole process run
run()
