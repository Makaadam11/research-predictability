import os
import joblib
import warnings
import pandas as pd
import numpy as np
from structs.columns import all_columns, numeric_columns, categorical_columns
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import RandomizedSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from sklearn.impute import SimpleImputer

PREPROCESSING_PATH = 'ml/preprocessing.sav'


def get_feature_lists():
    """Return the numeric and categorical feature lists used for ML."""
    numeric_feats = numeric_columns.copy()
    if 'actual' in numeric_feats:
        numeric_feats.remove('actual')

    categorical_feats = categorical_columns.copy()
    categorical_feats.remove('timetable_reasons')
    categorical_feats.remove('mental_health_activities')

    return numeric_feats, categorical_feats


EXCLUDE_COLUMNS = ['mental_health_activities', 'timetable_reasons', 'source', 'captured_at', 'predictions']


def train_and_save_model(X_train, y_train, model_type='RandomForest', suffix=''):
    """Train a model via RandomizedSearchCV and save to disk."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        if model_type == 'RandomForest':
            n_estimators = [int(x) for x in np.linspace(start=100, stop=1000, num=10)]
            max_features = ['sqrt', 'log2']
            max_depth = [int(x) for x in np.linspace(10, 110, num=11)]
            max_depth.append(None)
            min_samples_split = [2, 5, 10]
            min_samples_leaf = [1, 2, 4]
            bootstrap = [True, False]
            random_grid = {
                'n_estimators': n_estimators,
                'max_features': max_features,
                'max_depth': max_depth,
                'min_samples_split': min_samples_split,
                'min_samples_leaf': min_samples_leaf,
                'bootstrap': bootstrap
            }
            base_model = RandomForestClassifier(random_state=42)

        elif model_type == 'NeuralNetwork':
            hidden_layer_sizes = [(50, 50, 50), (50, 100, 50), (100,), (150, 100, 50)]
            activation = ['tanh', 'relu']
            solver = ['sgd', 'adam']
            alpha = [0.0001, 0.05, 0.01]
            learning_rate = ['constant', 'adaptive']
            random_grid = {
                'hidden_layer_sizes': hidden_layer_sizes,
                'activation': activation,
                'solver': solver,
                'alpha': alpha,
                'learning_rate': learning_rate
            }
            base_model = MLPClassifier(max_iter=1000, early_stopping=True, random_state=42)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

        model_random = RandomizedSearchCV(
            estimator=base_model,
            param_distributions=random_grid,
            n_iter=100, cv=3, verbose=0, random_state=42, n_jobs=-1
        )
        model_random.fit(X_train, y_train)
        best_model = model_random.best_estimator_

        model_filename = f'ml/{model_type}_{suffix}_model.sav'
        joblib.dump(best_model, model_filename)
        print(f"Saved {model_type} ({suffix}) model to {model_filename}")


def train_all_models(data_path='../data/merged/merged_data.xlsx'):
    """
    Train all models on the FULL Yes/No dataset and save preprocessing artifacts.
    Run this separately when you want to retrain models.
    """
    warnings.filterwarnings('ignore')

    # Load data with dual headers
    df = pd.read_excel(data_path, header=[0, 1])
    df.columns = all_columns

    numeric_feats, categorical_feats = get_feature_lists()

    # Keep only Yes/No records for training
    df_train = df[df['actual'].isin(['Yes', 'No', 1, 0])].copy()
    df_train['actual'] = df_train['actual'].map({'Yes': 1, 'No': 0, 1: 1, 0: 0})
    df_train = df_train.dropna(subset=['actual'])

    print(f"Training data: {len(df_train)} records")
    print(f"Class distribution:\n{df_train['actual'].value_counts()}")

    # Drop non-feature columns
    df_train = df_train.drop(columns=[c for c in EXCLUDE_COLUMNS if c in df_train.columns])

    # Encode numeric
    for col in numeric_feats:
        if col in df_train.columns:
            df_train[col] = pd.to_numeric(df_train[col], errors='coerce')

    # Encode categorical - save encoders and mode values
    encoders = {}
    mode_values = {}
    for col in categorical_feats:
        if col in df_train.columns:
            mode_val = str(df_train[col].mode().iloc[0])
            mode_values[col] = mode_val
            df_train[col] = df_train[col].fillna(mode_val).astype(str)
            le = LabelEncoder()
            df_train[col] = le.fit_transform(df_train[col])
            encoders[col] = le

    X = df_train[numeric_feats + categorical_feats]
    y = df_train['actual'].values

    # Impute missing numeric values
    imputer = SimpleImputer(strategy='median')
    X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=X.columns, index=X.index)

    # Scale numeric features only
    scaler = StandardScaler()
    X_scaled = X_imputed.copy()
    X_scaled[numeric_feats] = scaler.fit_transform(X_imputed[numeric_feats])

    # Save preprocessing artifacts
    preprocessing = {
        'encoders': encoders,
        'mode_values': mode_values,
        'scaler': scaler,
        'imputer': imputer,
        'numeric_features': numeric_feats,
        'categorical_features': categorical_feats,
    }
    joblib.dump(preprocessing, PREPROCESSING_PATH)
    print("Saved preprocessing artifacts.")

    # Train models on full dataset (no train/test split - all data used for production)
    X_values = X_scaled.values

    for model_type in ['RandomForest', 'NeuralNetwork']:
        # Original (no SMOTE)
        print(f"\nTraining {model_type} (original) on {len(X_values)} samples...")
        train_and_save_model(X_values, y, model_type, 'original')

        # With SMOTE
        smote = SMOTE(random_state=42)
        X_resampled, y_resampled = smote.fit_resample(X_values, y)
        print(f"Training {model_type} (smote) on {len(X_resampled)} samples...")
        train_and_save_model(X_resampled, y_resampled, model_type, 'smote')

    print("\nAll models trained and saved successfully.")


def predict_new_data(df, model_name='RandomForest_smote'):
    """
    Predict mental health proneness for 'Prefer not to say' records.
    Uses saved preprocessing artifacts and a pre-trained model.

    Args:
        df: DataFrame read with header=[0,1] from the merged Excel file.
        model_name: Name of the model to use (e.g. 'RandomForest_smote').

    Returns:
        DataFrame with all_columns as headers and updated 'predictions' column.
    """
    warnings.filterwarnings('ignore')

    df.columns = all_columns

    # Load preprocessing artifacts
    if not os.path.exists(PREPROCESSING_PATH):
        raise FileNotFoundError(
            f"Preprocessing artifacts not found at '{PREPROCESSING_PATH}'. "
            "Run train_all_models() first."
        )

    preprocessing = joblib.load(PREPROCESSING_PATH)
    encoders = preprocessing['encoders']
    mode_values = preprocessing['mode_values']
    scaler = preprocessing['scaler']
    imputer = preprocessing['imputer']
    numeric_feats = preprocessing['numeric_features']
    categorical_feats = preprocessing['categorical_features']

    # Set predictions based on known actual values
    # Yes -> 1, No -> 0
    known_yes = df['actual'].isin(['Yes', 1])
    known_no = df['actual'].isin(['No', 0])
    predict_mask = ~(known_yes | known_no)

    df['predictions'] = 0
    df.loc[known_yes, 'predictions'] = 1
    df.loc[known_no, 'predictions'] = 0

    if predict_mask.sum() == 0:
        print("No 'Prefer not to say' records to predict.")
        return df

    print(f"Predicting for {predict_mask.sum()} 'Prefer not to say' records...")

    # Prepare features for prediction rows only
    df_predict = df.loc[predict_mask].copy()

    # Numeric encoding
    for col in numeric_feats:
        if col in df_predict.columns:
            df_predict[col] = pd.to_numeric(df_predict[col], errors='coerce')

    # Categorical encoding using saved encoders
    for col in categorical_feats:
        if col in df_predict.columns:
            mode_val = mode_values.get(col, '')
            df_predict[col] = df_predict[col].fillna(mode_val).astype(str)
            le = encoders[col]
            # Handle unseen categories by mapping to 0 (most frequent encoded class)
            df_predict[col] = df_predict[col].apply(
                lambda x, _le=le: _le.transform([x])[0] if x in _le.classes_ else 0
            )

    X = df_predict[numeric_feats + categorical_feats].values

    # Apply saved imputer and scaler (transform only, not fit)
    X = imputer.transform(X)
    X[:, :len(numeric_feats)] = scaler.transform(X[:, :len(numeric_feats)])

    # Load pre-trained model and predict
    model_path = f'ml/{model_name}_model.sav'
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: '{model_path}'")

    model = joblib.load(model_path)
    predictions = model.predict(X)

    df.loc[predict_mask, 'predictions'] = predictions

    print(f"Predictions complete: {dict(pd.Series(predictions).value_counts())}")
    print(f"  Predicted prone (1): {(predictions == 1).sum()}")
    print(f"  Predicted not prone (0): {(predictions == 0).sum()}")

    return df


# Keep backward-compatible alias for existing imports
def evaluate_data(df, suppress_warnings=True):
    """Alias for predict_new_data for backward compatibility."""
    return predict_new_data(df)


if __name__ == "__main__":
    print("Training all models on full dataset...")
    train_all_models()
