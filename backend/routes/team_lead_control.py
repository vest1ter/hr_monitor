from fastapi import Depends
from backend.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from fastapi.routing import APIRouter
from backend.schemas.teamlead_function import HRdata_request
from backend.utils.JWT import team_lead_required
from backend.databases_function.database_function import add_hr_user


team_lead_control_router = APIRouter()





@team_lead_control_router.post("/add_hr")
async def add_hr(data: HRdata_request, role: str = Depends(team_lead_required)):
    add_hr_user(data)
    return {"message": "HR user added successfully"}