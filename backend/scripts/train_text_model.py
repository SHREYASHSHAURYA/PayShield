from pathlib import Path
import sys

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.services.ml_engine.features import build_training_frame


DATA_FILE = BASE_DIR / "data" / "processed" / "sms_training.csv"
MODEL_FILE = BASE_DIR / "models_store" / "scam_text_pipeline.joblib"

NUMERIC_COLUMNS = [
    "amount_score",
    "qr_present",
    "collect_request_present",
    "payment_link_present",
    "upi_present",
    "send_direction",
    "receive_direction",
    "pressure_flag",
    "impersonation_flag",
    "remote_access_flag",
]


def main() -> None:
    df = pd.read_csv(DATA_FILE)
    X = build_training_frame(df["text"].astype(str))
    y = df["label"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "text",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.95,
                    sublinear_tf=True,
                ),
                "text",
            ),
            (
                "numeric",
                "passthrough",
                NUMERIC_COLUMNS,
            ),
        ]
    )

    pipeline = Pipeline(
        steps=[
            ("features", preprocessor),
            (
                "clf",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=2000,
                    random_state=42,
                ),
            ),
        ]
    )

    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_FILE)

    print(f"saved={MODEL_FILE}")
    print(classification_report(y_test, predictions, digits=4))


if __name__ == "__main__":
    main()
