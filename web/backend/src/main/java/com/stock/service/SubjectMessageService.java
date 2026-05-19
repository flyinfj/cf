package com.stock.service;

import com.stock.entity.vo.IndustryCategoryVO;
import com.stock.entity.vo.SubjectDateVO;
import com.stock.entity.vo.SubjectInfoVO;
import com.stock.entity.vo.SubjectMessageDetailVO;

import java.util.List;

public interface SubjectMessageService {
    List<SubjectDateVO> getSubjectDates();
    List<SubjectMessageDetailVO> getMessageDetailsByDate(String date);
    List<IndustryCategoryVO> getIndustryCategories(String categoryCode);
    List<SubjectMessageDetailVO> getMessageDetailsByCategory(String categoryCode);
    List<SubjectInfoVO> getIndustryStocks(String categoryCode);
}