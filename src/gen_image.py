import os
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import PIL.Image

class AnimalClothesGenerator:
    """
    A class for generating images of animals dressed in different clothes using Google's Gemini AI.
    """
    
    def __init__(self, env_path="env/.env"):
        """
        Initialize the AnimalClothesGenerator with API client.
        Args:
            env_path (str): Path to the environment file containing API keys
        """
        # Always load from environment file (no API key argument)
        load_dotenv(env_path)
        self.client = genai.Client()
        
    def _analyze_animal_pose(self, animal_image_path):
        """
        Analyze the animal's pose from the input image.
        
        Args:
            animal_image_path (str): Path to the animal image
            
        Returns:
            str: Detailed description of the animal's pose
        """
        pose_analysis_prompt = ("Analyze this image of an animal and provide a detailed description for image generation purposes. This analysis will be used to generate a new image where the animal will be dressed in different clothes while maintaining the exact same pose and position. "
                               "Please describe in detail: "
                               "1. The animal's species and breed (if applicable) "
                               "2. The animal's pose, body position (sitting, standing, lying down, etc.), and visibility of the animal's body parts "
                               "3. The orientation of the animal's head and body "
                               "4. The position of the animal's legs, paws/hooves, and tail "
                               "5. The animal's facial expression and gaze direction "
                               "6. Any distinctive body language or posture details "
                               "IMPORTANT: This description will be used to generate a new image where the animal will wear different clothes. Please be extremely specific and detailed about the pose, positioning, body language, visibility, and scale so that the new generated image can maintain the exact same animal pose while only changing the clothing. Go straight to the description without preambles. "
                               "And as the clothes will be changed, please do not include any details about the animal's current wear, as it will be replaced with new clothes in the generated image.")

        image = PIL.Image.open(animal_image_path)
        
        print("Analyzing animal pose...")
        pose_response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[pose_analysis_prompt, image],
            config=types.GenerateContentConfig(
                response_modalities=['TEXT'],
                temperature=0.0,
            )
        )
        
        animal_pose_description = pose_response.candidates[0].content.parts[0].text
        print("Animal pose analysis:")
        print(animal_pose_description)
        print("\n" + "="*50 + "\n")
        
        return animal_pose_description
    
    def _load_clothes_description(self, clothes_description_path):
        """
        Load clothes description from a text file.
        
        Args:
            clothes_description_path (str): Path to the text file containing clothes description
            
        Returns:
            str: Clothes description text
        """
        if not os.path.exists(clothes_description_path):
            raise FileNotFoundError(f"Clothes description file not found: {clothes_description_path}")
        
        with open(clothes_description_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    
    def _create_generation_prompt(self, animal_pose_description, clothes_description):
        """
        Create the final prompt for image generation.
        
        Args:
            animal_pose_description (str): Description of the animal's pose
            clothes_description (str): Description of the clothes
            
        Returns:
            str: Complete prompt for image generation
        """
        return ("Create a photorealistic image using the provided reference images. The first image shows the animal that should be dressed, and the second image shows the clothes to be added. "
                "TASK: Dress the animal from the first image with the clothes from the second image. "
                f"ANIMAL POSE DETAILS (must be preserved exactly): {animal_pose_description} "
                f"CLOTHES DETAILS (must be replicated exactly): {clothes_description} "
                "IMPORTANT REQUIREMENTS: "
                "- Keep the exact same animal pose, body shape, and facial expression from the first image "
                "- Maintain the specific pose details described above "
                "- Only modify the animal by adding/changing the clothes to match the reference clothing from the second image "
                "- Replicate the exact texture, pattern, color, and fabric details described in the clothes analysis "
                "- Ensure the clothes fit naturally on the animal's body without altering the animal's anatomy "
                "- Clothes should appear realistically on the animal's body, adapting to the animal's specific body structure "
                "- Keep all other elements (background, foreground, lighting, animal's position) identical to the original first image")
    
    def generate_dressed_animal(self, animal_image_path, clothes_image_path, clothes_description_path, 
                              show_image=True, save_path=None):
        """
        Generate an image of an animal dressed in specified clothes.
        
        Args:
            animal_image_path (str): Path to the animal image
            clothes_image_path (str): Path to the clothes image
            clothes_description_path (str): Path to the text file containing clothes description
            show_image (bool): Whether to display the generated image
            save_path (str, optional): Path to save the generated image
            
        Returns:
            PIL.Image: Generated image object
        """
        # Validate input files
        if not os.path.exists(animal_image_path):
            raise FileNotFoundError(f"Animal image not found: {animal_image_path}")
        if not os.path.exists(clothes_image_path):
            raise FileNotFoundError(f"Clothes image not found: {clothes_image_path}")
        
        # Load images
        animal_image = PIL.Image.open(animal_image_path)
        clothes_image = PIL.Image.open(clothes_image_path)
        
        # Analyze animal pose
        animal_pose_description = self._analyze_animal_pose(animal_image_path)
        
        # Load clothes description
        clothes_description = self._load_clothes_description(clothes_description_path)
        
        # Create generation prompt
        text_input = self._create_generation_prompt(animal_pose_description, clothes_description)
        
        print("Generating image with enhanced prompt...")
        print("Final prompt:")
        print(text_input)
        print("\n" + "="*50 + "\n")
        
        # Generate image
        response = self.client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=[text_input, animal_image, clothes_image],
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE'],
                temperature=0.0,
            )
        )
        
        generated_image = None
        
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                generated_image = Image.open(BytesIO((part.inline_data.data)))
                
                if show_image:
                    generated_image.show()
                
                if save_path:
                    generated_image.save(save_path)
                    print(f"Image saved to: {save_path}")
        
        return generated_image


# Example usage
if __name__ == "__main__":
    # Create generator instance
    generator = AnimalClothesGenerator()
    
    # Generate dressed animal image
    result_image = generator.generate_dressed_animal(
        animal_image_path="images/animals/dog_1.png",
        clothes_image_path="images/clothes/clothes_1.png",
        clothes_description_path="images/clothes_describe/clothes_1.txt",
        show_image=True,
        save_path="animal_with_clothes_1.png"
    )