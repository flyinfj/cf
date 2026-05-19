package com.stock.service.impl;

import com.stock.dao.SubjectInfoDao;
import com.stock.dao.SubjectMessageDao;
import com.stock.entity.vo.IndustryCategoryVO;
import com.stock.entity.vo.SubjectDateVO;
import com.stock.entity.vo.SubjectInfoVO;
import com.stock.entity.vo.SubjectMessageDetailVO;
import com.stock.service.SubjectMessageService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class SubjectMessageServiceImpl implements SubjectMessageService {

    @Autowired
    private SubjectMessageDao subjectMessageDao;

    @Autowired
    private SubjectInfoDao subjectInfoDao;

    @Override
    public List<SubjectDateVO> getSubjectDates() {
        return subjectMessageDao.getSubjectDates();
    }

    @Override
    public List<SubjectMessageDetailVO> getMessageDetailsByDate(String date) {
        List<SubjectMessageDetailVO> messages = subjectMessageDao.getMessageDetailsByDate(date);
        // 为每条消息查询关联的列表
        for (SubjectMessageDetailVO message : messages) {
            List<SubjectInfoVO> stockList = subjectInfoDao.findByCategoryCode(message.getCategoryCode());
            message.setStockList(stockList);
        }
        return messages;
    }

    @Override
    public List<IndustryCategoryVO> getIndustryCategories(String categoryCode) {
        return subjectInfoDao.getIndustryCategories(categoryCode);
    }

    @Override
    public List<SubjectMessageDetailVO> getMessageDetailsByCategory(String categoryCode) {
        List<SubjectMessageDetailVO> messages = subjectMessageDao.getMessageDetailsByCategory(categoryCode);
        // 为每条消息查询关联的列表
        for (SubjectMessageDetailVO message : messages) {
            List<SubjectInfoVO> stockList = subjectInfoDao.findByCategoryCode(message.getCategoryCode());
            message.setStockList(stockList);
        }
        return messages;
    }

    @Override
    public List<SubjectInfoVO> getIndustryStocks(String categoryCode) {
        return subjectInfoDao.findIndustryStocks(categoryCode);
    }
}


