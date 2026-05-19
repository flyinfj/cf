"""主题/行业接口，与 Java SubjectController 一致。"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.common import success
from app.db import get_session
from app.services import subject_service

router = APIRouter(prefix="/subject", tags=["subject"])


@router.get("/dates")
def get_subject_dates(session: Session = Depends(get_session)):
    dates = subject_service.get_subject_dates(session)
    return success(data=dates)


@router.get("/messages")
def get_messages_by_date(date: str = Query(...), session: Session = Depends(get_session)):
    messages = subject_service.get_message_details_by_date(session, date)
    return success(data=messages)


@router.get("/industry/categories")
def get_industry_categories(session: Session = Depends(get_session)):
    categories = subject_service.get_industry_categories(session)
    return success(data=categories)


@router.get("/messages/category")
def get_messages_by_category(
    categoryCode: str = Query(..., alias="categoryCode"),
    session: Session = Depends(get_session),
):
    messages = subject_service.get_message_details_by_category(session, categoryCode)
    return success(data=messages)


@router.get("/industry/stocks")
def get_industry_stocks(
    categoryCode: str = Query(..., alias="categoryCode"),
    session: Session = Depends(get_session),
):
    stocks = subject_service.get_industry_stocks(session, categoryCode)
    return success(data=stocks)
