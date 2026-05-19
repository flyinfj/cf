"""主题/行业查询，与 Java SubjectMessageServiceImpl 及 Mapper SQL 一致。"""
from sqlmodel import Session
from sqlalchemy import text
from app.schemas.subject_schema import (
    SubjectDateVO,
    SubjectMessageDetailVO,
    SubjectInfoVO,
    IndustryCategoryVO,
)


def get_subject_dates(session: Session) -> list[SubjectDateVO]:
    rows = session.execute(
        text(
            "SELECT DISTINCT DATE_FORMAT(create_time, '%Y-%m-%d') as date "
            "FROM subject_message ORDER BY date DESC"
        )
    ).all()
    return [SubjectDateVO(date=row[0]) for row in rows]


def _find_stocks_by_category_code(session: Session, category_code: str) -> list[SubjectInfoVO]:
    rows = session.execute(
        text("""
            SELECT
                IFNULL(IFNULL(r2.par_category, r1.par_category), i.category) AS category1,
                CASE WHEN r2.par_category IS NULL THEN i.category ELSE r1.category END AS category2,
                CASE WHEN r2.par_category IS NULL OR r1.category IS NULL THEN NULL ELSE i.category END AS category3,
                i.stock_code, i.stock_name, i.remarks
            FROM subject_info i
            LEFT JOIN subject_rel r1 ON i.category_code = r1.category_code
            LEFT JOIN subject_rel r2 ON r1.par_category_code = r2.category_code
            WHERE i.category_code = :code
        """),
        {"code": category_code},
    ).all()
    return [
        SubjectInfoVO(
            category1=row[0],
            category2=row[1],
            category3=row[2],
            stock_code=row[3],
            stock_name=row[4],
            remarks=row[5],
        )
        for row in rows
    ]


def get_message_details_by_date(session: Session, date: str) -> list[SubjectMessageDetailVO]:
    rows = session.execute(
        text("""
            SELECT create_time, category_code, category_name, pct_chg, description
            FROM subject_message
            WHERE DATE_FORMAT(create_time, '%Y-%m-%d') = :date
            ORDER BY create_time DESC
        """),
        {"date": date},
    ).all()
    result = []
    for row in rows:
        detail = SubjectMessageDetailVO(
            create_time=row[0],
            category_code=row[1],
            category_name=row[2],
            pct_chg=float(row[3]) if row[3] is not None else None,
            description=row[4],
        )
        detail.stock_list = _find_stocks_by_category_code(session, row[1] or "")
        result.append(detail)
    return result


def get_industry_categories(session: Session) -> list[IndustryCategoryVO]:
    rows = session.execute(
        text("""
            SELECT category_code, category
            FROM subject_rel
            WHERE par_category_code IS NULL AND category_type IS NULL
            ORDER BY category
        """)
    ).all()
    return [IndustryCategoryVO(category_code=row[0], category=row[1]) for row in rows]


def get_message_details_by_category(
    session: Session, category_code: str
) -> list[SubjectMessageDetailVO]:
    rows = session.execute(
        text("""
            SELECT create_time, category_code, category_name, pct_chg, description
            FROM subject_message
            WHERE category_code = :code
            ORDER BY create_time DESC
        """),
        {"code": category_code},
    ).all()
    result = []
    for row in rows:
        detail = SubjectMessageDetailVO(
            create_time=row[0],
            category_code=row[1],
            category_name=row[2],
            pct_chg=float(row[3]) if row[3] is not None else None,
            description=row[4],
        )
        detail.stock_list = _find_stocks_by_category_code(session, row[1] or "")
        result.append(detail)
    return result


def get_industry_stocks(session: Session, category_code: str) -> list[SubjectInfoVO]:
    rows = session.execute(
        text("""
            SELECT
                r1.category AS category1,
                r2.category AS category2,
                r3.category AS category3,
                i.stock_code, i.stock_name, i.remarks
            FROM subject_rel r1
            LEFT JOIN subject_rel r2 ON r2.par_category_code = r1.category_code
            LEFT JOIN subject_rel r3 ON r3.par_category_code = r1.category_code
            LEFT JOIN subject_info i ON IFNULL(IFNULL(r3.category_code, r2.category_code), r1.category_code) = i.category_code
            WHERE r1.category_code = :code AND i.stock_code IS NOT NULL
        """),
        {"code": category_code},
    ).all()
    return [
        SubjectInfoVO(
            category1=row[0],
            category2=row[1],
            category3=row[2],
            stock_code=row[3],
            stock_name=row[4],
            remarks=row[5],
        )
        for row in rows
    ]
