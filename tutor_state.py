from typing import List, Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class TutorState(TypedDict):
    # User Profile Information
    user_id: str
    username: str

    # Academic State Variables
    agenda: List[str]
    current_topic_index: int
    comprehension_score: int

    # Active Message Windows utilizing the mandatory add_messages reducer
    messages: Annotated[List[BaseMessage], add_messages]