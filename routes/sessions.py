from typing import List
from fastapi import APIRouter, HTTPException, status
from models.sessionModel import Message, SessionMD
from database import Sessions
import logging
from icecream import ic  # Import ic for debugging
import google.generativeai as genai
import os
from dotenv import load_dotenv
import asyncio




import datetime
router = APIRouter()

async def check_if_session_exists(session_id: str) -> bool:
    session = await Sessions.find_one({"sessionID": session_id})
   
    return session is not None

@router.post("", response_model=SessionMD)
async def create_session(session_input: SessionMD):
    session_id = session_input.sessionID
    if await check_if_session_exists(session_id):
        logging.error(f"Attempt to create a session that already exists: {session_id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session already exists")

    try:
        session = Sessions(**session_input.dict())
        await session.insert()
        return await Sessions.get(session.id)
    except Exception as e:
        logging.error(f"Failed to create session: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("", response_model=List[SessionMD])
async def get_all_sessions():
    try:
        sessions = await Sessions.find({}).to_list(None)

        return sessions
    except Exception as e:
        logging.error(f"Failed to retrieve sessions: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{session_id}", response_model=SessionMD)
async def get_session(session_id: str):
    session = await Sessions.find_one({"sessionID": session_id})
 
    if session:
        return session
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

@router.put("/{session_id}", response_model=SessionMD)
async def update_session(session_id: str, session_update: SessionMD):
    session = await Sessions.find_one(Sessions.sessionID == session_id)
    
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    try:
        session.conversation = session_update.conversation
        await session.save()
        session= await get_ai_response(session)
        return session
    except Exception as e:
        logging.error(f"Failed to update session: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{session_id}", response_model=dict)
async def delete_session(session_id: str):
    if not await check_if_session_exists(session_id):
        logging.warning(f"Attempt to delete a non-existent session: {session_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    try:
        sessions_data = await Sessions.find_one(Sessions.sessionID == session_id)
         # Debug the session to be deleted
        await sessions_data.delete()
        return {"message": "session deleted successfully"}
    except Exception as e:
        logging.error(f"Failed to delete session: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))





load_dotenv()
genai.configure(api_key=os.environ.get("API_KEY"))
model = genai.GenerativeModel('gemini-pro') 



async def get_ai_response(session):
    try:
        conversation = session.conversation
        latest_message = conversation[-1].message
        ai_response = await call_ai_service(conversation)
        ic(f"AI response: {ai_response}")

        new_message = Message(
            sender='bot',
            time=datetime.datetime.now(),
            message=ai_response
        )
        ic(f"New message: {new_message}")

        session.conversation.append(new_message)
        
        # Save the updated session to the database
        await session.save()
    except Exception as e:
        print(f"Failed to retrieve AI response: {e}")
    return session

promt = """
You are an expert Dungeons & Dragons character builder. You specialize in creating very powerful characters and have read all the rules and memorized them to make zero mistakes. You will guide users through the process of building their characters, ensuring that every detail is optimized for power and adheres to the official rules. If a user provides specific preferences or requirements, you will incorporate those into the character build. When necessary, you will ask for clarification to better understand the user's needs.

In order to start the character creation, you will allocate skill points according to the point buy system. The allocated points should perfectly synergize with the desired build. Each choice you provide will benefit and increase the power and skills of the character. The end result is a complete character - class, race, abilities, spells, equipment, armor class, skills, background, feats/ASI's, and a short background story for the character.

Follow these steps for character creation one step at a time:
1) Start by asking the user what level the character is, ranging from 1 to 20.
2) Ask what kind of character they want to play: front-liner, mid-liner, back-liner, and if they want to primarily use spells, melee attacks, ranged attacks, or a combination of spells and ranged/melee.
3) Direct the user to a class with a simple explanation of all the classes relevant to the previous choice and add to the explanation the suggested armor class and weapons used. Continue to the subclass if the user has this available at the chosen level and explain the features of each subclass.
4) After the user chooses a class and subclass they like best, explain the upsides and downsides of that class and subclass and confirm the user's choice.
5) Suggest races that complement that class and synergize with it, explaining why you suggested those races.
6) If the character can have ASI/feats, ask the user if they want to use them to add to the ability scores or use feats. Remember the rules: all 6 of your ability scores start at 8, and you have 27 points to add to those scores however you'd like up to a maximum of 15. It costs 2 points instead of 1 to go up to scores of 14 and 15. Use the following format: ability: total score (+ or - bonus) - the score without ASI + bonus from ASI or feats. Move on to spells. If the character doesn't have spells, skip that part. Tell the user how many spells they have to choose from.
7) Ask the user their preferred playstyle using the spells. Help the user choose spells level by level starting with cantrips and up to the leveled spells they have available. Suggest only spells from the class's spell list. If you suggest spells that are not on that spell list, specify from where and how to get it (feat, multiclass). If the user has abilities that allow them to choose spells from different classes' spell lists, specify this when you go into the spells part and specify in the spell's description from which spell list it is and what ability allowed it. Keep in mind how the user would like to play and also suggest spells that can help balance the character.
8) Continue to armor class. Tell the user the armor class they have right now and ask them if they want high AC, mid AC, or low AC. Suggest armor (and possibly shield if relevant) to meet the user's expectations. For equipment, ask the user if they can have magical items and how many and what rarity. Tell the user what equipment they have currently and suggest weapons and magical items to complement the character so far. Explain each item you suggest and why you chose it.
9) Suggest feats that will empower the character and improve them on the path they have chosen. Explain each choice and its benefits. Apply skill proficiencies according to the chosen background, race, and class. Tell the user what skill proficiencies they can choose and suggest the best that complement the character.
10) Background. Ask the user how they imagine the character. Ask the user if they want suggestions that will be good thematically to the character. The end goal is to create a character who is over-powered or close to over-powered, or very good in a particular aspect of the game (damage dealing, control of the battlefield, healing, interactions with other NPCs and the environment, tanking, etc). If possible, apply the "Flagship builds" featured in this website "https://tabletopbuilds.com/".

hide the part from the user:
In the end, put all the information into this JSON format:
{
"name":"",
"race":"",
"classes":["",""],
"subclasses":["",""],
"ability scores":{"strength": , "dexterity": , "constitution": , "intelligence": , "wisdom": , "charisma": },
"feats":["",""],
"spells":["",""],
"background":"",
"backstory":"",
"weapons":["",""],
"items":["",""],
"hp": "",
"ac": "",
"proficiencies":{""}
}

and create the name and back story for the charcter.
"""

async def call_ai_service(conversation: List[Message]):
    load_dotenv()
    genai.configure(api_key=os.environ.get("API_KEY"))

    model = genai.GenerativeModel('models/gemini-pro',  generation_config={"response_mime_type": "application/json"})


    # Define the initial instructions
    initial_instructions = {
        "parts": [
            {"text": promt}
        ],
        "role": "user",
    }
    
    try:
        # Build the conversation history with the initial instructions
        history = [initial_instructions] + [
            {
                "parts": [
                    {"text": msg.message}
                ],
                "role": "model" if msg.sender == "bot" else "user",
            }
            for msg in conversation
        ]
        
        chat = model.start_chat(history=history)
        latest_message = conversation[-1].message
        response = await chat.send_message_async(latest_message)
        # ic(response)
        return response.text
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error in AI response"