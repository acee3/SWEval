import os
from ollama import Client
from ollama import ChatResponse


def get_file_content(file: str) -> str:
    file_content = ''
    with open(file, 'r') as f:
        file_content = f.read()
    return file_content


def get_code_fix_diff(files: list[str]) -> str:
    client = Client(
        host="https://ollama.com",
        headers={'Authorization': 'Bearer ' + os.environ.get('OLLAMA_API_KEY')}
    )
    file_contents = [get_file_content(file) for file in files]
    formatted_contents = '\n\n'.join(f'```python\n{content}\n```' for content in file_contents)
    response: ChatResponse = client.chat(model='minimax-m2:cloud', messages=[
    {
        'role': 'user',
        'content': f"""Fix the bug in the following code and only output the contents of a unified diff that can directly be applied to the files. Do not include any explanations or additional text outside of the diff:
            {formatted_contents}""",
    },
    ])
    return response['message']['content'].strip()


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
