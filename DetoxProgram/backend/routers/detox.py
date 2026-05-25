from fastapi import APIRouter

router = APIRouter()

@router.get("/missions/{dataset_id}")
async def get_detox_missions(dataset_id: str):
    # LLM이 생성한 디톡스 미션 리스트 및 역방향 쿼리 제안
    return {"dataset_id": dataset_id, "missions": "missions_placeholder"}
