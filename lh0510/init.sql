update subject set sec_category = null,sec_category_code = null  where sec_category_code='';
update subject set thr_category = null,thr_category_code = null  where thr_category_code='';

drop table subject_rel;
create table subject_rel
	select distinct * from (
	select ind_code category_code,fir_category category,null par_category_code,null par_category 
		from  subject 
	union all
	select sec_category_code category_code,sec_category category,ind_code par_category_code,fir_category par_category 
		from  subject where sec_category is not null
	union all
	select thr_category_code category_code,thr_category category,sec_category_code par_category_code,sec_category par_category 
		from  subject where thr_category is not null)t;
create index idx_subject_rel_01 on subject_rel(category_code);
create index idx_subject_rel_02 on subject_rel(par_category_code);

select *from subject_rel a 
	where par_category_code is null
	and exists (select *from subject_rel b where par_category_code is not null
	and a.category_code = b.category_code);


drop table subject_info;
create table subject_info
	select distinct * from(
	select ind_code category_code,fir_category category,stock_code,stock_name,reason,remarks
		from subject where sec_category is null
	union ALL 
	select sec_category_code category_code,sec_category category,stock_code,stock_name,reason,remarks
		from subject where thr_category is null
	union ALL 
	select thr_category_code category_code,thr_category category,stock_code,stock_name,reason,remarks
		from subject where thr_category is not null)t
create index idx_subject_info_01 on subject_info(category_code);

UPDATE subject_info a JOIN subject_stock b ON a.remarks = b.title 
	SET a.stock_code = b.stock_code, a.stock_name = b.stock_name;

select * from subject_info;

select f.category_code,f.category,s.category_code,s.category,t.category_code,t.category
#select distinct f.category_code,f.category
	from subject_rel f
	left join subject_rel s on f.category_code = s.par_category_code
	left join subject_rel t on s.category_code = t.par_category_code
	where f.par_category_code is null
		and f.category not like '%龙虎榜%'
		and f.category not like '%盘前必读%'
		and f.category not like '%连板复盘%'
		and f.category not like '%热门题材复盘%'
order by 1,3,5;


select * from subject_rel  where par_category_code is null
and category not like '%龙虎榜%'
and category not like '%盘前必读%'
and category not like '%连板复盘%'
and category not like '%热门题材复盘%';

