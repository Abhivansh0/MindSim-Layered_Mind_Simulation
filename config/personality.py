RESPONSIBILITY_DISTRIBUTION = {

    "openness":{

        "emotional_bias":0.4,
        "persistence_bias":0.0,
        "response_bias":0.6

    },
    "conscientiousness":{

        "emotional_bias":0.0,
        "persistence_bias":0.0,
        "response_bias":1.0

    },
    "extraversion":{

        "emotional_bias":0.6,
        "persistence_bias":0.0,
        "response_bias":0.4

    },
    "agreeableness":{

        "emotional_bias":0.3,
        "persistence_bias":0.0,
        "response_bias":0.7

    },
    "neuroticism":{

        "emotional_bias":0.4,
        "persistence_bias":0.5,
        "response_bias":0.1

    }
}

BIG_FIVE_EMOTION_MAP = {

    "openness": {
        "core": [
            {"surprise": {"zones": None}}
        ],
        "supporting": [
            {"anticipation": {"zones": None}},
            {"trust": {"zones": None}},
            {"joy": {"zones": None}}
        ],
        "contradicting": [
            {"fear": {"zones": None}},
            {"disgust": {"zones": None}}
        ]
    },

    "conscientiousness": {
        "core": [
            {"anticipation": {"zones": None}}
        ],
        "supporting": [
            {"trust": {"zones": None}},
            {"fear": {"zones": ["MEDIUM"]}},
            {"joy": {"zones": None}}
        ],
        "contradicting": [
            {"surprise": {"zones": None}},
            {"anger": {"zones": None}},
            {"fear": {"zones": ["LOW", "HIGH"]}}
        ]
    },

    "extraversion": {
        "core": [
            {"trust": {"zones": None}}
        ],
        "supporting": [
            {"anticipation": {"zones": None}},
            {"surprise": {"zones": None}},
            {"joy": {"zones": ["MEDIUM"]}}
        ],
        "contradicting": [
            {"sadness": {"zones": None}},
            {"fear": {"zones": None}},
            {"joy": {"zones": ["HIGH"]}}
        ]
    },

    "agreeableness": {
        "core": [
            {"trust": {"zones": None}}
        ],
        "supporting": [
            {"joy": {"zones": None}},
            {"sadness": {"zones": None}},
            {"disgust": {"zones": None}}
        ],
        "contradicting": [
            {"anger": {"zones": None}},
        ]
    },

    "neuroticism": {
        "core": [
            {"fear": {"zones": None}}
        ],
        "supporting": [
            {"sadness": {"zones": None}},
            {"anticipation": {"zones": None}},
            {"anger": {"zones": None}}
        ],
        "contradicting": [
            {"joy": {"zones": None}},
            {"trust": {"zones": None}}
        ]
    }
}

