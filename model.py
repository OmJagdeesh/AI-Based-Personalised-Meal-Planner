import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util
import os

class MealRecommender:
    def __init__(self, data_path="data/recipes.csv"):
        # Load data using Pandas
        self.df = pd.read_csv(data_path)
        
        # We use a very lightweight sentence-transformer model (PyTorch based)
        # all-MiniLM-L6-v2 is extremely fast on CPU and highly effective
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Pre-compute embeddings for all recipes based on their attributes
        self._compute_recipe_embeddings()

    def _compute_recipe_embeddings(self):
        """Create a rich text representation for each recipe and encode it."""
        texts = []
        for _, row in self.df.iterrows():
            # Combine nutritional info, tags, and description for a holistic embedding
            text = (
                f"{row['recipe_name']} - {row['description']}. "
                f"Cuisine: {row['cuisine']}. Dietary tags: {row['dietary']}. "
                f"Macros: {row['calories']} calories, {row['protein_g']}g protein, "
                f"{row['carbs_g']}g carbs, {row['fat_g']}g fat. "
                f"Ingredients: {row['ingredients']}"
            )
            texts.append(text)
        
        # Compute embeddings (tensor of shape [num_recipes, embedding_dim])
        self.recipe_embeddings = self.model.encode(texts, convert_to_tensor=True)

    def recommend_meals(self, user_profile, top_k=3):
        """
        Takes a user profile dictionary, creates a query, and retrieves the closest matching recipes.
        """
        # Formulate a query based on the user's needs
        query_text = (
            f"Looking for a {user_profile['meal_type']} meal. "
            f"Cuisine: {user_profile['cuisine_type']}. "
            f"Dietary restrictions: {user_profile['dietary_restrictions']}. "
            f"Target macros: ~{user_profile['calories']} calories, {user_profile['protein']}g protein, "
            f"{user_profile['carbs']}g carbs, {user_profile['fat']}g fat."
        )

        # Encode the user query
        query_embedding = self.model.encode(query_text, convert_to_tensor=True)

        # Compute cosine similarities between the query and all recipes
        cos_scores = util.cos_sim(query_embedding, self.recipe_embeddings)[0]

        # Get the top_k highest scores
        top_results = torch.topk(cos_scores, k=min(top_k, len(self.df)))

        recommendations = []
        for score, idx in zip(top_results[0], top_results[1]):
            recipe = self.df.iloc[idx.item()].to_dict()
            recipe['match_score'] = round(score.item() * 100, 1) # Convert to percentage
            recommendations.append(recipe)

        return recommendations
