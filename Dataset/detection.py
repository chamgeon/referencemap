"""
detect references from the genius data using gpt api.
"""


from prompts import REFERENCE_DETECTION_PROMPT_PREFIX, REFERENCE_DETECTION_PROMPT_FEWSHOT, REFERENCE_DETECTION_PROMPT
from schema import Annotation, Song, Gpt_response
import json
import re
from typing import Tuple, List, Dict
from pydantic import ValidationError
from openai import OpenAI, AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import asyncio


class ReferenceDetector:

    def __init__(self):
        
        self.songs = []
        self.client = OpenAI()
        self.async_client = AsyncOpenAI()
    


    def _validate_song_data(self, song_data: List[Dict]):

        """
        Validate song data. The input should be a list of dicts with the following keys:
        {
            "name": str,
            "content": List[Dict],
            "lyrics source": str
        }

        and each item in "content" should follow the schema:
        {
            "lyrics": str,
            "annotation": str,
            "source": str
        }
        """

        for song in song_data:
            self.songs.append(Song(**song))
    

    def _construct_detection_prompt(self, annotation: Annotation) -> Tuple[str, str, str]:

        """
        Construct detection prompt for a given annotation data.
        """

        detection_prompt = REFERENCE_DETECTION_PROMPT.replace("[TARGET LYRICS]", annotation.lyrics).replace("[HUMAN ANNOTATION]", annotation.annotation)

        return REFERENCE_DETECTION_PROMPT_PREFIX + REFERENCE_DETECTION_PROMPT_FEWSHOT + detection_prompt, annotation.source
    


    def _validate_and_process_gpt_response(self, gpt_response_content: str) -> List[Dict]:

        """
        Validate the gpt response, and process the response into a list of Gpt_response objects.
        """

        json_part = re.search('```json\n([\s\S]*)\n```', gpt_response_content, re.IGNORECASE)

        if not json_part:
            raise ValueError("No JSON part found in the GPT response")
        
        output = []

        for content in json.loads(json_part.group(1)):
            try:
                output.append(Gpt_response.model_validate(content).model_dump())
            except ValidationError:
                print(f"Response validation failed: unexpected type for Gpt_response")
        return output
    


    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _call_gpt(self, prompt: str) -> List[Dict]:

        """
        Synchronous GPT call with retry logic
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        return self._validate_and_process_gpt_response(response.choices[0].message.content)
    

    def get_gpt_responses(self, songs_data: List[Dict]) -> Dict:

        """
        Get gpt responses for a list of songs.
        Output schema:
        {
            song name: {
                gpt_responses: List[Dict(serialized Gpt_response)],
                source: str
            },
            ...
        }
        """

        output = {}
        self._validate_song_data(songs_data)

        for song in self.songs:
            print(f"processing {song.name}")
            output[song.name] = {"gpt_responses": [], "source": song.lyrics_source}
            for annotation in song.content:
                prompt, _ = self._construct_detection_prompt(annotation)
                gpt_responses = self._call_gpt(prompt)
                output[song.name]["gpt_responses"].extend(gpt_responses)

        return output



    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _acall_gpt(self, prompt: str) -> List[Dict]:

        """
        Asynchronous GPT call with retry logic
        """

        response = await self.async_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        return self._validate_and_process_gpt_response(response.choices[0].message.content)
    

    async def aget_gpt_responses(self, songs_data: List[Dict]) -> Dict:

        """
        Get gpt responses for a list of songs.
        Output schema:
        {
            song name: {
                gpt_responses: List[Dict(serialized Gpt_response)],
                source: str
            },
            ...
        }
        """

        self._validate_song_data(songs_data)
        output = {}
        tasks = []

        for song in self.songs:
            output[song.name] = {"gpt_responses": [], "source": song.lyrics_source}
            for annotation in song.content:
                prompt, _ = self._construct_detection_prompt(annotation)
                tasks.append((song.name, self._acall_gpt(prompt)))
        
        
        song_names, coroutines = zip(*tasks)
        gpt_responses = await asyncio.gather(*coroutines)

        for song_name, gpt_response in zip(song_names, gpt_responses):
            output[song_name]["gpt_responses"].extend(gpt_response)

        return output






def main():
    dataset_path = "data/genius/Frank Ocean/channel ORANGE.json"
    output_path = "data/gpt/Frank Ocean/channel ORANGE_2.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    detector = ReferenceDetector()
    
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    responses = asyncio.run(detector.aget_gpt_responses(data))
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(responses, f, indent=4, ensure_ascii=False)
    



if __name__ == "__main__":
    main()