AB5C_DESCRIPTORS = {

    "gregariousness": {"extraversion":0.74, "agreeableness":0.09, "conscientiousness":0.00, "neuroticism":-0.19, "openness":0.07},
    "friendliness": {"extraversion":0.66, "agreeableness":0.43, "conscientiousness":0.19, "neuroticism":-0.32, "openness":0.17},
    "assertiveness": {"extraversion":0.61, "agreeableness":-0.01, "conscientiousness":0.41, "neuroticism":-0.38, "openness":0.12},
    "poise": {"extraversion":0.75, "agreeableness":0.19, "conscientiousness":0.07, "neuroticism":-0.45, "openness":0.12},
    "leadership": {"extraversion":0.65, "agreeableness":0.24, "conscientiousness":0.35, "neuroticism":-0.34, "openness":0.27},
    "provocativeness": {"extraversion":0.63, "agreeableness":0.02, "conscientiousness":0.06, "neuroticism":-0.27, "openness":0.14},
    "self_disclosure": {"extraversion":0.44, "agreeableness":0.30, "conscientiousness":-0.03, "neuroticism":-0.07, "openness":0.20},
    "talkativeness": {"extraversion":0.50, "agreeableness":0.05, "conscientiousness":-0.04, "neuroticism":0.04, "openness":0.21},
    "sociability": {"extraversion":0.48, "agreeableness":0.16, "conscientiousness":0.04, "neuroticism":-0.10, "openness":0.02},
    "understanding": {"extraversion":0.28, "agreeableness":0.58, "conscientiousness":0.31, "neuroticism":-0.15, "openness":0.30},
    "warmth": {"extraversion":0.62, "agreeableness":0.59, "conscientiousness":0.32, "neuroticism":-0.34, "openness":0.25},
    "morality": {"extraversion":0.09, "agreeableness":0.26, "conscientiousness":0.55, "neuroticism":-0.20, "openness":-0.13},
    "pleasantness": {"extraversion":0.23, "agreeableness":0.58, "conscientiousness":0.32, "neuroticism":-0.29, "openness":0.17},
    "empathy": {"extraversion":0.54, "agreeableness":0.40, "conscientiousness":0.44, "neuroticism":-0.32, "openness":0.35},
    "cooperation": {"extraversion":-0.13, "agreeableness":0.50, "conscientiousness":0.24, "neuroticism":-0.03, "openness":0.03},
    "sympathy": {"extraversion":0.46, "agreeableness":0.72, "conscientiousness":0.27, "neuroticism":-0.16, "openness":0.28},
    "tenderness": {"extraversion":0.26, "agreeableness":0.50, "conscientiousness":0.12, "neuroticism":0.01, "openness":0.36},
    "nurturance": {"extraversion":0.14, "agreeableness":0.63, "conscientiousness":0.28, "neuroticism":-0.15, "openness":0.14},
    "conscientiousness": {"extraversion":0.17, "agreeableness":0.22, "conscientiousness":0.79, "neuroticism":-0.22, "openness":-0.08},
    "efficiency": {"extraversion":0.24, "agreeableness":0.14, "conscientiousness":0.78, "neuroticism":-0.36, "openness":-0.10},
    "dutifulness": {"extraversion":-0.08, "agreeableness":0.28, "conscientiousness":0.54, "neuroticism":-0.14, "openness":-0.11},
    "purposefulness": {"extraversion":0.43, "agreeableness":0.23, "conscientiousness":0.80, "neuroticism":-0.38, "openness":-0.03},
    "organization": {"extraversion":0.33, "agreeableness":0.09, "conscientiousness":0.53, "neuroticism":-0.28, "openness":0.08},
    "cautiousness": {"extraversion":-0.24, "agreeableness":-0.05, "conscientiousness":0.59, "neuroticism":-0.07, "openness":-0.16},
    "rationality": {"extraversion":-0.01, "agreeableness":-0.28, "conscientiousness":0.01, "neuroticism":0.17, "openness":-0.29},
    "perfectionism": {"extraversion":0.24, "agreeableness":0.06, "conscientiousness":0.42, "neuroticism":0.11, "openness":0.05},
    "orderliness": {"extraversion":0.05, "agreeableness":0.08, "conscientiousness":0.64, "neuroticism":-0.15, "openness":-0.24},
    "stability": {"extraversion":0.14, "agreeableness":0.12, "conscientiousness":0.21, "neuroticism":-0.71, "openness":-0.11},
    "happiness": {"extraversion":0.42, "agreeableness":0.18, "conscientiousness":0.40, "neuroticism":-0.75, "openness":-0.14},
    "calmness": {"extraversion":0.10, "agreeableness":0.50, "conscientiousness":0.18, "neuroticism":-0.54, "openness":0.06},
    "moderation": {"extraversion":0.18, "agreeableness":0.14, "conscientiousness":0.63, "neuroticism":-0.51, "openness":-0.14},
    "toughness": {"extraversion":0.18, "agreeableness":0.09, "conscientiousness":0.34, "neuroticism":-0.72, "openness":-0.05},
    "impulse_control": {"extraversion":-0.23, "agreeableness":0.21, "conscientiousness":0.30, "neuroticism":-0.26, "openness":-0.14},
    "imperturbability": {"extraversion":-0.04, "agreeableness":-0.23, "conscientiousness":0.07, "neuroticism":-0.50, "openness":-0.29},
    "cool_headedness": {"extraversion":-0.12, "agreeableness":-0.09, "conscientiousness":-0.32, "neuroticism":-0.09, "openness":-0.21},
    "tranquility": {"extraversion":-0.09, "agreeableness":-0.23, "conscientiousness":0.13, "neuroticism":-0.46, "openness":-0.46},
    "intellect": {"extraversion":0.24, "agreeableness":-0.04, "conscientiousness":0.24, "neuroticism":-0.12, "openness":0.32},
    "ingenuity": {"extraversion":0.47, "agreeableness":0.03, "conscientiousness":0.24, "neuroticism":-0.33, "openness":0.30},
    "reflection": {"extraversion":0.34, "agreeableness":0.54, "conscientiousness":0.16, "neuroticism":-0.04, "openness":0.49},
    "competence": {"extraversion":0.47, "agreeableness":0.11, "conscientiousness":0.51, "neuroticism":-0.42, "openness":0.10},
    "quickness": {"extraversion":0.38, "agreeableness":0.02, "conscientiousness":0.44, "neuroticism":-0.37, "openness":0.15},
    "introspection": {"extraversion":-0.05, "agreeableness":-0.01, "conscientiousness":-0.17, "neuroticism":0.19, "openness":0.33},
    "creativity": {"extraversion":0.22, "agreeableness":0.03, "conscientiousness":0.27, "neuroticism":-0.27, "openness":0.49},
    "imagination": {"extraversion":0.23, "agreeableness":0.14, "conscientiousness":0.19, "neuroticism":-0.10, "openness":0.71},
    "depth": {"extraversion":0.18, "agreeableness":0.20, "conscientiousness":0.20, "neuroticism":-0.02, "openness":0.48}
}

