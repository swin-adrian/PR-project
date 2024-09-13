# Step 1: Import necessary libraries
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report, confusion_matrix

# Step 2: Load the dataset (assuming your dataset is in CSV format)
# Replace 'dataset.csv' with the actual file path if it's in CSV, 
# or adapt it to your file type as needed if using a different format
df = pd.read_csv('./data/pr_train_data.csv')

# Step 3: Inspect the dataset (optional)
print(df.head())
print(df.info())

# Step 4: Preprocess the data
# Separate features (X) and target variable (y)
X = df.drop('PR', axis=1)  # 'PR' is the target variable
y = df['PR']


# Step 6: Scaling numerical features (optional but recommended for Logistic Regression)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Step 7: Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Step 8: Instantiate and train the Logistic Regression model
log_reg = LogisticRegression()
log_reg.fit(X_train, y_train)

# Step 9: Make predictions on the test set
y_pred = log_reg.predict(X_test)
y_pred_proba = log_reg.predict_proba(X_test)[:, 1]  # Predicted probabilities

# Step 10: Evaluate the model's performance
accuracy = accuracy_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_pred_proba)
classification_rep = classification_report(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)

# Print the evaluation metrics
print(f'Accuracy: {accuracy}')
print(f'ROC-AUC Score: {roc_auc}')
print(f'Classification Report:\n{classification_rep}')
print(f'Confusion Matrix:\n{conf_matrix}')

joblib.dump(log_reg, 'logreg_model.pkl')
