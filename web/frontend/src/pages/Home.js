import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout, Menu, Button, message, Tabs } from 'antd';
import {
  FireOutlined,
  BankOutlined,
  LogoutOutlined,
  LineChartOutlined,
  StarOutlined,
  UnorderedListOutlined,
  SettingOutlined,
  CustomerServiceOutlined,
} from '@ant-design/icons';
import request from '../utils/request';
import { HotMain } from './Home/HotContent';
import { IndustryMain } from './Home/IndustryContent';
import './Home.css';

const { Header, Content } = Layout;

/**
 * 一级菜单（目录）与二级菜单配置
 * 一级为目录名，二级为具体菜单名；同一二级菜单在工作区只允许打开一个标签页
 */
const MENU_CONFIG = [
  {
    key: 'quote',
    label: '行情报价',
    children: [
      { key: 'marketTrend', label: '市场走势', icon: <LineChartOutlined /> },
      { key: 'optionalStock', label: '自选股', icon: <StarOutlined /> },
      { key: 'allAStock', label: '全部A股', icon: <UnorderedListOutlined /> },
    ],
  },
  {
    key: 'subject',
    label: '题材库',
    children: [
      { key: 'hot', label: '热点信息', icon: <FireOutlined /> },
      { key: 'industry', label: '全部题材', icon: <BankOutlined /> },
    ],
  },
  {
    key: 'system',
    label: '系统设置',
    children: [{ key: 'settings', label: '系统设置', icon: <SettingOutlined /> }],
  },
  {
    key: 'complaint',
    label: '投诉与调解',
    children: [{ key: 'mediation', label: '投诉与调解', icon: <CustomerServiceOutlined /> }],
  },
];

