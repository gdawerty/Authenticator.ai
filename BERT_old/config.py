"""
BERT Training Configuration for Authentia.ai Document Classification
"""

class BERTConfig:
    # Model Configuration
    MODEL_NAME = "bert-base-uncased"
    MAX_LENGTH = 512
    BATCH_SIZE = 16
    LEARNING_RATE = 2e-5
    NUM_EPOCHS = 5
    WARMUP_STEPS = 500
    WEIGHT_DECAY = 0.01
    
    # Training Configuration
    SEED = 42
    GRADIENT_ACCUMULATION_STEPS = 4
    MAX_GRAD_NORM = 1.0
    LOGGING_STEPS = 100
    SAVE_STEPS = 1000
    EVAL_STEPS = 1000
    
    # Data Configuration
    TRAIN_FILE = "../data/CLEANED/text_train.csv"
    VAL_FILE = "../data/CLEANED/text_val.csv"
    TEST_FILE = "../data/CLEANED/text_test.csv"
    
    # Output Configuration
    OUTPUT_DIR = "./bert_output"
    SAVE_TOTAL_LIMIT = 3
    
    # Categories for Classification
    CATEGORIES = [
        'Education',
        'Insurance', 
        'Legal',
        'Resume',
        'Admin',
        'Other'
    ]
    
    # Subcategories mapping
    SUBCATEGORIES = {
        'Education': ['transcript', 'report_card', 'certificate', 'diploma', 'assignment', 'test_paper'],
        'Insurance': ['claim_form', 'policy_document', 'damage_assessment', 'medical_record', 'accident_report'],
        'Legal': ['contract', 'legal_document', 'court_filing', 'agreement', 'legal_brief'],
        'Resume': ['resume', 'cv', 'cover_letter', 'job_application'],
        'Admin': ['form', 'application', 'permit', 'license', 'certificate'],
        'Other': ['general', 'unknown', 'miscellaneous']
    }
