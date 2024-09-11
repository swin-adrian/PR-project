# Load the required libraries
import joblib
import numpy as np

# Load the saved logistic regression model
logreg_model = joblib.load('logreg_model.pkl')

# Function to predict the probability of PR
def predict_pr_probability(age, prtype, english, overseaexp, ausexp, eduqual, auseduqual, desregarea, speceduqual, acl, partqual, profyear):
    # Arrange the inputs into the format expected by the model
    input_data = np.array([[age, prtype, english, overseaexp, ausexp, eduqual, auseduqual, desregarea, speceduqual, acl, partqual, profyear]])
    
    # Use the model to predict the probability (use predict_proba)
    probability = logreg_model.predict_proba(input_data)
    
    # Return the probability for PR outcome 1 (PR invitation)
    return probability[0][1]  # The second column contains the probability for class 1 (PR invitation)

# Example usage
pr_probability = predict_pr_probability(55, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0)
print(f"Probability of PR invitation: {pr_probability * 100:.2f}%")
