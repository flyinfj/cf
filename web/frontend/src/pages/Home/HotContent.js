import React from 'react';
import { List, Card, Tag, Table } from 'antd';
import '../Home.css';

/**
 * 热点信息 - 内容区（左侧日期列表 + 右侧主题消息列表，均在标签页内）
 */
export const HotMain = ({
  dateList,
  selectedDate,
  onSelectDate,
  messageList,
  loading,
}) => (
  <div className="content-inner">
    <div className="content-panel">
      <div className="content-panel-title">日期</div>
      <List
        className="date-list in-content"
        dataSource={dateList}
        renderItem={(item) => (
          <List.Item
            className={`date-item ${selectedDate === item.date ? 'active' : ''}`}
            onClick={() => onSelectDate(item.date)}
          >
            {item.date}
          </List.Item>
        )}
      />
    </div>
    <div className="content-body">
      {selectedDate && (
        <div className="content-header">
          <h3>主题消息 - {selectedDate}</h3>
        </div>
      )}
      <List
        loading={loading}
        dataSource={messageList}
        renderItem={(item) => (
          <Card className="message-card" key={`${item.createTime}-${item.categoryCode}`}>
            <div className="message-header">
              <span className="message-time">
                {new Date(item.createTime).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
              </span>
              <Tag className="message-pct" color={item.pctChg >= 0 ? 'red' : 'green'}>
                {item.pctChg >= 0 ? '+' : ''}{item.pctChg?.toFixed(2)}%
              </Tag>
              <span className="subject-name">{item.categoryName}</span>
            </div>
            {item.description && (
              <div className="message-description">{item.description}</div>
            )}
            {item.stockList && item.stockList.length > 0 && (
              <div className="stock-list">
                <Table
                  dataSource={item.stockList}
                  rowKey={(record, index) => `${record.stockCode}-${index}`}
                  pagination={false}
                  size="small"
                  columns={[
                    { title: '题材', dataIndex: 'category1', key: 'category1', width: 120 },
                    { title: '分类', dataIndex: 'category2', key: 'category2', width: 120 },
                    { title: '子类', dataIndex: 'category3', key: 'category3', width: 120 },
                    { title: '代码', dataIndex: 'stockCode', key: 'stockCode', width: 100 },
                    { title: '名称', dataIndex: 'stockName', key: 'stockName', width: 150 },
                    { title: '备注', dataIndex: 'remarks', key: 'remarks', ellipsis: true },
                  ]}
                />
              </div>
            )}
          </Card>
        )}
      />
    </div>
  </div>
);

export default { HotMain };
