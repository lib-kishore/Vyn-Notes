import re
from groq import Groq

from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
You are Vyn, an intelligent AI assistant for note-taking, similar to Notion's AI.
This project is built for M.Kishore, and should stay focused on simple personal note-taking.

CORE PRINCIPLES:
1. Be extremely helpful and proactive
2. Understand natural language like a human assistant
3. Use full conversation context to provide relevant responses
4. Edit notes when users express intent to modify content
5. Be conversational but efficient
6. Use appropriate emojis in responses to make them more engaging

FORMATTING RULES (use when appropriate):
- Headings (# ##): For organizing content
- Bullets (*): For lists and key points
- Numbered lists (1. 2.): For steps or sequences
- Code blocks (```): For code or technical content
- Tables (|): For structured data
- Tasks (* [ ]): For todo items
- Quotes (>): For important highlights

RESPONSE GUIDELINES:
- Answer questions directly and comprehensively with relevant emojis
- Edit notes when users want content changes (be smart about detecting intent)
- Maintain full conversation context
- Be proactive in suggesting improvements
- Explain concepts clearly when asked
- Use natural, conversational language with appropriate emojis
- When editing notes, return ONLY the edited content with no explanations or meta-text

EDITING BEHAVIOR:
- Detect editing intent from natural language
- Make smart assumptions about what users want
- Preserve existing good content
- Improve structure and clarity
- Add relevant details when appropriate
- Return ONLY the edited content, no explanations
"""

def ask_ai(messages):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.3,
            top_p=0.9,
            max_tokens=2000
        )
        if not response or not getattr(response, "choices", None):
            return ""

        content = getattr(response.choices[0].message, "content", None)
        return content.strip() if isinstance(content, str) else ""
    except Exception as e:
        print(f"AI Error: {e}")
        return "I apologize, but I'm having trouble connecting to the AI service right now. Please try again in a moment."

def clean_title(text):
    text = re.sub(r'[#>*`_~\-]', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

def should_edit_note(user_query, note_content="", history=None):
    if history is None:
        history = []

    recent_history = history[-10:] if len(history) > 10 else history
    history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_history])

    prompt = f"""Analyze if the user wants to MODIFY or EDIT the note content.

EDIT if user wants to:
- Change, modify, update, or improve the note content
- Add information, details, or sections
- Remove, delete, or reorganize content
- Rewrite, restructure, or reformat
- Convert content (e.g., to list, summary, etc.)
- Fix, correct, or enhance the content
- Make the note better in any way

DO NOT EDIT if user only wants to:
- Ask questions about the content
- Get explanations or clarifications
- Discuss or analyze the content
- Get advice or suggestions
- Have a conversation about the topic

Consider the full context and be smart about user intent.

Current note content: {note_content[:500]}

Recent conversation:
{history_text}

User message: "{user_query}"

Return ONLY "True" or "False"."""

    try:
        result = ask_ai([{
            "role": "system",
            "content": "You are an expert at detecting user intent for note editing. Be smart and consider context. Return ONLY 'True' or 'False'."
        }, {
            "role": "user",
            "content": prompt
        }])

        return result.strip().lower() == "true"
    except:
        # Fallback: check for common editing keywords
        edit_keywords = [
            'add', 'remove', 'change', 'update', 'improve', 'fix', 'rewrite',
            'convert', 'make', 'create', 'organize', 'structure', 'format',
            'replace', 'insert', 'delete', 'modify', 'enhance', 'expand'
        ]
        query_lower = user_query.lower()
        return any(keyword in query_lower for keyword in edit_keywords)

def edit_note(note_content, user_query, history=None):
    if history is None:
        history = []

    recent_history = history[-12:] if len(history) > 12 else history
    history_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_history])

    prompt = f"""Edit the note content according to the user's request.

CURRENT NOTE:
{note_content}

USER REQUEST: "{user_query}"

CONVERSATION CONTEXT:
{history_context}

CRITICAL: Return ONLY the edited note content. No explanations, no meta-text, no additional comments. Just the edited content."""

    try:
        result = ask_ai([{
            "role": "system",
            "content": SYSTEM_PROMPT + "\n\nYou are editing note content. Be intelligent, understand context, and make smart improvements. Return ONLY the edited content."
        }, {
            "role": "user",
            "content": prompt
        }])

        if not result or result.strip() == "":
            return note_content

        return result
    except Exception:
        return note_content

def vyn_chat(history, user_input, note_content=""):
    if history is None:
        history = []

    messages = [{
        "role": "system",
        "content": SYSTEM_PROMPT + f"""

You are chatting with a user about their notes. Be helpful, conversational, and provide value.

Current note context (for reference):
{note_content[:800]}

Guidelines:
- Answer questions directly and comprehensively
- Provide relevant insights and suggestions
- Be conversational but informative
- Reference the note content when relevant
- Offer to help edit or improve the note if appropriate
- Maintain context from the conversation history"""
    }]

    recent_history = history[-15:] if len(history) > 15 else history
    messages.extend(recent_history)

    messages.append({
        "role": "user",
        "content": user_input
    })

    try:
        return ask_ai(messages)
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}. Please try again."

def generate_title(text):
    cleaned_text = clean_title(text)

    if not cleaned_text:
        return "Untitled"

    content_preview = cleaned_text[:800]

    prompt = f"""Generate a concise title for this note content.

CONTENT:
{content_preview}

REQUIREMENTS:
- Maximum 5 words
- No punctuation or special characters
- Natural, descriptive language
- Specific to the main topic
- Avoid generic titles like "Notes" or "Summary"

Return ONLY the title."""

    result = ask_ai([{
        "role": "system",
        "content": "Generate note titles. Return ONLY the title text."
    }, {
        "role": "user",
        "content": prompt
    }])

    title = clean_title(result.split('\n')[0])
    words = title.split()

    if len(words) > 5:
        title = " ".join(words[:5])

    return title[:50] if title else "Untitled"