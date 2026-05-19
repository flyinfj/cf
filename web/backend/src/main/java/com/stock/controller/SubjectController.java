package com.stock.controller;

import com.stock.common.Result;
import com.stock.entity.vo.IndustryCategoryVO;
import com.stock.entity.vo.SubjectDateVO;
import com.stock.entity.vo.SubjectInfoVO;
import com.stock.entity.vo.SubjectMessageDetailVO;
import com.stock.service.SubjectMessageService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/subject")
public class SubjectController {

    @Autowired
    private SubjectMessageService subjectMessageService;

    @GetMapping("/dates")
    public Result<List<SubjectDateVO>> getSubjectDates() {
        List<SubjectDateVO> dates = subjectMessageService.getSubjectDates();
        return Result.success(dates);
    }

    @GetMapping("/messages")
    public Result<List<SubjectMessageDetailVO>> getMessagesByDate(@RequestParam String date) {
        List<SubjectMessageDetailVO> messages = subjectMessageService.getMessageDetailsByDate(date);
        return Result.success(messages);
    }

    @GetMapping("/industry/categories")
    public Result<List<IndustryCategoryVO>> getIndustryCategories(@RequestParam(required = false) String categoryCode) {
        List<IndustryCategoryVO> categories = subjectMessageService.getIndustryCategories(categoryCode);
        return Result.success(categories);
    }

    @GetMapping("/messages/category")
    public Result<List<SubjectMessageDetailVO>> getMessagesByCategory(@RequestParam String categoryCode) {
        List<SubjectMessageDetailVO> messages = subjectMessageService.getMessageDetailsByCategory(categoryCode);
        return Result.success(messages);
    }

    @GetMapping("/industry/stocks")
    public Result<List<SubjectInfoVO>> getIndustryStocks(@RequestParam String categoryCode) {
        List<SubjectInfoVO> stocks = subjectMessageService.getIndustryStocks(categoryCode);
        return Result.success(stocks);
    }
}