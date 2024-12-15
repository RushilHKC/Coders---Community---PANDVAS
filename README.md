# legal-case-retrieval-system
Information Retrieval system to parse Boolean and free text queries to retrieve relevant law documents for a module's homework

Indexing: $ python index.py -i dataset-file -d dictionary-file -p postings-file

Searching: $ python search.py -d dictionary-file -p postings-file -q query-file -o output-file-of-results

# CourtSmart | LEGAL RESEARCH SOLUTION
Introducing CourtSmart – a pioneering NLP application designed to predict legal judgments with remarkable accuracy. Eliminate the uncertainties in legal decision-making and embrace efficiency and precision. CourtSmart leverages advanced natural language processing algorithms to analyze past cases, legal precedents, and relevant data, enabling accurate predictions of potential legal outcomes.

With CourtSmart, legal professionals can make well-informed decisions, save valuable time, and enhance their success rates. Harness the power of AI to transform the legal landscape and allow CourtSmart to guide you toward a more intelligent and efficient legal system.

Table of Contents:
Introduction
Modules
Models
Doc2Vec
1D-CNN
TextVectorization with TF-IDF
GloVe
BERT
Long Short-Term Memory (LSTM)

## Introduction
Natural Language Processing (NLP) has found extensive applications in the legal domain, particularly in tasks such as predicting the outcomes of legal judgments. Legal judgment prediction involves assessing the language of legal documents to forecast the outcomes of cases based on historical data.

CourtSmart is designed to analyze the language in legal cases and predict outcomes for similar cases by identifying patterns and trends in legal language. By employing CourtSmart, legal professionals can streamline their workflows, allocate resources more effectively, and make strategic decisions based on data-driven insights.

## Challenges in Legal Judgment Prediction
The task of legal judgment prediction presents significant challenges due to the complexity and variability of legal language. Legal documents often incorporate technical terminology, complex sentence structures, and domain-specific jargon, which can pose challenges for even advanced NLP models. Furthermore, legal outcomes can be influenced by a range of factors, such as the case's specific circumstances, the governing jurisdiction, and the personal judgment styles of presiding judges.

Despite these obstacles, advancements in NLP have shown encouraging results in legal judgment prediction. Researchers have successfully employed techniques like machine learning and deep learning to process legal language and achieve high-accuracy predictions of case outcomes. These approaches involve training models on extensive datasets of legal cases and applying these models to predict outcomes for new cases based on the language patterns in legal documents.

By combining cutting-edge NLP techniques with robust training datasets, CourtSmart offers a transformative tool for legal professionals, empowering them with insights to navigate the complexities of the legal system with confidence and precision.

# Modules
To maintain a structured and efficient codebase, the functionality of Court Smart has been organized into five distinct modules: preprocessing, plotting, utils, main, and deployment_utils.py. Each module plays a specific role in facilitating the development, analysis, and deployment of Court Smart's legal judgment prediction models.

### 1. Preprocessing Module
The Preprocessing module contains the Preprocessor class, which is responsible for various preprocessing tasks related to case facts, ensuring the input data is properly formatted and optimized for analysis. Key functionalities include:

Tokenization: Breaking down case facts into smaller, meaningful units.
Vectorization: Transforming text into numerical representations using various techniques.
Balancing: Ensuring data balance for unbiased training outcomes.
Anonymization: Removing sensitive or identifiable information from case facts.
Data Preprocessing: Handling data cleaning, normalization, and preparation for training.
These features are comprehensively explained in the Experiments section.

### 2. Plotting Module
The Plotting module includes the PlottingManager class, which is dedicated to visualizing the performance metrics of Court Smart's models. Key visualization capabilities include:

Loss and accuracy curves.
Heatmaps for detailed loss and accuracy analysis.
ROC-AUC (Receiver Operating Characteristic - Area Under Curve) curves.
Classification reports.
Confusion matrices for model evaluation.
These visualizations enable deeper insights into model performance and aid in fine-tuning for improved accuracy.

### 3. Utils Module
The Utils module contains reusable utility functions that streamline and support various processes across models. Notable functions include:

train_model(): Implements k-fold cross-validation for robust model training.
print_testing_loss_accuracy(): Summarizes testing loss and accuracy metrics for each fold.
calculate_average_measure(): Computes the average of specified performance measures, such as loss, validation loss, accuracy, and validation accuracy.
This module provides essential tools for efficient training and evaluation workflows.

### 4. Main Module
The Main module handles the deployment of Court Smart's frontend components, built using Streamlit. It provides a user-friendly interface for interacting with the models, visualizing predictions, and testing case facts.

### 5. Deployment Utils Module
The Deployment Utils module provides the necessary tools for deploying trained models and processing user inputs. Key features include:

generate_random_sample(): Fetches random samples from the testing set for validation.
generate_highlighted_words(): Highlights words in case facts that contribute significantly to the model's decision-making process.
VectorizerGenerator Class: Manages the creation of tokenizers and text vectorizers for models.
Predictor Class: Facilitates predictions and interprets model outputs.
This module bridges the gap between backend functionalities and user-facing applications, ensuring seamless deployment.

# Models
Court Smart employs a range of models to predict legal judgments with high accuracy. The following seven models, encompassing traditional and advanced techniques, were utilized to provide a comprehensive understanding of their efficacy:

### 1. Doc2Vec
Overview: Introduced by Quoc Le and Tomas Mikolov in "Distributed Representations of Sentences and Documents," Doc2Vec generates vector representations of entire documents, capturing contextual meaning.
Application: Ideal for representing legal cases holistically, enabling comparisons based on semantic relationships.

### 2. 1D-CNN
Overview: Derived from the concept of Convolutional Neural Networks (CNNs) used in image processing, 1D-CNN applies convolutional filters to textual data, extracting local and global features.
Application: Effective for capturing patterns in legal language across case facts and judgments.

### 3. Text Vectorization with TF-IDF
Text Vectorization: Converts textual data into numerical vectors using the TextVectorization layer in Keras. This layer tokenizes text and encodes each token as a unique integer.
TF-IDF (Term Frequency-Inverse Document Frequency): A statistical measure that evaluates the importance of a word in a document relative to its frequency across a corpus.
Application: Useful for identifying key terms in legal documents and reducing dimensionality in text-based datasets.

### 4. GloVe
Overview: GloVe (Global Vectors for Word Representation), introduced by Stanford researchers, captures semantic relationships between words using co-occurrence statistics.
Application: Enhances context understanding, making it effective for analyzing legal jargon and phrase associations.

### 5. BERT
Overview: Developed by Google, BERT (Bidirectional Encoder Representations from Transformers) is a state-of-the-art pre-trained language model. It captures context by analyzing words bidirectionally within a sentence.
Application: Highly effective for complex legal language tasks, such as precedent analysis and nuanced judgment prediction.

### 6. Long Short-Term Memory (LSTM)
Overview: LSTM networks, introduced by Hochreiter and Schmidhuber, address the limitations of traditional RNNs by retaining long-term dependencies in sequential data.
Application: Suitable for sequential patterns in legal cases, such as timelines and procedural dependencies.

### 7. FastText
Overview: FastText, developed by Facebook, extends word embeddings by considering subwords, allowing the model to understand rare and out-of-vocabulary terms.
Application: Beneficial for processing domain-specific legal terminology and rare phrases.

These models were selected to provide a balanced evaluation of traditional techniques (e.g., Doc2Vec) and advanced methodologies (e.g., BERT) to enhance Court Smart's accuracy and reliability in legal judgment prediction.
