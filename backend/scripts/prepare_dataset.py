from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = BASE_DIR / "data" / "raw" / "uci_sms" / "SMSSpamCollection"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "sms_training.csv"


def main() -> None:
    rows = []

    with RAW_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.rstrip("\n")
            if not line:
                continue

            parts = line.split("\t", 1)
            if len(parts) != 2:
                continue

            raw_label, text = parts
            label = 1 if raw_label.strip().lower() == "spam" else 0

            rows.append(
                {
                    "text": text.strip(),
                    "label": label,
                    "source": "uci_sms",
                }
            )

    df = pd.DataFrame(rows, columns=["text", "label", "source"])
    df = (
        df[df["text"].astype(str).str.len() > 0]
        .drop_duplicates(subset=["text"])
        .reset_index(drop=True)
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"saved={OUTPUT_FILE}")
    print(f"rows={len(df)}")
    print(f"label_counts={df['label'].value_counts().to_dict()}")


if __name__ == "__main__":
    main()
