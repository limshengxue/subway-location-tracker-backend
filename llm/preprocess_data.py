from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

class ProcessedOutletOperatingHours(BaseModel):
    outlet_id: str = Field(..., description="Outlet ID")
    mon_open: str | None = Field(None, description="Monday opening time (HH:MM format)")
    mon_close: str | None = Field(None, description="Monday closing time (HH:MM format)")
    tue_open: str | None = Field(None, description="Tuesday opening time (HH:MM format)")
    tue_close: str | None = Field(None, description="Tuesday closing time (HH:MM format)")
    wed_open: str | None = Field(None, description="Wednesday opening time (HH:MM format)")
    wed_close: str | None = Field(None, description="Wednesday closing time (HH:MM format)")
    thu_open: str | None = Field(None, description="Thursday opening time (HH:MM format)")
    thu_close: str | None = Field(None, description="Thursday closing time (HH:MM format)")
    fri_open: str | None = Field(None, description="Friday opening time (HH:MM format)")
    fri_close: str | None = Field(None, description="Friday closing time (HH:MM format)")
    sat_open: str | None = Field(None, description="Saturday opening time (HH:MM format)")
    sat_close: str | None = Field(None, description="Saturday closing time (HH:MM format)")
    sun_open: str | None = Field(None, description="Sunday opening time (HH:MM format)")
    sun_close: str | None = Field(None, description="Sunday closing time (HH:MM format)")
    public_holiday_open: str | None = Field(None, description="Public holiday opening time (HH:MM format)")
    public_holiday_close: str | None = Field(None, description="Public holiday closing time (HH:MM format)")

class OutletOperatingHoursDescription(BaseModel):
    outlet_id: str
    operating_hours: str | None = Field(None, nullable=True)

class ProcessedOutput(BaseModel):
    processed_outlets_operating_hour: list[ProcessedOutletOperatingHours]

def preprocess_data(outlets_operating_hours: list[OutletOperatingHoursDescription]) -> list[ProcessedOutletOperatingHours]:
    llm = ChatOpenAI(temperature=0, model="gpt-4o")
    structured_llm_operating_hours_processor = llm.with_structured_output(ProcessedOutput)  # Use ProcessedOutput

    # Define Prompt
    prompt = """
    You are given a list of outlets with their operating hours description. 
    Please extract the opening and closing time of each outlet for each day of the week.
    Return the times in HH:MM format.
    <outlets_with_operating_hours_description>
    {outlets_with_operating_hours_description}
    </outlets_with_operating_hours_description>
    """
    structured_llm_operating_hours_prompt = ChatPromptTemplate.from_messages(
        [("system", prompt)]
    )

    # Define Context Preparer
    processor = structured_llm_operating_hours_prompt | structured_llm_operating_hours_processor

    response = processor.invoke({"outlets_with_operating_hours_description": outlets_operating_hours})

    return response.processed_outlets_operating_hour
