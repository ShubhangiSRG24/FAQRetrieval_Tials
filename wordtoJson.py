import json
from docx import Document
import re

def word_to_json(word_file, json_file):
    # Load Word document
    doc = Document(word_file)
    
    faqs = []
    current_question = None

    # Regular expression to match the FAQ number
    question_pattern = re.compile(r'Q\d+\.\s+(.*)')
    answer_pattern = re.compile(r'A\d+\.\s+(.*)')

    # Iterate through paragraphs in the document
    for para in doc.paragraphs:
        text = para.text.strip()

        question_match = question_pattern.match(text)
        answer_match = answer_pattern.match(text)

        if question_match:
            # Found a question, save the current question-answer pair if it exists
            if current_question:
                faqs.append(current_question)
            # Start a new question-answer pair
            current_question = {'question': question_match.group(1), 'answer': ''}
        elif answer_match and current_question:
            # Found an answer, add it to the current question-answer pair
            current_question['answer'] = answer_match.group(1)

    # Add the last question-answer pair
    if current_question:
        faqs.append(current_question)

    # Write the JSON output to a file
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(faqs, f, ensure_ascii=False, indent=4)


# Usage
word_file_path = 'D://Anaconda3//envs//RetFAQ//FAQbackup_numbered.docx'
json_file_path = 'D://Anaconda3//envs//RetFAQ//output_faqs.json'
word_to_json(word_file_path, json_file_path)


