package com.stock.dao;

import com.stock.entity.SubjectMessage;
import com.stock.entity.vo.SubjectDateVO;
import com.stock.entity.vo.SubjectMessageDetailVO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.Date;
import java.util.List;

@Mapper
public interface SubjectMessageDao {
    List<SubjectDateVO> getSubjectDates();
    List<SubjectMessage> getMessagesByDate(@Param("date") String date);
    List<SubjectMessageDetailVO> getMessageDetailsByDate(@Param("date") String date);
    List<SubjectMessageDetailVO> getMessageDetailsByCategory(@Param("categoryCode") String categoryCode);
}


