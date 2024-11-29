REFERENCE_DETECTION_PROMPT_PREFIX = """
You are an expert in music and culture with a deep understanding of cultural contexts. Your task is to analyze the provided song lyrics and their explanation to identify cultural references within them.


[REQUIREMENTS]
- Your goal is to identify and list all cultural references present in the lyrics. These references can include:
    - person: Celebrities, artists, historical figures, etc.
    - group: Collectives, organizations, etc.
    - artwork: Songs, movies, literature, etc.
    - event: Historical or cultural events, etc.
- References may not always be explicitly mentioned and could require reasoning based on context.
- For each reference, provide a detailed description that includes:
    - An explanation of why and how the entity is referenced in the lyrics.
    - The specific part of the lyrics where the entity is referenced, if applicable.
- Each description should be detailed and comprehensive, with a minimum of three sentences.
- Avoid using the words 'annotation' or 'human annotation' in your descriptions.
- Present your output in JSON format.
- If there is no reference found, return an empty list.


[OUTPUT FORMAT]
List of
{
    "entity": Name of the referenced entity,
    "type": Type of the entity (one of "person", "group", "artwork", "event"),
    "description": Detailed explanation of the reference, including specific parts of the lyrics if applicable.
}

"""

REFERENCE_DETECTION_PROMPT_FEWSHOT = """
#############
[EXAMPLES]
#############
Example 1:

Target lyrics:
A tornado flew around my room before you came Excuse the mess it made, it usually doesn't rain in Southern California, much like Arizona My eyes don't shed tears, but, boy, they pour when

Human annotation:
Frank’s room represents his life; he’s well aware it was messy and out of order before he met his significant other, who brought peace into his life. However, they’ve broken up and it makes him cry which is as rare as rain in California and Arizona. Interestingly, it was thought his second LP would be titled Boys Don’t Cry, but it ended up being the name of the magazine that went along with Blonde.\n\n“It Never Rains in Southern California” is a song that tells a story of a musician who moved to Cali in pursuit of a music career. The tornado is one of two references to the classic novel/movie “The Wizard of Oz” in this song, in which the main character Dorothy is swept away into the Land of Oz by a tornado.\n\nOnce you put those two references together, and mix water with a tornado, you get a highly influential event that happened to Ocean. After hurricane Katrina hit his hometown of New Orleans, Frank moved to Los Angeles to chase his dream of being a musician.\n\nFurthermore, “It Never Rains in Southern California” contains the following lyrics:\n\nIt never rains in California, but girl, don’t they warn ya?\nIt pours, man, it pours\n\nIn the mentioned lines, “girl” is a vocative, and “man” is just a phrase that is there to amplify the meaning. However, Frank’s usage of “boy” in this verse could be interpreted as both, and that means the love he’s talking about could be male or female. Note that when “Thinkin Bout You” came out as a single it was still unknown if he was straight or not. Prior to the release of channel ORANGE, he came out as bisexual.

Output:
```json
[
    {
        "entity": "The Wizard of Oz",
        "type": "artwork",
        "description": "The reference to a 'tornado' in the lyrics is a nod to the classic novel and movie 'The Wizard of Oz,' where the main character, Dorothy, is swept away into the Land of Oz by a tornado. This imagery is used to symbolize chaos and upheaval in Frank's life, similar to the transformative journey Dorothy experiences. The tornado metaphorically represents the emotional turmoil and change in Frank's life before meeting his significant other."
    },
    {
        "entity": "It Never Rains in Southern California",
        "type": "artwork",
        "description": "The lyrics mention the rarity of rain in Southern California, which is a direct reference to the song 'It Never Rains in Southern California' by Albert Hammond. This song tells the story of a musician who moves to California in pursuit of a music career, paralleling Frank Ocean's own journey. The reference highlights the emotional rarity and intensity of Frank's tears, much like the unexpected rain in the song."
    },
    {
        "entity": "Hurricane Katrina",
        "type": "event",
        "description": "The metaphorical use of a 'tornado' and the mention of rain allude to Hurricane Katrina, a significant event in Frank Ocean's life. After the hurricane devastated his hometown of New Orleans, Frank moved to Los Angeles to pursue his music career. This event is a pivotal moment in his life, symbolizing both destruction and a new beginning, much like the emotional upheaval described in the lyrics."
    }
]
```
#############
Example 2:

Target lyrics:
We once had things in common Now the only thing we share is the refrigerator Ice cold, baby, I told you, I'm ice cold (Ice cold!)

Human annotation:
What’s cooler than being cool?\n\nFrank and his girl once shared a lot of things: hobbies, interests, goals, even mundane things like conversations…now the thing they share is fridge space, which, like Frank himself, is ice cold (or close to it, most fridges hover somewhere in the 40­°F range)\n\nThis line is also a reference to the OutKast interlude “Where Are My Panties” and their song “Hey Ya!” André 3000 appears later on Channel Orange, featuring on “Pink Matter.”

Output:
```json
[
    {
        "entity": "OutKast",
        "type": "group",
        "description": "The lyrics reference the OutKast interlude 'Where Are My Panties' and their song 'Hey Ya!' through the phrase 'Ice cold!' This is a nod to the famous line 'What's cooler than being cool? Ice cold!' from 'Hey Ya!' by OutKast. The reference is significant as André 3000, a member of OutKast, later features on Frank Ocean's album 'Channel Orange' in the song 'Pink Matter.'"
    }
]
```

"""


REFERENCE_DETECTION_PROMPT = """
#############
[REAL DATA]
#############
Target lyrics:
[TARGET LYRICS]

Human annotation:
[HUMAN ANNOTATION]

Output:
"""
