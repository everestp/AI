
import os

from bson import ObjectId
from openai import AsyncOpenAI
from dotenv import load_dotenv

from ..db.collections.files import file_collection


load_dotenv()

client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


async def process_file(id: str, file_path: str):

    file_id = ObjectId(id)

    try:

        # 1. Update status
        await file_collection.update_one(
            {"_id": file_id},
            {
                "$set": {
                    "status": "processing resume"
                }
            }
        )

        # 2. Upload PDF directly to OpenAI
        with open(file_path, "rb") as file:

            uploaded_file = await client.files.create(
                file=file,
                purpose="user_data"
            )

        # 3. Roast the resume
        await file_collection.update_one(
            {"_id": file_id},
            {
                "$set": {
                    "status": "roasting resume"
                }
            }
        )

        response = await client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_file",
                            "file_id": uploaded_file.id
                        },
                        {
                            "type": "input_text",
                            "text": """
You are a brutally honest resume reviewer.

Roast this resume, but make the feedback useful.

Analyze:

- Overall resume quality
- Weak bullet points
- Generic wording
- Missing technical details
- Weak projects
- Skills that look unsupported
- ATS problems
- Formatting issues
- Recruiter red flags
- Missing information
- Strong points

Be direct, honest, and slightly humorous.
Do not be unnecessarily insulting.

Return exactly this structure:

🔥 RESUME ROAST

Overall:
<short assessment>

🔥 Biggest Problems:
- ...
- ...
- ...

💀 Weakest Parts:
- ...
- ...
- ...

✅ What Actually Looks Good:
- ...
- ...

🛠️ How To Fix It:
- ...
- ...
- ...

🎯 Final Verdict:
<short conclusion>

Do NOT rewrite the entire resume.
"""
                        }
                    ]
                }
            ]
        )

        roast = response.output_text

        # 4. Store roast in MongoDB
        await file_collection.update_one(
            {"_id": file_id},
            {
                "$set": {
                    "status": "completed",
                    "roast": roast
                }
            }
        )

        print("File processed successfully:", id)
        print("File processed successfully:", roast)

        return roast

    except Exception as e:

        await file_collection.update_one(
            {"_id": file_id},
            {
                "$set": {
                    "status": "failed",
                    "error": str(e)
                }
            }
        )

        print(f"Error processing file {id}: {e}")
