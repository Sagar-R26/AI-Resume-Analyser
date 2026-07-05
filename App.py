import streamlit as st
import pandas as pd
import base64, random
import time,datetime
import pymysql
import os
import socket
import platform
import geocoder
import secrets
import io
import plotly.express as px
from geopy.geocoders import Nominatim
from pyresparser import ResumeParser
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from streamlit_tags import st_tags
from PIL import Image
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos
import nltk
nltk.download('stopwords', quiet=True)


###### Utility functions ######

def get_csv_download_link(df, filename, text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()
    converter.close()
    fake_file_handle.close()
    return text


def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations**")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course


###### Database setup ######

connection = pymysql.connect(host='localhost', user='root', password='your_password', db='cv')
cursor = connection.cursor()


def insert_data(sec_token, ip_add, host_name, dev_user, os_name_ver, latlong, city, state, country,
                act_name, act_mail, act_mob, name, email, res_score, timestamp, no_of_pages,
                reco_field, cand_level, skills, recommended_skills, courses, pdf_name):
    insert_sql = """insert into user_data
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (str(sec_token), str(ip_add), host_name, dev_user, os_name_ver, str(latlong),
                  city, state, country, act_name, act_mail, act_mob, name, email, str(res_score),
                  timestamp, str(no_of_pages), reco_field, cand_level, skills,
                  recommended_skills, courses, pdf_name)
    cursor.execute(insert_sql, rec_values)
    connection.commit()


def insertf_data(feed_name, feed_email, feed_score, comments, Timestamp):
    insertfeed_sql = """insert into user_feedback
    values (0,%s,%s,%s,%s,%s)"""
    rec_values = (feed_name, feed_email, feed_score, comments, Timestamp)
    cursor.execute(insertfeed_sql, rec_values)
    connection.commit()


###### Page config ######

st.set_page_config(page_title="AI Resume Analyzer", page_icon='./Logo/recommend.png')


###### Main app ######

def run():

    img = Image.open('./Logo/logo.png')
    st.image(img)
    st.sidebar.markdown("# Choose Something...")
    activities = ["User", "Feedback", "About", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)

    # Create DB and tables if not exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS CV;")

    cursor.execute("""CREATE TABLE IF NOT EXISTS user_data (
        ID INT NOT NULL AUTO_INCREMENT,
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
        PRIMARY KEY (ID));""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS user_feedback (
        ID INT NOT NULL AUTO_INCREMENT,
        feed_name varchar(50) NOT NULL,
        feed_email VARCHAR(50) NOT NULL,
        feed_score VARCHAR(5) NOT NULL,
        comments VARCHAR(100) NULL,
        Timestamp VARCHAR(50) NOT NULL,
        PRIMARY KEY (ID));""")


    ###### USER SECTION ######

    if choice == 'User':

        act_name = st.text_input('Name*')
        act_mail = st.text_input('Mail*')
        act_mob  = st.text_input('Mobile Number*')
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
        city = address.get('city', '')
        state = address.get('state', '')
        country = address.get('country', '')

        st.markdown('''<h5 style='text-align: left; color: #021659;'>Upload Your Resume, And Get Smart Recommendations</h5>''', unsafe_allow_html=True)

        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            with st.spinner('Hang On While We Cook Magic For You...'):
                time.sleep(4)

            save_image_path = './Uploaded_Resumes/' + pdf_file.name
            pdf_name = pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)

            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:

                resume_text = pdf_reader(save_image_path)

                st.header("**Resume Analysis**")
                st.success("Hello " + resume_data['name'])
                st.subheader("**Your Basic info**")
                try:
                    st.text('Name: ' + resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Degree: ' + str(resume_data['degree']))
                    st.text('Resume pages: ' + str(resume_data['no_of_pages']))
                except:
                    pass

                # Experience level prediction
                cand_level = ''
                if resume_data['no_of_pages'] < 1:
                    cand_level = "NA"
                    st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>''', unsafe_allow_html=True)
                elif 'INTERNSHIP' in resume_text or 'INTERNSHIPS' in resume_text or 'Internship' in resume_text or 'Internships' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''', unsafe_allow_html=True)
                elif 'EXPERIENCE' in resume_text or 'WORK EXPERIENCE' in resume_text or 'Experience' in resume_text or 'Work Experience' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''', unsafe_allow_html=True)
                else:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at Fresher level!!''', unsafe_allow_html=True)

                st.subheader("**Skills Recommendation**")

                st_tags(label='### Your Current Skills', text='See our skills recommendation below', value=resume_data['skills'], key='1')

                ds_keyword = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep learning', 'flask', 'streamlit']
                web_keyword = ['react', 'django', 'node js', 'react js', 'php', 'laravel', 'magento', 'wordpress', 'javascript', 'angular js', 'c#', 'asp.net', 'flask']
                android_keyword = ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy']
                ios_keyword = ['ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode']
                uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes', 'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator', 'illustrator', 'adobe after effects', 'after effects', 'adobe premier pro', 'premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp', 'user research', 'user experience']
                n_any = ['english', 'communication', 'writing', 'microsoft office', 'leadership', 'customer management', 'social media']

                recommended_skills = []
                reco_field = ''
                rec_course = ''

                for i in resume_data['skills']:
                    if i.lower() in ds_keyword:
                        reco_field = 'Data Science'
                        st.success("** Our analysis says you are looking for Data Science Jobs.**")
                        recommended_skills = ['Data Visualization', 'Predictive Analysis', 'Statistical Modeling', 'Data Mining', 'Clustering & Classification', 'Data Analytics', 'Quantitative Analysis', 'Web Scraping', 'ML Algorithms', 'Keras', 'Pytorch', 'Probability', 'Scikit-learn', 'Tensorflow', "Flask", 'Streamlit']
                        st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System', value=recommended_skills, key='2')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost the chances of getting a Job</h5>''', unsafe_allow_html=True)
                        rec_course = course_recommender(ds_course)
                        break

                    elif i.lower() in web_keyword:
                        reco_field = 'Web Development'
                        st.success("** Our analysis says you are looking for Web Development Jobs **")
                        recommended_skills = ['React', 'Django', 'Node JS', 'React JS', 'php', 'laravel', 'Magento', 'wordpress', 'Javascript', 'Angular JS', 'c#', 'Flask', 'SDK']
                        st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System', value=recommended_skills, key='3')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost the chances of getting a Job</h5>''', unsafe_allow_html=True)
                        rec_course = course_recommender(web_course)
                        break

                    elif i.lower() in android_keyword:
                        reco_field = 'Android Development'
                        st.success("** Our analysis says you are looking for Android App Development Jobs **")
                        recommended_skills = ['Android', 'Android development', 'Flutter', 'Kotlin', 'XML', 'Java', 'Kivy', 'GIT', 'SDK', 'SQLite']
                        st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System', value=recommended_skills, key='4')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost the chances of getting a Job</h5>''', unsafe_allow_html=True)
                        rec_course = course_recommender(android_course)
                        break

                    elif i.lower() in ios_keyword:
                        reco_field = 'IOS Development'
                        st.success("** Our analysis says you are looking for IOS App Development Jobs **")
                        recommended_skills = ['IOS', 'IOS Development', 'Swift', 'Cocoa', 'Cocoa Touch', 'Xcode', 'Objective-C', 'SQLite', 'Plist', 'StoreKit', "UI-Kit", 'AV Foundation', 'Auto-Layout']
                        st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System', value=recommended_skills, key='5')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost the chances of getting a Job</h5>''', unsafe_allow_html=True)
                        rec_course = course_recommender(ios_course)
                        break

                    elif i.lower() in uiux_keyword:
                        reco_field = 'UI-UX Development'
                        st.success("** Our analysis says you are looking for UI-UX Development Jobs **")
                        recommended_skills = ['UI', 'User Experience', 'Adobe XD', 'Figma', 'Zeplin', 'Balsamiq', 'Prototyping', 'Wireframes', 'Storyframes', 'Adobe Photoshop', 'Editing', 'Illustrator', 'After Effects', 'Premier Pro', 'Indesign', 'Wireframe', 'Solid', 'Grasp', 'User Research']
                        st_tags(label='### Recommended skills for you.', text='Recommended skills generated from System', value=recommended_skills, key='6')
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost the chances of getting a Job</h5>''', unsafe_allow_html=True)
                        rec_course = course_recommender(uiux_course)
                        break

                    elif i.lower() in n_any:
                        reco_field = 'NA'
                        st.warning("** Currently our tool only predicts and recommends for Data Science, Web, Android, IOS and UI/UX Development**")
                        recommended_skills = ['No Recommendations']
                        st_tags(label='### Recommended skills for you.', text='Currently No Recommendations', value=recommended_skills, key='6')
                        st.markdown('''<h5 style='text-align: left; color: #092851;'>Maybe Available in Future Updates</h5>''', unsafe_allow_html=True)
                        rec_course = "Sorry! Not Available for this Field"
                        break

                st.subheader("**Resume Tips & Ideas**")
                resume_score = 0

                checks = [
                    (['Objective', 'Summary'], 6, "Awesome! You have added Objective/Summary", "Please add your career objective"),
                    (['Education', 'School', 'College'], 12, "Awesome! You have added Education Details", "Please add Education"),
                    (['EXPERIENCE', 'Experience'], 16, "Awesome! You have added Experience", "Please add Experience"),
                    (['INTERNSHIPS', 'INTERNSHIP', 'Internships', 'Internship'], 6, "Awesome! You have added Internships", "Please add Internships"),
                    (['SKILLS', 'SKILL', 'Skills', 'Skill'], 7, "Awesome! You have added Skills", "Please add Skills"),
                    (['HOBBIES', 'Hobbies'], 4, "Awesome! You have added your Hobbies", "Please add Hobbies"),
                    (['INTERESTS', 'Interests'], 5, "Awesome! You have added your Interest", "Please add Interest"),
                    (['ACHIEVEMENTS', 'Achievements'], 13, "Awesome! You have added your Achievements", "Please add Achievements"),
                    (['CERTIFICATIONS', 'Certifications', 'Certification'], 12, "Awesome! You have added your Certifications", "Please add Certifications"),
                    (['PROJECTS', 'PROJECT', 'Projects', 'Project'], 19, "Awesome! You have added your Projects", "Please add Projects"),
                ]

                for keywords, score_add, success_msg, fail_msg in checks:
                    if any(kw in resume_text for kw in keywords):
                        resume_score += score_add
                        st.markdown(f'''<h5 style='text-align: left; color: #1ed760;'>[+] {success_msg}</h4>''', unsafe_allow_html=True)
                    else:
                        st.markdown(f'''<h5 style='text-align: left; color: #000000;'>[-] {fail_msg}</h4>''', unsafe_allow_html=True)

                st.subheader("**Resume Score**")

                st.markdown(
                    """<style>.stProgress > div > div > div > div { background-color: #d73b5c; }</style>""",
                    unsafe_allow_html=True,
                )

                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score += 1
                    time.sleep(0.02)
                    my_bar.progress(percent_complete + 1)

                st.success('** Your Resume Writing Score: ' + str(score) + '**')
                st.warning("** Note: This score is calculated based on the content that you have in your Resume. **")

                ts = time.time()
                timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S')

                insert_data(str(sec_token), str(ip_add), host_name, dev_user, os_name_ver, latlong,
                            city, state, country, act_name, act_mail, act_mob,
                            resume_data['name'], resume_data['email'], str(resume_score),
                            timestamp, str(resume_data['no_of_pages']), reco_field, cand_level,
                            str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)

                st.header("**Bonus Video for Resume Writing Tips**")
                st.video(random.choice(resume_videos))

                st.header("**Bonus Video for Interview Tips**")
                st.video(random.choice(interview_videos))

                st.balloons()
            else:
                st.error('Something went wrong..')


    ###### FEEDBACK SECTION ######

    elif choice == 'Feedback':

        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S')

        with st.form("my_form"):
            st.write("Feedback form")
            feed_name = st.text_input('Name')
            feed_email = st.text_input('Email')
            feed_score = st.slider('Rate Us From 1 - 5', 1, 5)
            comments = st.text_input('Comments')
            submitted = st.form_submit_button("Submit")
            if submitted:
                insertf_data(feed_name, feed_email, feed_score, comments, timestamp)
                st.success("Thanks! Your Feedback was recorded.")
                st.balloons()

        plotfeed_data = pd.read_sql('select * from user_feedback', connection)

        st.subheader("**Past User Rating's**")
        fig = px.pie(values=plotfeed_data.feed_score.value_counts(),
                     names=plotfeed_data.feed_score.unique(),
                     title="Chart of User Rating Score From 1 - 5",
                     color_discrete_sequence=px.colors.sequential.Aggrnyl)
        st.plotly_chart(fig)

        cursor.execute('select feed_name, comments from user_feedback')
        st.subheader("**User Comment's**")
        st.dataframe(pd.DataFrame(cursor.fetchall(), columns=['User', 'Comment']), width=1000)


    ###### ABOUT SECTION ######

    elif choice == 'About':

        st.subheader("**About The Tool - AI RESUME ANALYZER**")

        st.markdown('''
        <p align='justify'>
            A tool which parses information from a resume using natural language processing and finds the keywords,
            cluster them onto sectors based on their keywords. And lastly show recommendations, predictions,
            analytics to the applicant based on keyword matching.
        </p>
        <p align="justify">
            <b>How to use it: -</b><br/><br/>
            <b>User -</b> In the Side Bar choose yourself as user and fill the required fields and upload your
            resume in pdf format. Just sit back and relax our tool will do the magic on it's own.<br/><br/>
            <b>Feedback -</b> A place where user can suggest some feedback about the tool.<br/><br/>
            <b>Admin -</b> For login use <b>admin</b> as username and <b>admin@resume-analyzer</b> as password.
            It will load all the required stuffs and perform analysis.
        </p>
        ''', unsafe_allow_html=True)


    ###### ADMIN SECTION ######

    else:
        st.success('Welcome to Admin Side')

        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')

        if st.button('Login'):
            if ad_user == 'admin' and ad_password == 'admin@resume-analyzer':

                datanalys = pd.read_sql(
                    '''SELECT ID, ip_add, resume_score, convert(Predicted_Field using utf8),
                    convert(User_level using utf8), city, state, country from user_data''', connection
                )

                st.success("Total %d Users Have Used The Tool : )" % datanalys.ID.count())

                data = pd.read_sql(
                    '''SELECT ID, sec_token, ip_add, act_name, act_mail, act_mob,
                    convert(Predicted_Field using utf8), Timestamp, Name, Email_ID,
                    resume_score, Page_no, pdf_name, convert(User_level using utf8),
                    convert(Actual_skills using utf8), convert(Recommended_skills using utf8),
                    convert(Recommended_courses using utf8), city, state, country, latlong,
                    os_name_ver, host_name, dev_user from user_data''', connection
                )

                st.header("**User's Data**")
                st.dataframe(data)
                st.markdown(get_csv_download_link(data, 'User_Data.csv', 'Download Report'), unsafe_allow_html=True)

                feed_data = pd.read_sql('''SELECT * from user_feedback''', connection)
                st.header("**User's Feedback Data**")
                st.dataframe(feed_data)

                # Charts
                cols = [
                    ('feed_score', "Chart of User Rating Score From 1 - 5", px.colors.sequential.Aggrnyl),
                    ('Predicted_Field', 'Predicted Field according to the Skills', px.colors.sequential.Aggrnyl_r),
                    ('User_Level', "Pie-Chart for User's Experienced Level", px.colors.sequential.RdBu),
                    ('resume_score', 'From 1 to 100', px.colors.sequential.Agsunset),
                    ('IP_add', 'Usage Based On IP Address', px.colors.sequential.matter_r),
                    ('City', 'Usage Based On City', px.colors.sequential.Jet),
                    ('State', 'Usage Based on State', px.colors.sequential.PuBu_r),
                    ('Country', 'Usage Based on Country', px.colors.sequential.Purpor_r),
                ]

                for col, title, colors in cols:
                    if col in datanalys.columns or col in data.columns:
                        src = datanalys if col in datanalys.columns else data
                        st.subheader(f"**Pie-Chart for {title}**")
                        fig = px.pie(src, values=src[col].value_counts(), names=src[col].unique(),
                                     title=title, color_discrete_sequence=colors)
                        st.plotly_chart(fig)

            else:
                st.error("Wrong ID & Password Provided")


run()
