import os
from ollama import chat
from ollama import ChatResponse


def get_file_content(file: str) -> str:
    file_content = ''
    with open(file, 'r') as f:
        file_content = f.read()
    return file_content


def get_code_fix_diff(files: list[str]) -> str:
    file_contents = [get_file_content(file) for file in files]
    formatted_contents = '\n\n'.join(f'```python\n{content}\n```' for content in file_contents)
    response: ChatResponse = chat(model='gemma3:1b', messages=[
    {
        'role': 'user',
        'content': f"""Fix the following code and output the response as a diff file:
            {formatted_contents}""",
    },
    ])
    return response['message']['content']


def main():
    test_suite_dir = 'eval_suite'

    for file in os.listdir(test_suite_dir):
        test_case_path = os.path.join(test_suite_dir, file)
        
        if os.path.isfile(test_case_path):
            continue
        
        bad_code_dir = os.path.join(test_suite_dir, file, 'original')
        
        if not os.path.isdir(bad_code_dir):
            continue

        source_files = []
        for root, _, files in os.walk(bad_code_dir):
            for filename in files:
                if filename.endswith('.py'):
                    source_files.append(os.path.join(root, filename))
        
        diff_output = get_code_fix_diff(source_files)
        print(f'--- Fixes for test case: {file} ---')
        print(diff_output)
        print('-----------------------------------\n')


if __name__ == "__main__":
    main()
