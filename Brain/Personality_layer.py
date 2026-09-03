from config.personality import RESPONSIBILITY_DISTRIBUTION, AB5C_DESCRIPTORS, EMOTIONAL_CLASS, EMOTIONAL_BIAS_TEMPLATES, BIG_FIVE_EMOTION_MAP
import json
from Simulation.mind_state import MindState
from Brain.Emotion_layer import EmotionLayer
import math
import os

class PersonalityLayer:

    MAX_SELECTION_THRESHOLD = 0.5
    PERSONALITY_SHIFT_RATE = 0.02
    MINIMUM_ACTIVATION_THRESHOLD = 0.15

    def __init__(self, mind_state:MindState, emotion_layer: EmotionLayer):
        self.ocean = {
            "openness":0.0,
            "conscientiousness":0.0,
            "extraversion":0.0,
            "agreeableness":0.0,
            "neuroticism":0.0
        }
        self.mind_state = mind_state
        self.emotion_layer = emotion_layer

        self.emotional_biases = {}
        with open(os.path.join("config", "Descriptor_scaled_DNA.json"), "r") as file:
            self.emotional_biases = json.load(file)

        self.responsibility_weight = {
             "core" : 1.0,
             "supporting" : 0.5,
             "contradicting" : -0.5
        }

        self.intensity_weight = {
             "V" : 0.1,
             "L" : 0.4,
             "M" : 0.7,
             "H" : 1.0
        }

        self.zone_matchup = {
            "V" : "LOW",
            "L" : "LOW",
            "M" : "MEDIUM",
            "H" : "HIGH"
        }

        self.active_personality_traits = {}
    def get_selected_traits(self, distribution):
            selected_traits = {}
            sorted_distribution = sorted(
                    distribution.items(),
                    key=lambda x: abs(x[1]),
                    reverse=True
                )
                
            for trait, value in sorted_distribution:
                if abs(value) >= self.MAX_SELECTION_THRESHOLD:
                    selected_traits[trait] = value
                
            for trait, value in sorted_distribution:
                if len(selected_traits) >= 2:
                    break
                elif trait not in selected_traits:
                    selected_traits[trait] = value
            
            return selected_traits


    def generate_descriptor_family_biases(self):
            descriptor_family_biases = {}
            for descriptor, distribution in AB5C_DESCRIPTORS.items():
                family = {
                    "emotional_bias": 0,
                    "persistence_bias": 0,
                    "response_bias": 0
                }
                selected_traits = self.get_selected_traits(distribution)
                for trait, value in selected_traits.items():
                    family["emotional_bias"] += abs(value) * RESPONSIBILITY_DISTRIBUTION[trait]["emotional_bias"]
                    family["persistence_bias"] += abs(value) * RESPONSIBILITY_DISTRIBUTION[trait]["persistence_bias"]
                    family["response_bias"] += abs(value) * RESPONSIBILITY_DISTRIBUTION[trait]["response_bias"]
                
                total = sum(abs(value)
                            for value in selected_traits.values())

                for category in family:
                    family[category] = round(family[category] / total, 3)

                descriptor_family_biases[descriptor] = family
            

            with open("Descriptor_family_bias.json", "w") as file:
                json.dump(
                    descriptor_family_biases,
                    file,
                    indent=4,
                    ensure_ascii=False
                )
            return descriptor_family_biases 

    def classify_family_biases(self, margin: 0.15):

        family_biases = {}
        with open("Descriptor_family_bias.json", "r") as file:
                family_biases = json.load(file)

        classifications = {}
        for descriptor, biases in family_biases.items():
          
            sorted_biases = sorted(biases.items(), key=lambda x: x[1], reverse=True)
            top_family, top_value = sorted_biases[0]

            classes = {top_family : top_value}

            for family, value in sorted_biases[1:]:
                if(top_value - value) <= margin:
                    classes[family] = value

            classifications[descriptor] = classes

        with open ("Family_biases_real.json", "w") as file:
            json.dump(
                 classifications,
                 file,
                 indent=4,
                 ensure_ascii=False
            )

        return classifications

    def get_template(self, trait, loading):
        entry = EMOTIONAL_BIAS_TEMPLATES[trait]
        if(loading >= 0):
              direction = "positive"
        else:
             direction = "negative"

        template = entry[direction]
        return template

    def compute_DNA(self, loadings):
        numerator = {}
        descriptor_DNA = {}
        denominator = sum(abs(l) for l in loadings.values())
        for trait, loading in loadings.items():
            template = self.get_template(trait=trait, loading=loading)
            weight = abs(loading)
            for emotion, value in template.items():
                numerator[emotion] = numerator.get(emotion, 0.0) + weight * value

        if denominator == 0:
             return {}

        for emo, v in numerator.items():
             descriptor_DNA[emo] = round(v / denominator, 4)

        return descriptor_DNA

    def get_DNA(self):
        descriptor_DNA = {}
        for descriptor, contri in EMOTIONAL_CLASS.items():
            loadings = AB5C_DESCRIPTORS[descriptor.lower()]
            relevant_loadings = {t: l for t, l in loadings.items() if t != "conscientiousness"}
            DNA = self.compute_DNA(loadings=relevant_loadings)
            scaled_DNA = {emo: round(v * contri, 4) for emo, v in DNA.items()}
            descriptor_DNA[descriptor] = scaled_DNA

        with open("Descriptors_scaled_DNA.json", "w") as file:
             json.dump(
                  descriptor_DNA,
                  file,
                  indent=4,
                  ensure_ascii=False
             )

    def get_role_entry(self, emotion_map_role_list, emotion):
        for entry in emotion_map_role_list:
            if emotion in entry:
                return entry[emotion]
        return None

    def resolve_role_weight(self, emotion_map, emotion, bin_value):
        for role in ("core", "supporting", "contradicting"):
            entry = self.get_role_entry(emotion_map[role], emotion)
            if entry is None:
                continue
            zones = entry["zones"]

            if zones is None:
                return self.responsibility_weight[role]
            if bin_value in zones:
                return self.responsibility_weight[role]

        return 0.0
    
    def calculate_pattern_score(self, pattern):
        ordered_emotions = ["anger", "anticipation", "disgust", "fear", "joy", "sadness", "surprise", "trust"]
        emotion_pattern = dict(zip(ordered_emotions, pattern))
        scores = {}

        for trait in self.ocean:
            emotion_map = BIG_FIVE_EMOTION_MAP[trait]
            numerator = 0.0
            denominator = 0.0
            
            for emo, emo_p in emotion_pattern.items():
                bin_value = self.zone_matchup[emo_p]
                emo_role_weight = self.resolve_role_weight(emotion_map, emo, bin_value)
                if emo_role_weight == 0.0:
                    continue

                emo_intensity_weight = self.intensity_weight[emo_p]
                R_i_W_i = emo_role_weight * emo_intensity_weight

                numerator += R_i_W_i
                denominator += abs(R_i_W_i)

            scores[trait] = round(numerator/denominator, 4) if denominator != 0.0 else 0.0
        return scores

    def calculate_pattern_strength_with_memories(self, number_of_memories_in_pattern):
        return 1 - math.exp(-((self.PERSONALITY_SHIFT_RATE * number_of_memories_in_pattern) ** 2))

    def calculate_delta_G(self, k_old, k_new):
        return self.calculate_pattern_strength_with_memories(k_new) - self.calculate_pattern_strength_with_memories(k_old)

    def calculate_final_nudge(self, pattern, k_old, k_new):
        delta_G = self.calculate_delta_G(k_old, k_new)
        scores = self.calculate_pattern_score(pattern)
        total_nudge = {}
        for trait, pattern_score in scores.items():
            nudge = delta_G * pattern_score
            total_nudge[trait] = nudge

        for ocean_trait, nudge_value in total_nudge.items():
            if nudge_value > 0:
                self.ocean[ocean_trait] += nudge_value * (1 - self.ocean[ocean_trait])
            elif nudge_value < 0:
                self.ocean[ocean_trait] += nudge_value * (1 + self.ocean[ocean_trait])

        self.mind_state.personality_state["ocean"] = self.ocean

    def calculate_active_personality_traits(self):
        activation = {}
        self.active_personality_traits = {}
        for complex_trait, loadings in AB5C_DESCRIPTORS.items():
            complex_trait_numerator = 0.0
            complex_trait_denominator = 0.0
            for trait, loading_i in loadings.items():
                complex_trait_denominator += abs(loading_i)
                complex_trait_numerator += loading_i * self.ocean[trait]

            activation[complex_trait] = round(complex_trait_numerator/complex_trait_denominator, 4)

        for descriptor, descriptor_activation in activation.items():
            if abs(descriptor_activation) >= self.MINIMUM_ACTIVATION_THRESHOLD:
                self.active_personality_traits[descriptor] = descriptor_activation

        self.mind_state.personality_state["active_complex_traits"] = self.active_personality_traits

    def get_total_emotional_influence(self):
        final_emotional_influence = {}

        for descriptor, activation in self.active_personality_traits.items():
            if descriptor in EMOTIONAL_CLASS:
                emotional_influence_map = self.emotional_biases[descriptor]
                for emotion, DNA in emotional_influence_map.items():
                    final_emotional_influence[emotion] = final_emotional_influence.get(emotion, 0.0) + DNA * activation

        return final_emotional_influence

    def apply_emotional_influence(self):
        emotional_influence = self.get_total_emotional_influence()
        for emotion, influence in emotional_influence.items():
            current_value = self.emotion_layer.emotion_tanks[emotion]
            new_value = current_value + influence
            self.emotion_layer.emotion_tanks[emotion] = max(0.0, min(new_value, 1.0))
