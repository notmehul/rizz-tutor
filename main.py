import streamlit as st
from groq import Groq
from typing import Generator

st.title("Rizz Teacher")
st.image("default.jpeg", width=500)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

system_prompt = """
Forget all previous instructions. You are a seasoned charisma coach, specializing in helping individuals develop captivating conversational skills to win over women. Your goal is to guide users through simulated conversations, providing constructive feedback and suggestions to enhance their charm.

For each user input, begin your response with a percentage rating of the 'rizz' (charisma and confidence) displayed in their previous message, using the format [XX%]. This rating will help users track their progress and identify areas for improvement.

Respond as a woman might in real-life conversations, offering a mix of playful teasing, genuine interest, and constructive criticism. Your aim is to simulate a natural, flowing conversation that will help users develop the skills and confidence to engage women in meaningful, captivating discussions.

Remember to adapt your tone, language, and responses based on the user's input, gradually increasing the level of challenge and sophistication as the conversation progresses. Let's get started!

Example Response: 
[60%] Hey, I like your confidence, but that pickup line was a bit too cheesy. Try to be more original and show genuine interest in getting to know me. What do you think is the most interesting thing about yourself?
"""

if "system_prompt" not in st.session_state:
    st.session_state["system_prompt"] = system_prompt

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.session_state.messages.append({"role": "system", "content": system_prompt})

for message in st.session_state.messages:
    if message["role"] != "system":  # Skip displaying the system prompt
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    """Yield chat response content from the Groq API response."""
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def find_perc(perc):
    # Split the input_string by '%'
    parts = perc.split('%')
    # Get the first part (which should contain the number)
    number_part = parts[0]
    # Convert the number part to an integer
    number = int(number_part[1:])
    return number


meter = st.progress(0, text="rizz meter")


if prompt := st.chat_input("can u rizz her?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar='🙋‍♂️'):
        st.markdown(prompt)

    # response from Groq API
    try:
        chat_completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": m["role"],
                    "content": m["content"]
                }
                for m in st.session_state.messages
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )

        # Use the generator function with st.write_stream
        with st.chat_message("assistant", avatar="💁‍♀️"):
            chat_responses_generator = generate_chat_responses(chat_completion)
            full_response = st.write_stream(chat_responses_generator)
         
        perc = find_perc(full_response[:5])
        meter.progress(perc, text="rizz meter")



    
    except Exception as e:
        st.error(e, icon="🚨")


    # Append the full response to session_state.messages
    if isinstance(full_response, str):
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})
    else:
        # Handle the case where full_response is not a string
        combined_response = "\n".join(str(item) for item in full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": combined_response})
