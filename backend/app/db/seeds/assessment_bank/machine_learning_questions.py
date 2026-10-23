"""
Machine Learning Question Bank.
Contains 30 verified questions (10 basic, 10 intermediate, 10 advanced).
"""

MACHINE_LEARNING_QUESTIONS = [
    # ─── BASIC (10 Questions) ───────────────────────────────────────────
    {
        "difficulty": "basic",
        "topic": "ML Paradigms",
        "prompt_text": "What characterizes Supervised Learning compared to Unsupervised Learning?",
        "code_snippet": None,
        "options": [
            "Supervised learning requires human engineers to manually tune weights during training.",
            "Supervised learning trains models on labeled input-output pairs (features and target ground truth), whereas unsupervised learning discovers patterns and structures from unlabeled data.",
            "Supervised learning only works on numerical image data.",
            "Unsupervised learning always produces higher accuracy than supervised learning."
        ],
        "correct_option_index": 1,
        "explanation": "Supervised learning algorithms are provided training examples with input features and known target labels (y). Unsupervised learning operates on data without explicit target labels, discovering clustering or manifold representations."
    },
    {
        "difficulty": "basic",
        "topic": "Regression vs Classification",
        "prompt_text": "Which of the following predictive modeling tasks is a Regression problem?",
        "code_snippet": None,
        "options": [
            "Predicting whether a bank transaction is fraudulent or legitimate (binary).",
            "Classifying an email into Spam, Social, or Primary categories (multiclass).",
            "Predicting the numerical selling price of a residential house in dollars (continuous).",
            "Identifying whether an MRI scan contains a malignant tumor."
        ],
        "correct_option_index": 2,
        "explanation": "Regression models predict continuous numerical quantities (e.g. house price in dollars, temperature, stock return). Classification models predict categorical or discrete class labels."
    },
    {
        "difficulty": "basic",
        "topic": "Loss Functions: MSE vs MAE",
        "prompt_text": "How does Mean Squared Error (MSE) penalize large prediction errors compared to Mean Absolute Error (MAE)?",
        "code_snippet": "MSE = (1/n) * sum((y_true - y_pred)**2)\nMAE = (1/n) * sum(abs(y_true - y_pred))",
        "options": [
            "MSE penalizes all errors linearly regardless of magnitude.",
            "Because MSE squares the residual errors, it penalizes large outlier errors disproportionately more severely than MAE.",
            "MAE produces higher penalties for large errors than MSE.",
            "MSE is insensitive to outliers."
        ],
        "correct_option_index": 1,
        "explanation": "Squaring the difference in MSE causes larger errors to contribute exponentially more to the overall loss, making MSE models more sensitive to outliers than MAE (which uses absolute linear differences)."
    },
    {
        "difficulty": "basic",
        "topic": "Train/Test Split & Data Leakage",
        "prompt_text": "Why must feature scaling (like StandardScaler fit) be applied strictly to the training set and not the combined dataset before train/test splitting?",
        "code_snippet": None,
        "options": [
            "Because testing sets cannot contain numbers with decimal points.",
            "To prevent data leakage: fitting on the combined data leaks statistical properties (mean and standard deviation) of the unseen test set into the training process, producing artificially optimistic evaluation metrics.",
            "Scaling algorithms crash if applied to more than 1000 rows.",
            "The test set must always have a mean of 100."
        ],
        "correct_option_index": 1,
        "explanation": "Data leakage occurs when information from outside the training dataset is used to create the model. Fitting scalers on the full dataset leaks test set distribution into the training pipeline, invalidating performance estimates."
    },
    {
        "difficulty": "basic",
        "topic": "Overfitting & Underfitting",
        "prompt_text": "What symptoms indicate that a machine learning model is severely OVERFITTING?",
        "code_snippet": None,
        "options": [
            "High training error and high test error.",
            "Near-zero training error but substantially higher test error (poor generalization to unseen data).",
            "Fast training times and low parameter counts.",
            "High bias and low variance."
        ],
        "correct_option_index": 1,
        "explanation": "Overfitting (high variance) occurs when a model memorizes noise and idiosyncrasies in the training data, achieving near-perfect training performance but failing to generalize to unseen test data."
    },
    {
        "difficulty": "basic",
        "topic": "Categorical Encoding",
        "prompt_text": "When is One-Hot Encoding generally preferred over Label Encoding for nominal categorical features like [\"Red\", \"Green\", \"Blue\"]?",
        "code_snippet": None,
        "options": [
            "When the categorical feature has over 1,000,000 unique cardinalities.",
            "When the categories have no inherent ordinal ranking; Label Encoding (assigning 0, 1, 2) can mislead linear models into inferring that Blue (2) is greater than Red (0).",
            "One-Hot Encoding is only used for text processing with BERT.",
            "Label Encoding is prohibited in Python."
        ],
        "correct_option_index": 1,
        "explanation": "Label encoding assigns integer ranks that algorithms (linear models, distance-based algorithms) interpret as ordered numerical magnitudes. For nominal data with no natural hierarchy, One-Hot Encoding creates binary indicator columns to prevent spurious ordinal assumptions."
    },
    {
        "difficulty": "basic",
        "topic": "Feature Scaling",
        "prompt_text": "Why do distance-based algorithms like K-Nearest Neighbors (KNN) and Support Vector Machines (SVM) require feature scaling?",
        "code_snippet": None,
        "options": [
            "Without scaling, distance metrics (e.g. Euclidean distance) will be dominated by features with arbitrarily larger numerical ranges (like Annual Income vs Age).",
            "Distance-based algorithms cannot process floating-point numbers.",
            "Scaling increases the number of features in the dataset.",
            "Feature scaling eliminates all missing values automatically."
        ],
        "correct_option_index": 0,
        "explanation": "Euclidean distance is calculated as `sqrt(sum((x1 - x2)^2))`. Features with large ranges (e.g. salary in thousands) completely overshadow features with small ranges (e.g. age in tens), skewing distance computations unless standardized."
    },
    {
        "difficulty": "basic",
        "topic": "Evaluation Metrics: Precision vs Recall",
        "prompt_text": "In a cancer detection diagnostic model where failing to detect a present tumor (False Negative) is catastrophic, which metric should be prioritized?",
        "code_snippet": "Precision = TP / (TP + FP)\nRecall = TP / (TP + FN)",
        "options": [
            "Precision",
            "Recall (Sensitivity)",
            "Specificity",
            "Accuracy"
        ],
        "correct_option_index": 1,
        "explanation": "Recall measures the proportion of actual positive cases correctly identified (`TP / (TP + FN)`). When missing a positive case (False Negative) has severe consequences, maximizing Recall minimizes dangerous False Negatives."
    },
    {
        "difficulty": "basic",
        "topic": "Decision Trees: Splitting Criteria",
        "prompt_text": "What do metrics like Gini Impurity and Information Gain (Entropy) quantify when constructing a Classification Decision Tree?",
        "code_snippet": None,
        "options": [
            "The memory consumption of the tree nodes.",
            "The degree of class label mixing (impurity) within a node, helping the algorithm select splits that maximize node purity.",
            "The speed of network communication.",
            "The correlation between independent input features."
        ],
        "correct_option_index": 1,
        "explanation": "Splitting criteria evaluate node homogeneity. A node containing examples from only one class has zero impurity. The algorithm chooses candidate splits that maximize impurity reduction (information gain) to create pure leaf partitions."
    },
    {
        "difficulty": "basic",
        "topic": "K-Nearest Neighbors (KNN)",
        "prompt_text": "What happens if you set the hyperparameter K = 1 in a K-Nearest Neighbors classifier?",
        "code_snippet": None,
        "options": [
            "The model achieves high bias and underfits drastically.",
            "The decision boundary becomes highly complex and sensitive to noise and individual outliers, leading to high variance (overfitting).",
            "The classifier always outputs the majority class label.",
            "The training error on the training set becomes 100%."
        ],
        "correct_option_index": 1,
        "explanation": "At K=1, the model assigns the class of the single closest training point. This produces an extremely jagged, flexible decision boundary that captures noise and outliers, resulting in 0% training error but high variance (overfitting)."
    },

    # ─── INTERMEDIATE (10 Questions) ────────────────────────────────────
    {
        "difficulty": "intermediate",
        "topic": "Regularization: L1 vs L2",
        "prompt_text": "What unique mathematical property distinguishes L1 regularization (Lasso) from L2 regularization (Ridge)?",
        "code_snippet": "Lasso Loss = MSE + lambda * sum(abs(w))\nRidge Loss = MSE + lambda * sum(w**2)",
        "options": [
            "L2 regularization can only be applied to neural networks.",
            "L1 regularization drives less important feature weights strictly to zero, performing automatic feature selection and producing sparse models, whereas L2 shrinks weights toward zero without setting them exactly to zero.",
            "L1 regularization causes weights to grow exponentially.",
            "L2 regularization eliminates multicollinearity by deleting columns."
        ],
        "correct_option_index": 1,
        "explanation": "Due to the sharp geometric corners of the L1 norm diamond constraint budget, loss contours frequently intersect coordinate axes at zero, driving irrelevant weights strictly to zero (sparsity). L2 uses a smooth spherical penalty, shrinking weights continuously."
    },
    {
        "difficulty": "intermediate",
        "topic": "ROC-AUC Metric",
        "prompt_text": "What does an Area Under the ROC Curve (ROC-AUC) score of 0.5 represent for a binary classifier?",
        "code_snippet": None,
        "options": [
            "A perfect classifier with zero false positives.",
            "Performance no better than random guessing.",
            "A model that always predicts the positive class.",
            "A classifier that achieves 50% precision and 100% recall."
        ],
        "correct_option_index": 1,
        "explanation": "The ROC curve plots True Positive Rate vs False Positive Rate across all classification probability thresholds. An AUC of 1.0 indicates perfect discrimination; an AUC of 0.5 corresponds to the diagonal line representing random chance."
    },
    {
        "difficulty": "intermediate",
        "topic": "Cross-Validation: Stratified K-Fold",
        "prompt_text": "Why is Stratified K-Fold cross-validation essential when evaluating models on imbalanced classification datasets (e.g. 98% negative, 2% positive)?",
        "code_snippet": None,
        "options": [
            "It runs 10x faster than standard K-Fold.",
            "It guarantees that each fold contains approximately the same percentage of each target class as the complete dataset, preventing folds from having zero minority instances.",
            "It replaces missing data with the median value.",
            "It balances the dataset by synthesizing fake data."
        ],
        "correct_option_index": 1,
        "explanation": "Standard random K-Fold can accidentally allocate very few or zero positive instances into a validation fold when class imbalance is severe. Stratified K-Fold preserves the target class proportion across every split."
    },
    {
        "difficulty": "intermediate",
        "topic": "Bias-Variance Tradeoff",
        "prompt_text": "In the mathematical bias-variance decomposition of expected prediction error, what does the 'Bias' term capture?",
        "code_snippet": "Expected Error = Bias^2 + Variance + Irreducible Error",
        "options": [
            "The sensitivity of the model to small fluctuations in the training dataset.",
            "The error introduced by approximating a complex real-world phenomenon with an overly simplified model (e.g. fitting a straight line to quadratic data).",
            "Random sensor noise in the data collection process.",
            "The floating-point rounding error of the CPU."
        ],
        "correct_option_index": 1,
        "explanation": "Bias represents the erroneous assumptions in the learning algorithm. High bias models (e.g. linear regression on non-linear data) underfit because they fail to capture the underlying data patterns."
    },
    {
        "difficulty": "intermediate",
        "topic": "Ensemble Methods: Bagging vs Boosting",
        "prompt_text": "What is the primary difference in how base learners are trained in Bagging (e.g., Random Forests) versus Boosting (e.g., Gradient Boosting)?",
        "code_snippet": None,
        "options": [
            "Bagging trains trees sequentially to minimize bias; Boosting trains trees independently in parallel.",
            "Bagging trains multiple independent base learners in parallel on bootstrap samples of the data and aggregates them to reduce variance; Boosting trains base learners sequentially, where each new learner corrects errors made by predecessors to reduce bias.",
            "Bagging only works on neural networks; Boosting only works on linear regression.",
            "There is no difference; they are alternative names for the same algorithm."
        ],
        "correct_option_index": 1,
        "explanation": "Bagging (Bootstrap Aggregating) trains models independently in parallel and averages them to decrease variance. Boosting builds models iteratively in sequence, training each new learner on the pseudo-residuals or re-weighted errors of the prior ensemble to decrease bias."
    },
    {
        "difficulty": "intermediate",
        "topic": "Dimensionality Reduction: PCA",
        "prompt_text": "How does Principal Component Analysis (PCA) determine its principal component axes?",
        "code_snippet": None,
        "options": [
            "By selecting the features that have the highest correlation with the target label y.",
            "By computing the eigenvectors of the feature covariance matrix and ordering them by their eigenvalues (direction of maximum variance in the data).",
            "By randomly projecting data onto a 2D plane.",
            "By clustering data points using Euclidean distance."
        ],
        "correct_option_index": 1,
        "explanation": "PCA centers data and calculates the feature covariance matrix. The eigenvectors of this matrix define orthogonal axes of maximum variance, and their corresponding eigenvalues quantify the amount of variance explained along each axis."
    },
    {
        "difficulty": "intermediate",
        "topic": "Unsupervised Clustering: K-Means",
        "prompt_text": "What problem does the K-Means++ initialization algorithm solve compared to standard random centroid initialization?",
        "code_snippet": None,
        "options": [
            "It automatically determines the optimal number of clusters K without human input.",
            "It initializes cluster centroids far apart from each other with probability proportional to their squared distance from nearest existing centroids, reducing the likelihood of converging to poor local minima.",
            "It converts K-Means into a hierarchical clustering tree.",
            "It eliminates the need for distance metrics."
        ],
        "correct_option_index": 1,
        "explanation": "Standard K-Means randomly picks initial centroids, often clustering them closely together and getting trapped in poor local optima. K-Means++ spaces initial centroids out probabilistically, accelerating convergence and improving solution quality."
    },
    {
        "difficulty": "intermediate",
        "topic": "Gradient Descent Optimization",
        "prompt_text": "What is the trade-off between Stochastic Gradient Descent (SGD) with batch size = 1 and Full Batch Gradient Descent?",
        "code_snippet": None,
        "options": [
            "Full Batch GD converges faster per epoch than SGD.",
            "Full Batch GD computes exact gradients over the entire dataset (stable but memory-intensive and computationally slow per step); SGD updates parameters per sample (fast and noisy, helping escape shallow local minima, but has noisy fluctuations).",
            "SGD cannot be used with non-linear activation functions.",
            "Full Batch GD produces 0 loss on any problem."
        ],
        "correct_option_index": 1,
        "explanation": "Full Batch GD computes gradients over all n samples per step, which is computationally expensive for large datasets and can get stuck in saddle points. SGD uses one sample per update, providing fast, noisy steps that offer regularization and escape from shallow saddle points."
    },
    {
        "difficulty": "intermediate",
        "topic": "Neural Network Activation Functions: ReLU",
        "prompt_text": "Why did the Rectified Linear Unit (ReLU: f(x) = max(0, x)) largely displace the Sigmoid activation function in hidden layers of deep neural networks?",
        "code_snippet": "f(x) = max(0, x)",
        "options": [
            "ReLU limits output values to between 0 and 1.",
            "ReLU's derivative is 1 for all positive inputs, preventing the vanishing gradient problem that plagues Sigmoid's saturated tails during backpropagation, and computes significantly faster.",
            "ReLU prevents dead neurons under all conditions.",
            "ReLU requires fewer weights in dense layers."
        ],
        "correct_option_index": 1,
        "explanation": "Sigmoid saturates for large positive or negative values, yielding near-zero derivatives that cause vanishing gradients when chained across deep layers. ReLU has a constant derivative of 1 for x > 0, allowing gradients to propagate backward without decay."
    },
    {
        "difficulty": "intermediate",
        "topic": "Hyperparameter Tuning: Grid vs Random Search",
        "prompt_text": "Why does Random Search often outperform exhaustive Grid Search when tuning machine learning hyperparameters with equal computational budgets?",
        "code_snippet": None,
        "options": [
            "Grid search only checks integer values.",
            "Typically, only a small subset of hyperparameters strongly influence performance; Random Search samples unique values along all continuous dimensions rather than testing duplicate values along uninfluential dimensions.",
            "Random Search uses quantum computing.",
            "Grid Search is not supported in scikit-learn."
        ],
        "correct_option_index": 1,
        "explanation": "As shown by Bergstra and Bengio (2012), not all hyperparameters are equally important. Grid search wastes trials testing the same values of an important parameter with different uninfluential parameters. Random search explores more distinct values of the important hyperparameter."
    },

    # ─── ADVANCED (10 Questions) ─────────────────────────────────────────
    {
        "difficulty": "advanced",
        "topic": "Optimization: Adam vs AdamW",
        "prompt_text": "What critical flaw in the original Adam optimizer's L2 regularization implementation led to the creation of AdamW (Decoupled Weight Decay)?",
        "code_snippet": None,
        "options": [
            "Adam crashed when learning rates dropped below 1e-4.",
            "In original Adam, L2 regularization was added to the gradient, meaning weight decay was scaled by historical second moments (moving average of squared gradients) and effectively reduced for weights with large gradients; AdamW decouples weight decay directly from gradient updates.",
            "Adam failed on non-convex loss surfaces.",
            "AdamW removes momentum from optimizer states."
        ],
        "correct_option_index": 1,
        "explanation": "In standard Adam, adding L2 penalty to the gradient passes it through moving averages `m_t` and `v_t`. Weights with large gradients experience less effective decay than weights with small gradients. Loshchilov & Hutter (2019) resolved this in AdamW by decoupling weight decay directly: `w = w - lr * decay * w`."
    },
    {
        "difficulty": "advanced",
        "topic": "Loss Functions: Focal Loss",
        "prompt_text": "What is the primary mechanism of Focal Loss in dense object detection and extreme class imbalance?",
        "code_snippet": "FL(p_t) = -alpha_t * (1 - p_t)**gamma * log(p_t)",
        "options": [
            "It drops all negative examples from training.",
            "It adds a modulating factor `(1 - p_t)^gamma` to standard cross-entropy loss that down-weights easy, well-classified examples (p_t -> 1), focusing gradients on hard, misclassified instances.",
            "It replaces softmax with sigmoid in multi-class networks.",
            "It forces all weights to sum to 1."
        ],
        "correct_option_index": 1,
        "explanation": "In extreme class imbalance (e.g. 1 foreground object vs 100,000 background boxes), the vast quantity of easily classified negatives dominates gradient updates. Focal Loss dynamically scales loss by `(1 - p_t)^gamma`, suppressing easy negatives and prioritizing hard examples."
    },
    {
        "difficulty": "advanced",
        "topic": "Support Vector Machines: Kernel Trick",
        "prompt_text": "How does the Kernel Trick enable Support Vector Machines to construct non-linear decision boundaries in computationally feasible time?",
        "code_snippet": "K(x_i, x_j) = exp(-gamma * ||x_i - x_j||**2)",
        "options": [
            "By transforming input data using random decision tree splits.",
            "By computing the inner (dot) product of data points in a high- or infinite-dimensional Hilbert feature space directly using a kernel function K(x, z), without explicitly mapping data points into that costly high-dimensional space (Mercer's Theorem).",
            "By compressing vectors using discrete Fourier transforms.",
            "By training an ensemble of neural networks in parallel."
        ],
        "correct_option_index": 1,
        "explanation": "Explicitly mapping input vectors to high- or infinite-dimensional feature spaces (e.g. RBF kernel) is computationally prohibitive or impossible. Mercer's theorem guarantees that valid positive semi-definite kernel functions compute the inner product in that feature space directly in input space time."
    },
    {
        "difficulty": "advanced",
        "topic": "Manifold Learning: t-SNE vs UMAP",
        "prompt_text": "What fundamental mathematical advantage does UMAP (Uniform Manifold Approximation and Projection) possess over t-SNE for non-linear dimensionality reduction?",
        "code_snippet": None,
        "options": [
            "UMAP only works on 1D time series data.",
            "UMAP preserves global structure much better than t-SNE (which primarily preserves local neighborhoods) and scales significantly faster computationally via Riemannian geometry and fuzzy simplicial sets.",
            "t-SNE cannot project data into 2 dimensions.",
            "UMAP is a linear projection identical to PCA."
        ],
        "correct_option_index": 1,
        "explanation": "While t-SNE focuses on local cluster structure and distorts global inter-cluster relationships, UMAP leverages theoretical foundations in Riemannian geometry and algebraic topology to preserve both local and global manifold structure with substantially lower runtime complexity."
    },
    {
        "difficulty": "advanced",
        "topic": "Normalization: Batch Norm vs Layer Norm",
        "prompt_text": "Why is Layer Normalization (LayerNorm) predominantly used in Transformer architectures and recurrent models rather than Batch Normalization (BatchNorm)?",
        "code_snippet": None,
        "options": [
            "LayerNorm requires smaller GPU VRAM allocations than BatchNorm.",
            "BatchNorm normalizes across the batch dimension, which depends on batch size and fails with variable-length sequences or small batch sizes; LayerNorm normalizes across the hidden feature dimension independently for each sequence token/sample.",
            "BatchNorm cannot be differentiated during backpropagation.",
            "LayerNorm converts floats into 8-bit integers."
        ],
        "correct_option_index": 1,
        "explanation": "BatchNorm calculates mean and variance across the batch dimension, making it sensitive to batch size and unsuitable for variable sequence lengths in NLP. LayerNorm computes normalization statistics across the feature/channel dimension of a single sample, independent of other batch items."
    },
    {
        "difficulty": "advanced",
        "topic": "Imbalanced Data: SMOTE Mechanics",
        "prompt_text": "How does SMOTE (Synthetic Minority Over-sampling Technique) generate synthetic samples for the minority class?",
        "code_snippet": None,
        "options": [
            "By duplicating existing minority class records with random noise added to all features.",
            "By finding the k-nearest neighbors of a minority sample within the minority class, and interpolating random points along the line segments connecting the sample to its neighbors in feature space.",
            "By training a GAN generator on the majority class.",
            "By removing majority class samples until balance is reached."
        ],
        "correct_option_index": 1,
        "explanation": "Rather than naive duplication (which causes overfitting), SMOTE selects a minority instance, finds its k-nearest neighbors in the minority class, and synthesizes new examples by computing convex combinations (`x_new = x + rand(0, 1) * (x_neighbor - x)`)."
    },
    {
        "difficulty": "advanced",
        "topic": "Model Explainability: SHAP Values",
        "prompt_text": "What theoretical foundation from cooperative game theory guarantees the consistency and local accuracy of SHAP (Shapley Additive exPlanations) values?",
        "code_snippet": None,
        "options": [
            "Nash Equilibrium",
            "Shapley Values (fairly allocating the total payout of a coalition game among cooperating players, where players correspond to features and payout is model prediction).",
            "Pareto Optimality",
            "Prisoner's Dilemma matrix"
        ],
        "correct_option_index": 1,
        "explanation": "SHAP computes feature attributions based on classic Shapley values from cooperative game theory. It is the unique additive feature attribution method satisfying efficiency, symmetry, dummy player, and additivity axioms."
    },
    {
        "difficulty": "advanced",
        "topic": "Deep Learning: Vanishing & Exploding Gradients",
        "prompt_text": "In deep networks, what mathematical property of weight matrices causes exploding or vanishing gradients during backpropagation, and how does He/Kaiming initialization solve it?",
        "code_snippet": "w = np.random.randn(fan_in, fan_out) * np.sqrt(2.0 / fan_in)",
        "options": [
            "Singular values and eigenvalues: repeated matrix multiplications scale variance by factor product; Kaiming initialization sets weight variance to `2 / fan_in` to preserve activation and gradient variance across ReLU layers.",
            "Weights become complex imaginary numbers without Kaiming init.",
            "Floating-point mantissa underflow in PyTorch tensors.",
            "Kaiming initialization sets all weights to zero."
        ],
        "correct_option_index": 0,
        "explanation": "Repeated multiplication by weight matrices across L layers exponentially amplifies (if spectral radius > 1) or dampens (if spectral radius < 1) signal variance. Kaiming (He) initialization accounts for ReLU zeroing half of activations by calibrating variance to `2 / fan_in`, stabilizing variance across layers."
    },
    {
        "difficulty": "advanced",
        "topic": "Production ML: Concept Drift vs Covariate Shift",
        "prompt_text": "In production machine learning systems, what distinguishes Covariate Shift from Concept Drift?",
        "code_snippet": None,
        "options": [
            "Covariate shift occurs in SQL databases; concept drift occurs in NoSQL databases.",
            "Covariate Shift: the input feature distribution changes `P(X)` while the conditional ground truth relationship `P(Y|X)` remains constant; Concept Drift: the underlying relationship between inputs and targets `P(Y|X)` fundamentally changes over time.",
            "Covariate shift only affects neural networks.",
            "They are synonymous terms describing data format changes."
        ],
        "correct_option_index": 1,
        "explanation": "Covariate Shift occurs when input distributions shift (e.g. user demographics change, `P(X)` shifts) but the relationship `P(Y|X)` holds. Concept Drift occurs when the true relationship changes (e.g. macroeconomic shifts change consumer purchasing behavior, `P(Y|X)` shifts)."
    },
    {
        "difficulty": "advanced",
        "topic": "Bayesian Optimization for Hyperparameters",
        "prompt_text": "In Bayesian Optimization for hyperparameter tuning, what is the role of an Acquisition Function (such as Expected Improvement - EI)?",
        "code_snippet": None,
        "options": [
            "To clean and tokenize text datasets.",
            "To balance exploration (sampling regions of high model uncertainty) versus exploitation (sampling regions where the surrogate model predicts strong objective performance) to choose the next trial configuration.",
            "To automatically stop the training process when loss reaches zero.",
            "To compute gradients of non-differentiable code."
        ],
        "correct_option_index": 1,
        "explanation": "Bayesian Optimization fits a probabilistic surrogate (e.g., Gaussian Process) over the black-box objective. The Acquisition Function quantifies the utility of candidate points, mathematically balancing exploitation (high predicted score) and exploration (high uncertainty) to determine the next evaluation."
    }
]