const Home = () => {
  const navigate = useNavigate();
  const [selectedFirstLevel, setSelectedFirstLevel] = useState(MENU_CONFIG[0].key);
  const [openTabs, setOpenTabs] = useState([]);
  const [activeTabKey, setActiveTabKey] = useState(null);
  const [dateList, setDateList] = useState([]);
  const [selectedDate, setSelectedDate] = useState(null);
  const [industryList, setIndustryList] = useState([]);
  const [selectedIndustry, setSelectedIndustry] = useState(null);
  const [messageList, setMessageList] = useState([]);
  const [loading, setLoading] = useState(false);

  const currentFirstLevel = MENU_CONFIG.find((m) => m.key === selectedFirstLevel);
  const secondLevelItems = currentFirstLevel?.children || [];

  useEffect(() => {
    const user = localStorage.getItem('user');
    if (!user) {
      navigate('/login');
      return;
    }
  }, [navigate]);

  useEffect(() => {
    if (activeTabKey === 'hot') {
      loadSubjectDates();
    } else if (activeTabKey === 'industry') {
      loadIndustryCategories();
    }
  }, [activeTabKey]);

  useEffect(() => {
    if (selectedDate && activeTabKey === 'hot') {
      loadMessagesByDate(selectedDate);
    }
  }, [selectedDate, activeTabKey]);

  useEffect(() => {
    if (selectedIndustry && activeTabKey === 'industry') {
      loadIndustryStocks(selectedIndustry.categoryCode);
    }
  }, [selectedIndustry, activeTabKey]);

  const loadSubjectDates = async () => {
    try {
      const res = await request.get('/subject/dates');
      if (res.code === 200) {
        setDateList(res.data || []);
        if (res.data && res.data.length > 0) {
          setSelectedDate(res.data[0].date);
        }
      }
    } catch (error) {
      message.error('加载主题列表失败');
    }
  };

  const loadMessagesByDate = async (date) => {
    setLoading(true);
    try {
      const res = await request.get(`/subject/messages?date=${date}`);
      if (res.code === 200) {
        setMessageList(res.data || []);
      }
    } catch (error) {
      message.error('加载消息列表失败');
    } finally {
      setLoading(false);
    }
  };

  const loadIndustryCategories = async () => {
    try {
      const res = await request.get('/subject/industry/categories');
      if (res.code === 200) {
        setIndustryList(res.data || []);
        if (res.data && res.data.length > 0) {
          setSelectedIndustry(res.data[0]);
        }
      }
    } catch (error) {
      message.error('加载行业列表失败');
    }
  };

  const loadIndustryStocks = async (categoryCode) => {
    setLoading(true);
    try {
      const res = await request.get(`/subject/industry/stocks?categoryCode=${categoryCode}`);
      if (res.code === 200) {
        setMessageList(res.data || []);
      }
    } catch (error) {
      message.error('加载行业股票失败');
    } finally {
      setLoading(false);
    }
  };

  /** 点击二级菜单：若该菜单已打开则切换到对应标签，否则新增一个标签（同一菜单只开一个） */
  const handleSecondLevelClick = (key, label) => {
    const exists = openTabs.some((t) => t.key === key);
    if (exists) {
      setActiveTabKey(key);
      return;
    }
    setOpenTabs((prev) => [...prev, { key, label }]);
    setActiveTabKey(key);
  };

  const handleCloseTab = (targetKey, e) => {
    if (e && e.stopPropagation) e.stopPropagation();
    const index = openTabs.findIndex((t) => t.key === targetKey);
    if (index < 0) return;
    const next = openTabs.filter((t) => t.key !== targetKey);
    setOpenTabs(next);
    if (activeTabKey === targetKey) {
      setActiveTabKey(next.length ? next[Math.min(index, next.length - 1)].key : null);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/login');
  };

  const renderTabContent = () => {
    if (!activeTabKey) {
      return (
        <div className="empty-content">
          请从上方二级菜单选择功能，打开的页面将以标签形式显示在此处；同一菜单只会打开一个标签。
        </div>
      );
    }
    switch (activeTabKey) {
      case 'hot':
        return (
          <HotMain
            dateList={dateList}
            selectedDate={selectedDate}
            onSelectDate={setSelectedDate}
            messageList={messageList}
            loading={loading}
          />
        );
      case 'industry':
        return (
          <IndustryMain
            industryList={industryList}
            selectedIndustry={selectedIndustry}
            onSelectIndustry={setSelectedIndustry}
            messageList={messageList}
            loading={loading}
          />
        );
      case 'marketTrend':
        return <div className="placeholder-content">市场走势（功能开发中）</div>;
      case 'optionalStock':
        return <div className="placeholder-content">自选股（功能开发中）</div>;
      case 'allAStock':
        return <div className="placeholder-content">全部A股（功能开发中）</div>;
      case 'settings':
        return <div className="placeholder-content">系统设置（功能开发中）</div>;
      case 'mediation':
        return <div className="placeholder-content">投诉与调解（功能开发中）</div>;
      default:
        return null;
    }
  };

  const firstLevelMenuItems = MENU_CONFIG.map((item) => ({
    key: item.key,
    label: item.label,
  }));

  return (
    <Layout className="home-layout">
      <Header className="home-header">
        <div className="header-row">
          <div className="header-left">
            <h2 className="logo">久赢恒丰</h2>
            <Menu
              theme="dark"
              mode="horizontal"
              selectedKeys={[selectedFirstLevel]}
              items={firstLevelMenuItems}
              onClick={({ key }) => setSelectedFirstLevel(key)}
              style={{ flex: 1, minWidth: 0 }}
            />
          </div>
          <Button
            type="text"
            icon={<LogoutOutlined />}
            onClick={handleLogout}
            style={{ color: 'white' }}
          >
            退出
          </Button>
        </div>
        <div className="second-level-bar">
          <Menu
            theme="dark"
            mode="horizontal"
            selectedKeys={activeTabKey ? [activeTabKey] : []}
            className="second-level-menu second-level-menu-horizontal"
            items={secondLevelItems.map((item) => ({
              key: item.key,
              icon: item.icon,
              label: item.label,
              onClick: () => handleSecondLevelClick(item.key, item.label),
            }))}
          />
        </div>
      </Header>
      <Layout className="home-content-layout">
        <Content className="home-content">
          {openTabs.length > 0 ? (
            <Tabs
              type="editable-card"
              hideAdd
              activeKey={activeTabKey || openTabs[0].key}
              onChange={setActiveTabKey}
              onEdit={(targetKey, action) => {
                if (action === 'remove' && targetKey) handleCloseTab(targetKey, {});
              }}
              className="workspace-tabs"
              items={openTabs.map((tab) => ({
                key: tab.key,
                label: tab.label,
                children: activeTabKey === tab.key ? renderTabContent() : null,
              }))}
            />
          ) : (
            <div className="workspace-empty">{renderTabContent()}</div>
          )}
        </Content>
      </Layout>
    </Layout>
  );
};

export default Home;
