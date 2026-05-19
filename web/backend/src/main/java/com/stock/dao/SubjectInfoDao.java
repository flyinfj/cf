package com.stock.dao;

import com.stock.entity.vo.IndustryCategoryVO;
import com.stock.entity.vo.SubjectInfoVO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface SubjectInfoDao {
    List<SubjectInfoVO> findByCategoryCode(@Param("categoryCode") String categoryCode);
    List<IndustryCategoryVO> getIndustryCategories(@Param("categoryCode") String categoryCode);
    List<SubjectInfoVO> findIndustryStocks(@Param("categoryCode") String categoryCode);
}


