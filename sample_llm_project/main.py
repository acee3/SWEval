import os
from ollama import Client
from ollama import ChatResponse
import patch_ng as patch
import tempfile


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
    
    
    # TODO: Ensure proper format of the diff file
    
    
    return response['message']['content'].strip().removeprefix("```diff").removesuffix("```")


def apply_diff_to_file(file_path: str, diff: str) -> bool:
    with tempfile.NamedTemporaryFile('w', delete=True, encoding='utf-8', dir=file_path) as f:
        f.write(diff)
        pset = patch.fromfile(f.name)
        if not pset:
            print(f'Error: improper format for {file_path}\nDIFF:\n{diff}\n')
            return False
        patch_status = pset.apply(root=file_path)
        if not patch_status:
            print(f'Error: patch failed for {file_path}\nDIFF:\n{diff}\n')
            return False
    return True


def main():


    # TODO: Move this logic for trying all test cases to eval script and only have a function for a single test case here that receives a copy of the directory
    

    test_suite_dir = 'eval_suite'

    for file in os.listdir(test_suite_dir):
        test_case_path = os.path.join(test_suite_dir, file)
        
        if os.path.isfile(test_case_path):
            continue
        
        bad_code_dir = os.path.join(test_suite_dir, file, 'original')
        
        if not os.path.isdir(bad_code_dir):
            continue


        # TODO: Feed the file paths as well as the code to the LLM


        source_files = []
        for root, _, files in os.walk(bad_code_dir):
            for filename in files:
                if filename.endswith('.py'):
                    source_files.append(os.path.join(root, filename))
        
        diff_output = get_code_fix_diff(source_files)
        print(f'--- Fixes for test case: {file} ---')
        print(diff_output)
        print('-----------------------------------\n')
        
        apply_diff_to_file(bad_code_dir, diff_output)


if __name__ == "__main__":
    main()
