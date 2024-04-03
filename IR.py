
# import subprocess
# import streamlit as st
# import json
# from main import summarize_case


# st.set_page_config(
#     page_title="COURTSMART",
#     page_icon="🧊",
#     layout="wide")

# path = '/home/harshwardhan/Project/Court-smart/src/legal-case-retrieval-system-master/q1-2.txt'

# def execute_search(query, path):
#     with open(path, 'w') as query_file:
#         query_file.write(query)

#     try:
#         command = [
#             'python3',
#             'search.py',
#             '-d', '/home/harshwardhan/Project/Court-smart/src/legal-case-retrieval-system-master/dictionary.txt',
#             '-p', '/home/harshwardhan/Project/Court-smart/src/legal-case-retrieval-system-master/postings.txt',
#             '-q', path,
#             '-o', '/home/harshwardhan/Project/Court-smart/src/legal-case-retrieval-system-master/ouput.txt'
#         ]
#         result = subprocess.run(command, stdout=subprocess.PIPE, text=True, stderr=subprocess.PIPE, check=True)

#         with open('/home/harshwardhan/Project/Court-smart/src/legal-case-retrieval-system-master/ouput.txt', 'r') as output_file:
#             output_content = output_file.read()

#         return output_content
#     except subprocess.CalledProcessError as e:
#         return f"Error executing search script: {e.stderr}"

# def main():
#     st.title('Search Application')

#     query = st.text_area('Enter your query:')
    
    
#     if st.button('Search'):
#         if query:
#             try:
#                 result_json = execute_search(query, path)
#                 result_data = json.loads(result_json)
                
#                 st.subheader(f"Results for '{query}:'")
                
#                 for line in result_data:
#                     title = line['title']
#                     content = line['content']
#                     with st.expander(title):
#                         st.write(f'<div style="text-align: justify">{content}</div>', unsafe_allow_html=True)
                    
#             except subprocess.CalledProcessError as e:
#                 st.error(f"Error executing search script: {e.stderr}")
#         else:
#             st.warning('Please enter a query.')

# if __name__ == '__main__':
#     main()


import subprocess
import streamlit as st
import json
import re

from deployment_utils import DataPreparator, Predictor, generate_random_sample, generate_highlighted_words, extract_case_information


data_preparator = DataPreparator()
predictor = Predictor()

st.set_page_config(
    page_title="COURTSMART",
    page_icon="🧊",
    layout="wide")



path = '/home/harshwardhan/Project/Court-smart/src/q1-2.txt'

def execute_search(query, path):
    with open(path, 'w') as query_file:
        query_file.write(query)

    try:
        command = [
            'python3',
            'search.py',
            '-d', '/home/harshwardhan/Project/Court-smart/src/dictionary.txt',
            '-p', '/home/harshwardhan/Project/Court-smart/src/postings.txt',
            '-q', path,
            '-o', '/home/harshwardhan/Project/Court-smart/src/ouput.txt'
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, text=True, stderr=subprocess.PIPE, check=True)

        with open('/home/harshwardhan/Project/Court-smart/src/ouput.txt', 'r') as output_file:
            output_content = output_file.read()

        return output_content
    except subprocess.CalledProcessError as e:
        return f"Error executing search script: {e.stderr}"



def extract_petitioner_respondent(title):
    # Split the title by "vs" and remove extra spaces
    pattern = r'(.+?)\s*(vs|versus|Versus)\s*(.+)$'
    match = re.match(pattern, title)

    if match:
        # Extract petitioner and respondent based on the matched groups
        petitioner = match.group(1).strip()
        respondent = match.group(3).strip()
        return petitioner, respondent
    else:
        return None, None


def main():
    global petitioner, respondent, case_facts
    st.title('Search Application')

    query = st.text_area('Enter your query:', height=100)  # Adjust width as needed
    
    if st.button('Search'):
        if query:
            try:
                result_json = execute_search(query, path)
                result_data = json.loads(result_json)
                
                st.subheader(f"Results for '{query}:'")
                
                
                for line in result_data:
                    title = line['title']
                    content = line['content']
                    title_identifier = f"{title}"
                    content_identifier = f"{content}"
                    petitioner, respondent = extract_petitioner_respondent(title_identifier)
                    
                    # with st.expander(title):
                    #     st.write(f'<div style="text-align: justify">{content}</div>', unsafe_allow_html=True)

                        


                        
                        
                    #     # Add a button to summarize the content
                    #     if st.button(f'Summarize',key=f'Summarize_{content_identifier}'):
                            
                    #         summarized_case_facts = predictor.summarize_facts(case_facts)
                    #         st.write('<p class="bold-text"> Your Summarized Case Facts </p>', unsafe_allow_html=True)

                    #         st.write(case_facts, unsafe_allow_html=True)
                    with st.expander(title):
                        case_facts = (f"<p>petitioner: {petitioner}</p>"
                                        f"<p>respondent: {respondent}</p>"
                                        f"<p>case_facts: {content}</p>")
                        # summarized_case_facts = predictor.summarize_facts(case_facts)

                        expander_content = st.empty()  # Placeholder to store expander content
                        expander_content.write(f'<div style="text-align: justify">{case_facts}</div>',key=f'Summarize_{content_identifier}', unsafe_allow_html=True)
                        

                        # Add a button to summarize the content
                    submitted = st.button(f'Summarize', key=f'Summarize_{content_identifier}')
                    if submitted:
                        expander_content.write(f'<div style="text-align: justify">{content}</div>', unsafe_allow_html=True)
                                
                                

                            
                       
                    
            except subprocess.CalledProcessError as e:
                st.error(f"Error executing search script: {e.stderr}")
        else:
            st.warning('Please enter a query.')

if __name__ == '__main__':
    main()


