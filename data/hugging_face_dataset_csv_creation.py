from datasets import load_dataset
import pandas as pd

def strip_hugging_phase(text, rows=1000, csv_filename="dataset.csv"):
    file_path = text.replace("https://huggingface.co/datasets/", "") \
                    .replace("http://huggingface.co/datasets/", "") \
                    .strip("/")

    dataset = load_dataset(file_path, name="wikipedia", split=f"train[:{rows}]")
    df = pd.DataFrame(dataset)
    df.to_csv(csv_filename, index=False)

    return csv_filename

print("What is the Hugging Face dataset:")
hugging_phase = input()
strip_hugging_phase(hugging_phase)

    


