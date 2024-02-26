import time
from os import listdir
from os.path import isfile, join

from openai import OpenAI, RateLimitError

client = OpenAI()


def process_file(filename):

    with open(filename) as f:
        source_code = f.read()

    if not source_code:
        print("Error reading source code")
        return

    success = False
    completion = None
    while not success:
        try:
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You will be provided with a piece of code, and your task is to explain it in a concise way.",
                    },
                    {"role": "user", "content": source_code},
                ],
            )
            success = True
        except RateLimitError as e:
            print(f"Rate limit error, sleeping. {e}")
            time.sleep(10)

    return completion.choices[0].message.content


def main():
    output_file_name = "../doc/example_code/example_summaries.rst"
    with open(output_file_name, "w") as output_file:
        output_file.write("Example Code\n")
        output_file.write("============\n\n")

        source_file_path = "../arcade/examples/"
        files_in_directory = [
            f for f in listdir(source_file_path) if isfile(join(source_file_path, f))
        ]

        count = 0
        for input_file_name in files_in_directory:
            print("Processing file {}".format(input_file_name))
            result = process_file(source_file_path + input_file_name)
            output_file.write(f"{input_file_name}\n")
            line = len(input_file_name) * "-"
            output_file.write(f"{line}\n")
            output_file.write(
                f".. image:: how_to_examples/{input_file_name[:-3]}.png\n\n"
            )
            output_file.write(f"Source: :ref:`{input_file_name[:-3]}`\n\n")
            output_file.write(result)
            output_file.write("\n\n")
            # if count >= 10:
            #     break

            count += 1


main()