# Final descriptor classification — 3 classes, values from Descriptor_family_bias.json
# emotional_bias / response_bias: margin-based (margin=0.15, relative to descriptor's top value)
# persistence_bias: structural (nonzero = Neuroticism was a top-2 selected trait for this descriptor)

EMOTIONAL_CLASS = {
    "gregariousness": 0.559,
    "friendliness": 0.482,
    "poise": 0.525,
    "provocativeness": 0.54,
    "self_disclosure": 0.478,
    "talkativeness": 0.541,
    "sociability": 0.525,
    "warmth": 0.454,
    "happiness": 0.472,
    "stability": 0.309,
    "calmness": 0.352,
    "toughness": 0.272,
    "imperturbability": 0.4,
    "tranquility": 0.4,
    "intellect": 0.486,
    "ingenuity": 0.517,
    "introspection": 0.4,
    "imagination": 0.449,
}  # 18 descriptors

RESPONSE_CLASS = {
    "friendliness": 0.518,
    "assertiveness": 0.641,
    "leadership": 0.61,
    "self_disclosure": 0.522,
    "talkativeness": 0.459,
    "sociability": 0.475,
    "understanding": 0.804,
    "warmth": 0.546,
    "morality": 0.904,
    "pleasantness": 0.807,
    "empathy": 0.669,
    "cooperation": 0.797,
    "sympathy": 0.583,
    "tenderness": 0.658,
    "nurturance": 0.792,
    "conscientiousness": 0.935,
    "efficiency": 0.716,
    "dutifulness": 0.898,
    "purposefulness": 0.79,
    "organization": 0.77,
    "cautiousness": 0.827,
    "rationality": 0.649,
    "perfectionism": 0.782,
    "orderliness": 0.891,
    "stability": 0.305,
    "calmness": 0.388,
    "moderation": 0.597,
    "toughness": 0.389,
    "impulse_control": 0.582,
    "imperturbability": 0.284,
    "cool_headedness": 0.842,
    "tranquility": 0.35,
    "intellect": 0.514,
    "reflection": 0.652,
    "competence": 0.712,
    "quickness": 0.722,
    "introspection": 0.417,
    "creativity": 0.742,
    "imagination": 0.551,
    "depth": 0.629,
}  # 39 descriptors

PERSISTENCE_CLASS = {
    "stability": 0.386,
    "toughness": 0.34,
    "happiness": 0.321,
    "imperturbability": 0.316,
    "calmness": 0.26,
    "tranquility": 0.25,
    "impulse_control": 0.232,
    "moderation": 0.224,
    "ingenuity": 0.206,
}  # 9 descriptors

EMOTIONAL_BIAS_TEMPLATES = { # THESE ARE JUST THE DEMO VALUES

    "neuroticism": {

        "positive": {
            "fear": 0.9,
            "sadness": 0.75,
            "anticipation": 0.5,
            "anger": 0.4,
            "trust": -0.6,
            "joy": -0.6
        },
        "negative": {
            "fear": -0.9,
            "sadness": -0.75,
            "anticipation": -0.5,
            "anger": -0.4,
            "trust": 0.6,
            "joy": 0.6
        }
    },

    "openness": {

        "positive": {
            "surprise": -0.4
        },
        "negative": {
            "surprise": 0.4,
            "fear": 0.35
        }
    },

    "extraversion": {

        "positive": {
            "joy": 0.7
        },
        "negative": {
            "anger": 0.5, 
            "fear": 0.55, 
            "disgust": 0.35,
            "sadness": 0.6, 
            "joy": -0.3
        }
    },

    "agreeableness": {

        "positive": {
            "fear": 0.4, 
            "sadness": 0.4, 
            "disgust": 0.45, 
            "anger": -0.55
        },
        "negative": {
            "anger": 0.55, 
            "trust": -0.5
        }
    },
}