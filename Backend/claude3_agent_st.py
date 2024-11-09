import streamlit as st
import boto3
import os
from PIL import Image
import claude3_tools as tools

# Get the AWS region from an environment variable
aws_region = os.environ.get('AWS_REGION', 'us-east-1')  # Default to 'us-east-1' if not set

# Create the Cognito client with the specified region
cognito_client = boto3.client('cognito-idp', region_name=aws_region)

COGNITO_CLIENT_ID = os.environ.get('COGNITO_CLIENT_ID')

# Page configuration
st.set_page_config(
    page_title="Smile IT Solutions",
    page_icon="https://smileitsolutions.uk/hubfs/apple-touch-icon-precomposed-1.png",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .h1 { color: #0000; }
    .stApp { background-color: #000; }
    .stButton>button {
        color: #DF651A;
        background-color: #0000;
        border-color: #DF651A;
    }
     .stTextInput>div>div>input {
        background-color: rgb(7,55,99);
        color: white;
    }
    .stTextInput>label {
        color: #DF651A;
    }
    .stButton>button:hover {
        background-color: #DF651A;
        border-color: #DF651A;
        color: #fff;
    }
    .content-container {
        max-width: 800px;
        margin: auto;
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Authentication function
def sign_in(username, password):
    try:
        response = cognito_client.initiate_auth(
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        return response
    except cognito_client.exceptions.NotAuthorizedException:
        st.error("Incorrect username or password.")
        return None
    except Exception as e:
        st.error(f"An error occurred during sign in. Please try again.")
        return None

# Main application function
def app():
    # Authentication
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    st.markdown('<div class="content-container">', unsafe_allow_html=True)

    if not st.session_state.authenticated:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.image("FullSmileLogoWhite.png", use_column_width=True)
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Sign In"):
                auth_result = sign_in(username, password)
                if auth_result:
                    st.session_state.authenticated = True
                    st.success("Successfully signed in!")
                    st.rerun()
    else:
        st.markdown("<h3 style='color: #DF651A;padding: 35px;'>Organisation AI Agent</h3>", unsafe_allow_html=True)
        # Logo and title
        col1, col2 = st.columns([1, 2])
        with col1:
            logo2 = Image.open("SmileAgent.png")
            resized_logo = logo2.resize((200, 200))  # (width, height)
            st.image(resized_logo)
           
        with col2:
            logo = Image.open("FullSmileLogoWhite.png")
            resized_logo = logo.resize((350, 120))  # (width, height)
            st.image(resized_logo)
            

        # Tool selection
        current_tool = st.selectbox(
            "Choose Tool:",
            ["AWS Well Architected Tool", "Diagram Tool", "Code Gen Tool"],
        )

        query = st.text_input("Query:")

        if st.button("Submit Query"):
            with st.spinner("Generating..."):
                if current_tool == "AWS Well Architected Tool":
                    answer = tools.aws_well_arch_tool(query)
                    st.markdown(answer["ans"])
                    docs = answer["docs"].split("\n")
                    with st.expander("Resources"):
                        for doc in docs:
                            st.write(doc)
                elif current_tool == "Diagram Tool":
                    answer = tools.diagram_tool(query)
                    base64_string = tools.pil_to_base64(answer)
                    caption = tools.gen_image_caption(base64_string)
                    st.image(answer)
                    with st.expander("Explanation"):
                        st.markdown(caption)
                elif current_tool == "Code Gen Tool":
                    answer = tools.code_gen_tool(query)
                    st.code(answer)

        if st.button("Sign Out"):
            st.session_state.authenticated = False
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def main():
    app()

if __name__ == "__main__":
    main()