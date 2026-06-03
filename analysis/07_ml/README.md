# ClassifyAnything

ClassifyAnything is a flexible tool designed to help you perform supervised classification on any type of 2D matrix data using Jupyter Notebooks. The main goals of this tool are:

1. To offer all the needed methods in each step for a hands-on experience.
2. To explain what's going on, so you can understand the process.
3. To help you pick the best model for your data.

## How to use this pipeline?

1. Clone this project into your local project folder.
2. Work on the Jupyter notebooks in order according to your purpose.
3. Follow the instruction and explanation step by step for exploring your data.
4. Wrap all the analyses into HTML reports by running `bash script_render_html.sh`.

## Configure the environment
```bash
conda env create -f conda_environment.yml
conda activate muscle-dnam-ml
```

Or use Pixi:

```bash
pixi install
pixi run rerun
```

## Supervised Learning Workflow

### 1. Data Loading and Preprocessing
[01_Preprocessing.ipynb](01_Preprocessing.ipynb)
    - Load the dataset into your Jupyter notebook
    - Explore the dataset
    - Perform necessary data preprocessing steps, such as:
        - Handling missing values
        - Handling outliers
        - Feature scaling or normalization

### 2. Leakage-Safe Model Selection and Training
[02_Model_Selection_Leakage_Safe.ipynb](02_Model_Selection_Leakage_Safe.ipynb)
    - Split the raw dataset into training and test sets first
        - Training dataset is used to fit all feature-selection steps and to fine-tune model hyperparameters with stratified k-fold validation.
        - Test dataset is kept held out and transformed only with selectors fitted on the training set.
        - This prevents information leakage from the test set into model training.
        - For fully unbiased cross-validation estimates, feature selection should be placed inside an sklearn `Pipeline`; in this workflow, the held-out test set is the primary unbiased benchmark.

#### 2-1. Logistic Regression:
[03-01_Logistic_Regression.ipynb](03-01_Logistic_Regression.ipynb)
   - Logistic regression models the relationship between input features and the probability of belonging to a particular class.
   - It is a linear model that uses a logistic function to map the output to a probability value.
   - Logistic regression is often used for binary classification tasks, but can be extended to multi-class classification as well.

#### 2-2. Decision Trees:
[03-02_Decision_Trees.ipynb](03-02_Decision_Trees.ipynb)
   - Decision trees partition the feature space into regions based on feature values and make predictions based on the majority class in each region.
   - They are intuitive and easy to interpret, as they represent a flowchart-like structure of if-else decision rules.

#### 2-3. Random Forests:
[03-03_Random_Forest.ipynb](03-03_Random_Forest.ipynb)
   - Random forests are an ensemble learning method that combines multiple decision trees to make predictions.
   - They create a set of decision trees using random subsets of features and average the predictions from individual trees to obtain the final prediction.
   - Random forests are known for their robustness and ability to handle high-dimensional data.

#### 2-4. Support Vector Machines (SVM):
[03-04_SVM.ipynb](03-04_SVM.ipynb)
   - SVMs find an optimal hyperplane that separates different classes by maximizing the margin between them.
   - They can handle linear and non-linear classification tasks by using different kernel functions.
   - SVMs work well with both small and large datasets and are effective in high-dimensional spaces.

#### 2-5. Naive Bayes:
   - Naive Bayes classifiers are based on Bayes' theorem and assume that features are conditionally independent given the class label.
   - They are computationally efficient and can handle large datasets.
   - Naive Bayes classifiers work well in situations where the independence assumption holds reasonably well.

#### 2-6. K-Nearest Neighbors (KNN):
   - KNN is a non-parametric algorithm that classifies new instances based on the class labels of k nearest neighbors in the training set.
   - It does not explicitly learn a model and relies on the proximity of instances in the feature space.
   - KNN can handle multi-class classification and can work well when the decision boundary is non-linear.

#### 2-7. Gradient Boosting methods:
   - Gradient Boosting methods, such as XGBoost and LightGBM, build an ensemble of weak prediction models in a sequential manner.
   - Each subsequent model corrects the errors made by the previous models, leading to improved performance.
   - Gradient Boosting methods often provide excellent predictive accuracy but require careful hyperparameter tuning.

These are just a few examples of supervised learning algorithms for classification tasks. The choice of algorithm depends on various factors such as the nature of the data, the size of the dataset, interpretability requirements, and performance goals. It's often useful to experiment with different algorithms and compare their performance to determine the most suitable one for your specific classification problem.

### 3. Exploratory Feature Selection
[03_Exploratory_Feature_Selection.ipynb](03_Exploratory_Feature_Selection.ipynb)
    - Exploratory feature-selection visualizations on the full dataset
    - Not used to generate the train/test matrices for model benchmarking in this corrected workflow
    - Do not use this notebook's selected features for final model training or reported test performance

### 4. Model Evaluation
    - Evaluate the trained model on the test set
    - Calculate and interpret the performance metrics relevant to your task, such as: Accuracy, Precision, Recall, F1-score.
    - Discuss the implications of the evaluation metrics in assessing the model's performance
