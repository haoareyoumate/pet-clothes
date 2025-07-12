# streamlit run src/ui.py
import streamlit as st
import os
from PIL import Image
import tempfile
from gen_image import AnimalClothesGenerator
import traceback

# Set page config
st.set_page_config(
    page_title="Pet Fashion Designer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1E88E5;
        margin-bottom: 2rem;
    }
    .clothes-option {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 10px;
        margin: 10px;
        text-align: center;
        cursor: pointer;
    }
    .clothes-option:hover {
        border-color: #1E88E5;
        box-shadow: 0 2px 8px rgba(30, 136, 229, 0.3);
    }
    .selected-clothes {
        border-color: #1E88E5 !important;
        background-color: #f3f8ff;
    }
    .stButton > button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.3rem 0.6rem;
        font-weight: bold;
        font-size: 0.85rem;
        margin-top: 0.3rem;
        height: auto;
        min-height: 2rem;
    }
    .stButton > button:hover {
        background-color: #1565C0;
    }
    /* Style for clothes grid */
    .stImage > img {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    /* Add some spacing between rows */
    .row-widget.stHorizontal {
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def load_clothes_options():
    """Load available clothes options from the images directory"""
    clothes_dir = "images/clothes"
    clothes_describe_dir = "images/clothes_describe"
    
    clothes_options = []
    
    if os.path.exists(clothes_dir) and os.path.exists(clothes_describe_dir):
        clothes_files = [f for f in os.listdir(clothes_dir) if f.endswith('.png')]
        
        for clothes_file in clothes_files:
            clothes_name = os.path.splitext(clothes_file)[0]
            description_file = f"{clothes_name}.txt"
            
            if os.path.exists(os.path.join(clothes_describe_dir, description_file)):
                clothes_options.append({
                    'name': clothes_name,
                    'image_path': os.path.join(clothes_dir, clothes_file),
                    'description_path': os.path.join(clothes_describe_dir, description_file)
                })
    
    return clothes_options

def display_clothes_selection(clothes_options):
    """Display clothes options for selection"""
    st.subheader("Choose a Cute Outfit")
    
    if not clothes_options:
        st.error("No outfit options found. Please ensure images are in 'images/clothes/' and descriptions in 'images/clothes_describe/'")
        return None
    
    # Create a grid layout with fixed number of columns
    cols_per_row = 4  # Adjust this to control how many clothes per row
    selected_clothes = None
    
    # Calculate number of rows needed
    num_rows = (len(clothes_options) + cols_per_row - 1) // cols_per_row
    
    for row in range(num_rows):
        cols = st.columns(cols_per_row)
        
        for col_idx in range(cols_per_row):
            item_idx = row * cols_per_row + col_idx
            
            # Check if we have more items to display
            if item_idx < len(clothes_options):
                clothes = clothes_options[item_idx]
                
                with cols[col_idx]:
                    try:
                        clothes_image = Image.open(clothes['image_path'])
                        
                        # Crop to 6:4 aspect ratio (width:height) if needed
                        original_width, original_height = clothes_image.size
                        target_aspect_ratio = 6 / 4  # width / height
                        current_aspect_ratio = original_width / original_height
                        
                        if current_aspect_ratio > target_aspect_ratio:
                            # Image is too wide, crop width
                            new_width = int(original_height * target_aspect_ratio)
                            left = (original_width - new_width) // 2
                            clothes_image = clothes_image.crop((left, 0, left + new_width, original_height))
                        elif current_aspect_ratio < target_aspect_ratio:
                            # Image is too tall, crop height
                            new_height = int(original_width / target_aspect_ratio)
                            top = (original_height - new_height) // 2
                            clothes_image = clothes_image.crop((0, top, original_width, top + new_height))
                        
                        # Resize image to fixed dimensions (240x160) for consistency
                        clothes_image = clothes_image.resize((240, 160), Image.Resampling.LANCZOS)

                        # Display image with fixed dimensions
                        st.image(
                            clothes_image, 
                            caption=f"Outfit {item_idx+1}", 
                            use_container_width=False,
                            width=240
                        )
                        
                        if st.button(f"Choose Outfit {item_idx+1}", key=f"select_{item_idx}"):
                            selected_clothes = clothes
                            st.session_state.selected_clothes = clothes
                            st.success(f"Selected Outfit {item_idx+1} for your pet! 🎉")
                            
                    except Exception as e:
                        st.error(f"Error loading outfit option {item_idx+1}: {str(e)}")
    
    # Return previously selected clothes if available
    if 'selected_clothes' in st.session_state:
        return st.session_state.selected_clothes
    
    return selected_clothes

def main():
    # Main header
    st.markdown("<h1 class='main-header'>Pet Fashion Designer</h1>", unsafe_allow_html=True)
    st.markdown("Give your beloved pets a stylish makeover with our fun clothing collection! 🐾✨")
    
    # Initialize session state
    if 'generated_image' not in st.session_state:
        st.session_state.generated_image = None
    if 'selected_clothes' not in st.session_state:
        st.session_state.selected_clothes = None
    
    # Sidebar for settings (API key input removed)
    with st.sidebar:
        st.header("⚙️ Settings")
        st.info("🐱🐶")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Your Pet's Photo")
        
        uploaded_file = st.file_uploader(
            "Choose a photo of your furry friend...",
            type=['png', 'jpg', 'jpeg'],
            help="Upload a clear photo of your pet that you want to dress up"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            animal_image = Image.open(uploaded_file)
            st.image(animal_image, caption="Your Pet", use_container_width=True)
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                animal_image.save(tmp_file.name)
                temp_animal_path = tmp_file.name
        else:
            temp_animal_path = None
    
    with col2:
        st.subheader("Styled Pet Result")
        
        if st.session_state.generated_image:
            st.image(st.session_state.generated_image, caption="Your Fashionable Pet", use_container_width=True)
        else:
            st.info("Upload your pet's photo and choose an outfit to see the magical transformation!")
    
    # Clothes selection
    clothes_options = load_clothes_options()
    selected_clothes = display_clothes_selection(clothes_options)
    
    # Generation section
    st.markdown("---")
    
    if temp_animal_path and selected_clothes:
        col_gen1, col_gen2, col_gen3 = st.columns([1, 2, 1])
        
        with col_gen2:
            if st.button("Style My Pet", type="primary"):
                try:
                    with st.spinner("Creating your pet's fashionable look... This may take a few moments!"):
                        # Initialize generator without API key
                        generator = AnimalClothesGenerator()
                        
                        # Generate the image
                        generated_image = generator.generate_dressed_animal(
                            animal_image_path=temp_animal_path,
                            clothes_image_path=selected_clothes['image_path'],
                            clothes_description_path=selected_clothes['description_path'],
                            show_image=False,  # Don't show in separate window
                            save_path=None
                        )
                        
                        # Store in session state
                        st.session_state.generated_image = generated_image
                        
                        st.success("Your pet looks absolutely adorable!")
                        
                        # Rerun to display the new image
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ Oops! Something went wrong: {str(e)}")
                    st.error("Please try again later.")
                    
                    # Show detailed error in expander for debugging
                    with st.expander("🔍 Show detailed error"):
                        st.code(traceback.format_exc())
    
    elif not temp_animal_path:
        st.warning("⚠️ Please upload a photo of your pet first.")
    elif not selected_clothes:
        st.warning("⚠️ Please choose an adorable outfit for your pet.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Made with ❤️ for pet lovers everywhere • Powered by Google Gemini AI"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()