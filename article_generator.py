from dotenv import load_dotenv
import os
from openai import OpenAI
import httpx

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PROXY = os.getenv('PROXY')

proxies = {'http://': PROXY, 'https://': PROXY}
http_client = httpx.Client(proxies=proxies)
client = OpenAI(api_key=OPENAI_API_KEY, http_client = http_client)

MODEL="gpt-4o"

system_prompt = """
You are a helpful assistant that helps me with writing articles based on old articles and errors that they have but must be eradicated.
Here, the new articels must be shown as persen writen and native.
The structure and requirements are same as following:
- Aim for a 6th grader readability level
- Use simple and clear language
- Avoid complex sentences and jargon.
- Friendly and conversational.
- Engaging and slightly informal.
- Respectful, encouraging and always positive.
- Multiple short paragraphs.
- Use headings and subheadings to break up content.
- Incorporate bullet points and lists where appropriate.
- Bold important words or phrases to highlight key points.
- Start with a hook to grab attention.
- Pose questions to engage the reader's curiosity.
- Include interesting facts or anecdotes.
- Intriguing and entertaining.
- Build around creating and feeding curiosity.
- Relatable and relevant to the audience's daily life and interests.
- Helpful and Valuable: Always ensure the content is helpful to the readers. Stay away from content that does not add value or practical insights to the reader's life.
- Headline Creation: Length: Maximum of 9 words or 60 characters, Intrigue: Always create headlines that spark curiosity and encourage the reader to learn more.
- Headline: 9 words max or 60 characters.
- Article length: 150-350 words.
- Split paragraphs: content should be split into multiple paragraphs to ensure clear readability.
- Remove all non ASCII contents.
Recommend that you avoid repeating or using expressions that you frequently use to prevent detection by AI content detector.
And don't output explanation or comment, but only output new article.
"""

def generate_article(old_article, errors):
    grammar_error_dict = errors[0]
    spam_error_dict = errors[1]
    ai_detection_error_dict = errors[2]
    # grammar errors
    very_hard_to_read = 'very hard to read: { '
    for item in grammar_error_dict['red']:
        very_hard_to_read += item + ', '
    very_hard_to_read += '}'
    hard_to_read = 'hard to read: { '
    for item in grammar_error_dict['yellow']:
        hard_to_read += item + ', '
    hard_to_read += '}'
    grammar_issues = 'grammar issues: { '
    for item in grammar_error_dict['lime']:
        grammar_issues += item + ', '
    grammar_issues += '}'
    weakener = 'weakener: { '
    for item in grammar_error_dict['sky']:
        weakener += item + ', '
    weakener += '}'
    simpler_alternatives = 'simpler alternatives: { '
    for item in grammar_error_dict['violet']:
        simpler_alternatives += item + ', '
    simpler_alternatives += '}'
    # spam errors
    money = 'about money: { '
    for item in spam_error_dict['money']:
        money += item + ', '
    money += '}'
    shady = 'shady: { '
    for item in spam_error_dict['shady']:
        shady += item + ', '
    shady += '}'
    urgency = 'urgency: { '
    for item in spam_error_dict['urgency']:
        urgency += item + ', '
    urgency += '}'
    unnatural = 'unnatural: { '
    for item in spam_error_dict['unnatural']:
        unnatural += item + ', '
    unnatural += '}'
    overpromise = 'overpromise: { '
    for item in spam_error_dict['overpromise']:
        overpromise += item + ', '
    overpromise += '}'
    # ai detection
    ai_written = 'writen by ai: { '
    for item in ai_detection_error_dict['ai']:
        ai_written += item + ', '
    ai_written += '}'
    paraphrased = 'paraphrased: { '
    for item in ai_detection_error_dict['p']:
        paraphrased += item + ', '
    paraphrased += '}'
    # make user prompt
    user_prompt = f"""
This is old article.
--------------------------------
{old_article}
--------------------------------
And here are errors.
- grammar errors:
{very_hard_to_read}
{hard_to_read}
{grammar_issues}
{weakener}
{simpler_alternatives}
- spam errors:
{shady}
{money}
{urgency}
{unnatural}
{overpromise}
- ai detection errors:
{ai_written}
{paraphrased}
-------------------------------
Plz, generate the most native article based on old article and avoided these errors.
"""

    # generate the article
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content