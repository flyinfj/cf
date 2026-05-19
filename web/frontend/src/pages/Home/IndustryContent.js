import React, { useMemo, useState, useRef, useEffect } from 'react';
import { Table, Tabs } from 'antd';
import { PlusOutlined, MinusOutlined, CaretRightOutlined, CaretDownOutlined } from '@ant-design/icons';
import request from '../../utils/request';
import '../Home.css';

/** 格式化价格/数值，空值显示 - */
function fmtNum(val, decimals = 2) {
  if (val == null || val === '') return '—';
  const n = Number(val);
  if (Number.isNaN(n)) return '—';
  return decimals === 0 ? n.toLocaleString() : n.toLocaleString('zh-CN', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

/** 格式化成交额：元转万/亿 */
function fmtAmount(val) {
  if (val == null || val === '') return '—';
  const n = Number(val);
  if (Number.isNaN(n)) return '—';
  if (n >= 1e8) return (n / 1e8).toFixed(2) + '亿';
  if (n >= 1e4) return (n / 1e4).toFixed(2) + '万';
  return n.toLocaleString();
}

/** 涨跌幅样式：正红负绿 */
function PctCell({ value }) {
  if (value == null || value === '') return '—';
  const n = Number(value);
  if (Number.isNaN(n)) return '—';
  const s = (n >= 0 ? '+' : '') + n.toFixed(2) + '%';
  return <span className={n >= 0 ? 'pct-up' : 'pct-down'}>{s}</span>;
}

/** 数值列排序：空值排最后 */
function sortByNum(dataIndex) {
  return (a, b) => {
    const va = a[dataIndex];
    const vb = b[dataIndex];
    const na = va != null && va !== '' ? Number(va) : NaN;
    const nb = vb != null && vb !== '' ? Number(vb) : NaN;
    if (Number.isNaN(na) && Number.isNaN(nb)) return 0;
    if (Number.isNaN(na)) return 1;
    if (Number.isNaN(nb)) return -1;
    return na - nb;
  };
}

/** 计算一组中的有效涨幅平均值（空值不参与） */
function avgPctChg(items, key = 'pctChg') {
  const vals = items.map((r) => r[key]).filter((v) => v != null && v !== '' && !Number.isNaN(Number(v)));
  if (!vals.length) return null;
  const sum = vals.reduce((a, v) => a + Number(v), 0);
  return sum / vals.length;
}

/** 判断列表中是否存在某字段非空（非 null/undefined/空字符串） */
function hasSomeNonEmpty(list, field) {
  if (!list || !list.length) return false;
  return list.some((r) => {
    const v = r[field];
    return v != null && String(v).trim() !== '';
  });
}

/** 为题材排名表生成带 rowSpan 的数据行（相同分类合并单元格），并计算各层平均涨幅 */
function buildRankRows(list) {
  if (!list || !list.length) return [];
  const rows = list.map((r, i) => ({ ...r, _index: i }));
  const getSpan = (key) => {
    const spans = {};
    let prev = null;
    let start = 0;
    rows.forEach((row, i) => {
      const v = row[key];
      if (v === prev) {
        spans[row._index] = 0;
      } else {
        if (prev !== null) spans[rows[start]._index] = i - start;
        start = i;
        prev = v;
      }
    });
    if (prev !== null) spans[rows[start]._index] = rows.length - start;
    return spans;
  };
  const span1 = getSpan('category1');
  const span2 = getSpan('category2');
  const span3 = getSpan('category3');
  // 按 category1/2/3 分组计算平均涨幅
  const avgByKey = (key) => {
    const groups = {};
    rows.forEach((row) => {
      const k = row[key] ?? '';
      if (!groups[k]) groups[k] = [];
      groups[k].push(row);
    });
    const res = {};
    Object.keys(groups).forEach((k) => {
      const avg = avgPctChg(groups[k]);
      groups[k].forEach((row) => {
        res[row._index] = avg;
      });
    });
    return res;
  };
  const _avgPctChg1 = avgByKey('category1');
  const _avgPctChg2 = avgByKey('category2');
  const _avgPctChg3 = avgByKey('category3');
  const fmtAvg = (avg) => (avg != null ? `${(avg >= 0 ? '+' : '') + avg.toFixed(2)}%` : '');
  return rows.map((row) => ({
    ...row,
    _rowSpan1: span1[row._index] ?? 1,
    _rowSpan2: span2[row._index] ?? 1,
    _rowSpan3: span3[row._index] ?? 1,
    _avgPctChg1: _avgPctChg1[row._index],
    _avgPctChg2: _avgPctChg2[row._index],
    _avgPctChg3: _avgPctChg3[row._index],
    _fmtAvg1: fmtAvg(_avgPctChg1[row._index]),
    _fmtAvg2: fmtAvg(_avgPctChg2[row._index]),
    _fmtAvg3: fmtAvg(_avgPctChg3[row._index]),
  }));
}

/** 从树节点收集所有叶子 */
function collectLeaves(node) {
  if (!node) return [];
  if (node.isLeaf) return [node];
  return (node.children || []).flatMap((c) => collectLeaves(c));
}

/** 将列表转为树：题材 -> 分类 -> 子类 -> 个股；若某层所有数据为空则跳过该层；题材与分类相同时去掉重复一层 */
function buildThemeTree(list) {
  if (!list || !list.length) return [];
  const levelKeys = ['category1', 'category2', 'category3'].filter((k) => hasSomeNonEmpty(list, k));
  if (levelKeys.length === 0) return [];

  const root = {};
  list.forEach((item, idx) => {
    const path = levelKeys.map((k) => item[k] != null && String(item[k]).trim() !== '' ? String(item[k]).trim() : '-');
    let cur = root;
    for (let i = 0; i < path.length; i++) {
      const key = path[i];
      if (i === path.length - 1) {
        if (!cur[key]) cur[key] = [];
        cur[key].push({
          key: `${idx}-${item.stockCode}`,
          title: `${item.stockName || ''} (${item.stockCode || ''})`,
          isLeaf: true,
          stockName: item.stockName,
          stockCode: item.stockCode,
          remarks: item.remarks,
          pctChg: item.pctChg,
        });
      } else {
        if (!cur[key]) cur[key] = {};
        cur = cur[key];
      }
    }
  });

  function toTreeNodes(obj, levelIdx, parentTitle) {
    if (!obj || typeof obj !== 'object') return [];
    const isLeafLevel = levelIdx === levelKeys.length - 1;
    return Object.keys(obj).flatMap((key) => {
      const val = obj[key];
      if (isLeafLevel && Array.isArray(val)) {
        return [{ key: `${levelIdx}-${key}`, title: key, children: val, avgPctChg: avgPctChg(val) }];
      }
      const children = toTreeNodes(val, levelIdx + 1, key);
      if (levelIdx >= 1 && key === parentTitle) {
        return children;
      }
      const allLeaves = children.flatMap((c) => collectLeaves(c));
      return [{ key: `${levelIdx}-${key}`, title: key, children, avgPctChg: avgPctChg(allLeaves) }];
    });
  }

  return toTreeNodes(root, 0, null);
}

/** 脑图：从左到右展开，根在左，每层子节点在父节点右侧，+/- 控制展开收起；根与节点可显示涨幅；展开后将该行滚入视口避免被挡 */
function MindMapView({ rootTitle, rootCount, rootPctChg, treeData, scrollContainerRef }) {
  const [expandedKeys, setExpandedKeys] = useState({});
  const [contentTopPadding, setContentTopPadding] = useState(0);
  const rowRefs = useRef({});
  const lastExpandedKeyRef = useRef(null);
  const contentWrapRef = useRef(null);
  const rootRef = useRef(null);

  const registerRowRef = (key, el) => {
    if (el) rowRefs.current[key] = el;
  };

  const toggle = (key) => {
    setExpandedKeys((prev) => {
      const next = { ...prev, [key]: !prev[key] };
      if (next[key]) lastExpandedKeyRef.current = key;
      return next;
    });
  };

  useEffect(() => {
    setContentTopPadding(0);
  }, [treeData]);

  /* 展开后：仅当该行在视口上方（被挡住）时微调滚动，避免整页 scrollIntoView 导致下移过多；用 padding 顶出时只设当前所需值不累加 */
  useEffect(() => {
    const key = lastExpandedKeyRef.current;
    if (!key || !scrollContainerRef?.current) return;
    const rowEl = rowRefs.current[key];
    const container = scrollContainerRef.current;
    if (!rowEl) return;
    lastExpandedKeyRef.current = null;
    /* 等展开子节点渲染后再测量和调整，避免用上一帧的 topmost */
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        const rowRect = rowEl.getBoundingClientRect();
        const containerRect = container.getBoundingClientRect();
        const rowTopAboveView = rowRect.top < containerRect.top;
        if (rowTopAboveView) {
          /* 只滚动“刚好露出”的位移，避免 scrollIntoView 一次滚太多 */
          const delta = rowRect.top - containerRect.top;
          container.scrollTop += delta;
        }
        const tabPanel = container.closest('[role="tabpanel"]');
        const rootEl = rootRef.current;
        if (!tabPanel || !rootEl) return;
        let topmost = rootEl.getBoundingClientRect().top;
        Object.keys(expandedKeys).forEach((k) => {
          if (expandedKeys[k] && rowRefs.current[k]) {
            const top = rowRefs.current[k].getBoundingClientRect().top;
            if (top < topmost) topmost = top;
          }
        });
        const tabPanelRect = tabPanel.getBoundingClientRect();
        const tabPanelPaddingTop = parseFloat(getComputedStyle(tabPanel).paddingTop) || 0;
        const tabPanelVisibleTop = tabPanelRect.top + tabPanelPaddingTop;
        if (topmost < tabPanelVisibleTop) {
          const A = Math.round(tabPanelVisibleTop - topmost);
          /* 只设“当前所需”与“已有”的较大值，不累加，避免多点几次下移过多 */
          setContentTopPadding((prev) => Math.max(prev, A + 10));
        }
      });
    });
  }, [expandedKeys, scrollContainerRef]);

  if (!treeData || treeData.length === 0) {
    return (
      <div ref={contentWrapRef} className="mind-map-wrap mind-map-ltr" style={{ paddingTop: contentTopPadding }}>
        <div ref={rootRef} className="mind-map-root">
          <div className="mind-map-root-title">
            {rootTitle || '—'}
            {rootCount != null && <span className="mind-map-root-count">({rootCount})</span>}
          </div>
        </div>
        <div className="mind-map-empty">暂无题材数据</div>
      </div>
    );
  }

  return (
    <div ref={contentWrapRef} className="mind-map-wrap mind-map-ltr" style={{ paddingTop: contentTopPadding }}>
      <div ref={rootRef} className="mind-map-root">
        <div className="mind-map-root-title">
          {rootTitle || '—'}
          {rootCount != null && <span className="mind-map-root-count">({rootCount})</span>}
        </div>
        {rootPctChg != null && (
          <div className={`mind-map-root-pct ${rootPctChg >= 0 ? 'pct-up' : 'pct-down'}`}>
            {(rootPctChg >= 0 ? '+' : '') + Number(rootPctChg).toFixed(2)}%
          </div>
        )}
      </div>
      <div className="mind-map-h-branch">
        <div className="mind-map-h-line" />
        <div className="mind-map-v-branch">
          {treeData.map((node) => (
            <MindMapNode
              key={node.key}
              node={node}
              expanded={!!expandedKeys[node.key]}
              onToggle={() => toggle(node.key)}
              expandedKeys={expandedKeys}
              onToggleKey={toggle}
              registerRowRef={registerRowRef}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

/** 脑图节点：节点框在左，展开时子节点在右侧（横向展开）；显示涨幅 */
function MindMapNode({ node, expanded, onToggle, expandedKeys, onToggleKey, registerRowRef }) {
  const hasChildren = node.children && node.children.length > 0;
  const isLeaf = node.isLeaf;
  const pctVal = node.avgPctChg != null ? node.avgPctChg : (node.pctChg != null ? node.pctChg : null);
  const pctStr = pctVal != null ? (pctVal >= 0 ? '+' : '') + Number(pctVal).toFixed(2) + '%' : null;

  return (
    <div
      className="mind-map-row"
      ref={(el) => registerRowRef?.(node.key, el)}
    >
      <div className="mind-map-node">
        <div className="mind-map-node-content">
          <div className="mind-map-node-title">
            {node.title}
            {!isLeaf && hasChildren && <span className="mind-map-node-count">({node.children.length})</span>}
          </div>
          {pctStr != null && (
            <div className={`mind-map-node-pct ${pctVal >= 0 ? 'pct-up' : 'pct-down'}`}>{pctStr}</div>
          )}
        </div>
        {hasChildren && (
          <button
            type="button"
            className="mind-map-node-expand"
            onClick={(e) => {
              e.stopPropagation();
              onToggle();
            }}
            aria-label={expanded ? '收起' : '展开'}
          >
            {expanded ? <MinusOutlined /> : <PlusOutlined />}
          </button>
        )}
      </div>
      {hasChildren && expanded && (
        <div className="mind-map-h-branch mind-map-sub-branch">
          <div className="mind-map-h-line" />
          <div className="mind-map-v-branch mind-map-sub-nodes">
            {node.children.map((child) =>
              child.isLeaf ? (
                <div key={child.key} className="mind-map-leaf-row">
                  <div className="mind-map-leaf-box mind-map-leaf-name-code">
                    <div className="mind-map-leaf-name">{child.stockName || '—'}</div>
                    <div className="mind-map-leaf-code">{child.stockCode || '—'}</div>
                    {child.pctChg != null && (
                      <div className={`mind-map-leaf-pct ${child.pctChg >= 0 ? 'pct-up' : 'pct-down'}`}>
                        {(child.pctChg >= 0 ? '+' : '') + Number(child.pctChg).toFixed(2)}%
                      </div>
                    )}
                  </div>
                  <div className="mind-map-leaf-line" />
                  <div className="mind-map-leaf-box mind-map-leaf-remarks">
                    {child.remarks || '—'}
                  </div>
                </div>
              ) : (
                <MindMapNode
                  key={child.key}
                  node={child}
                  expanded={!!expandedKeys[child.key]}
                  onToggle={() => onToggleKey(child.key)}
                  expandedKeys={expandedKeys}
                  onToggleKey={onToggleKey}
                  registerRowRef={registerRowRef}
                />
              )
            )}
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * 全部题材 - 左侧题材树不变，右侧 4 个 Tab：题材成分、题材排名、题材图谱、题材介绍
 */
export const IndustryMain = ({
  industryList,
  selectedIndustry,
  onSelectIndustry,
  messageList,
  loading,
}) => {
  const [innerTab, setInnerTab] = useState('ingredient');
  const treeWrapRef = useRef(null);
  const tableScrollWrapRef = useRef(null);
  const graphScrollRef = useRef(null);
  const [treeScrollY, setTreeScrollY] = useState(400);
  const [tableScrollY, setTableScrollY] = useState(400);
  const [expandedRowKeys, setExpandedRowKeys] = useState([]);
  const [loadedChildren, setLoadedChildren] = useState({});
  const [loadingChildCode, setLoadingChildCode] = useState(null);

  const loadChildren = async (categoryCode) => {
    if (loadedChildren[categoryCode]) return;
    setLoadingChildCode(categoryCode);
    try {
      const res = await request.get(`/subject/industry/categories?categoryCode=${encodeURIComponent(categoryCode)}`);
      if (res?.code === 200 && Array.isArray(res.data)) {
        setLoadedChildren((prev) => ({ ...prev, [categoryCode]: res.data }));
      }
    } finally {
      setLoadingChildCode(null);
    }
  };

  useEffect(() => {
    if (!treeWrapRef.current) return;
    const el = treeWrapRef.current;
    const update = () => setTreeScrollY(el.clientHeight);
    update();
    const ro = new ResizeObserver(update);
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  /* 题材成分/题材排名：根据容器高度设置表格 body 可滚动高度（表头约 39px） */
  useEffect(() => {
    const el = tableScrollWrapRef.current;
    if (!el) return;
    const headerH = 39;
    const update = () => setTableScrollY(Math.max(800, (el.clientHeight - headerH) * 3));
    update();
    const ro = new ResizeObserver(update);
    ro.observe(el);
    return () => ro.disconnect();
  }, [innerTab]);

  const rankRows = useMemo(() => buildRankRows(messageList), [messageList]);
  const themeTree = useMemo(() => buildThemeTree(messageList), [messageList]);
  const rootTitle = selectedIndustry?.category || '全部题材';
  const { graphTreeData, graphRootPctChg } = useMemo(() => {
    if (!themeTree?.length) return { graphTreeData: themeTree, graphRootPctChg: undefined };
    const single = themeTree.length === 1 && rootTitle && themeTree[0].title === rootTitle;
    return {
      graphTreeData: single ? themeTree[0].children : themeTree,
      graphRootPctChg: single ? themeTree[0].avgPctChg : undefined,
    };
  }, [themeTree, rootTitle]);

  const showCategory1 = hasSomeNonEmpty(messageList, 'category1');
  const showCategory2 = hasSomeNonEmpty(messageList, 'category2');
  const showCategory3 = hasSomeNonEmpty(messageList, 'category3');

  const ingredientCategoryColumns = [
    showCategory1 && { title: '题材', dataIndex: 'category1', key: 'category1', width: 100 },
    showCategory2 && { title: '分类', dataIndex: 'category2', key: 'category2', width: 90 },
    showCategory3 && { title: '子类', dataIndex: 'category3', key: 'category3', width: 90 },
  ].filter(Boolean);

  const tabItems = [
    {
      key: 'ingredient',
      label: '题材成分',
      children: (
        <div ref={tableScrollWrapRef} className="industry-stock-table">
          <Table
            loading={loading}
            dataSource={messageList}
            rowKey={(record, index) => `${record.stockCode}-${index}`}
            pagination={false}
            size="small"
            scroll={{ y: tableScrollY }}
            columns={[
              ...ingredientCategoryColumns,
              { title: '代码', dataIndex: 'stockCode', key: 'stockCode', width: 88 },
              { title: '名称', dataIndex: 'stockName', key: 'stockName', width: 80 },
              { title: '昨收', dataIndex: 'preClose', key: 'preClose', width: 82, align: 'right', sorter: sortByNum('preClose'), render: (v) => fmtNum(v) },
              { title: '开盘', dataIndex: 'open', key: 'open', width: 78, align: 'right', sorter: sortByNum('open'), render: (v) => fmtNum(v) },
              { title: '最高', dataIndex: 'high', key: 'high', width: 78, align: 'right', sorter: sortByNum('high'), render: (v) => fmtNum(v) },
              { title: '最低', dataIndex: 'low', key: 'low', width: 78, align: 'right', sorter: sortByNum('low'), render: (v) => fmtNum(v) },
              { title: '当前价', dataIndex: 'close', key: 'close', width: 78, align: 'right', sorter: sortByNum('close'), render: (v) => fmtNum(v) },
              { title: '涨幅', dataIndex: 'pctChg', key: 'pctChg', width: 82, align: 'right', sorter: sortByNum('pctChg'), render: (v) => <PctCell value={v} /> },
              { title: '成交量', dataIndex: 'vol', key: 'vol', width: 90, align: 'right', sorter: sortByNum('vol'), render: (v) => fmtNum(v, 0) },
              { title: '成交额', dataIndex: 'amount', key: 'amount', width: 88, align: 'right', sorter: sortByNum('amount'), render: (v) => fmtAmount(v) },
              { title: '量比', dataIndex: 'vr', key: 'vr', width: 68, align: 'right', sorter: sortByNum('vr'), render: (v) => fmtNum(v) },
              { title: '换手', dataIndex: 'turnoverRate', key: 'turnoverRate', width: 78, align: 'right', sorter: sortByNum('turnoverRate'), render: (v) => (v != null && v !== '' ? `${Number(v).toFixed(2)}%` : '—') },
              { title: '备注', dataIndex: 'remarks', key: 'remarks', width: 120, ellipsis: true },
            ]}
          />
        </div>
      ),
    },
    {
      key: 'rank',
      label: '题材排名',
      children: (
        <div ref={tableScrollWrapRef} className="industry-stock-table industry-rank-table">
          <Table
            loading={loading}
            dataSource={rankRows}
            rowKey={(_, i) => String(i)}
            pagination={false}
            size="small"
            scroll={{ y: tableScrollY }}
            columns={[
              showCategory1 && {
                title: '题材',
                dataIndex: 'category1',
                key: 'category1',
                width: 140,
                render: (val, row) => ({
                  children: (
                    <>
                      <div>{val}</div>
                      {row._rowSpan1 > 0 && row._fmtAvg1 && (
                        <div className={`rank-cell-avg ${row._avgPctChg1 >= 0 ? 'pct-up' : 'pct-down'}`}>{row._fmtAvg1}</div>
                      )}
                    </>
                  ),
                  props: { rowSpan: row._rowSpan1 },
                }),
              },
              showCategory2 && {
                title: '分类',
                dataIndex: 'category2',
                key: 'category2',
                width: 140,
                render: (val, row) => ({
                  children: (
                    <>
                      <div>{val}</div>
                      {row._rowSpan2 > 0 && row._fmtAvg2 && (
                        <div className={`rank-cell-avg ${row._avgPctChg2 >= 0 ? 'pct-up' : 'pct-down'}`}>{row._fmtAvg2}</div>
                      )}
                    </>
                  ),
                  props: { rowSpan: row._rowSpan2 },
                }),
              },
              showCategory3 && {
                title: '子类',
                dataIndex: 'category3',
                key: 'category3',
                width: 140,
                render: (val, row) => ({
                  children: (
                    <>
                      <div>{val}</div>
                      {row._rowSpan3 > 0 && row._fmtAvg3 && (
                        <div className={`rank-cell-avg ${row._avgPctChg3 >= 0 ? 'pct-up' : 'pct-down'}`}>{row._fmtAvg3}</div>
                      )}
                    </>
                  ),
                  props: { rowSpan: row._rowSpan3 },
                }),
              },
              { title: '代码', dataIndex: 'stockCode', key: 'stockCode', width: 100 },
              { title: '名称', dataIndex: 'stockName', key: 'stockName', width: 120 },
              {
                title: '涨幅',
                dataIndex: 'pctChg',
                key: 'pctChg',
                width: 88,
                align: 'right',
                render: (v) => <PctCell value={v} />,
              },
              { title: '备注', dataIndex: 'remarks', key: 'remarks', ellipsis: true },
            ].filter(Boolean)}
          />
        </div>
      ),
    },
    {
      key: 'graph',
      label: '题材图谱',
      children: (
        <div ref={graphScrollRef} className="theme-tree-wrap mind-map-wrap-container">
          <MindMapView
            rootTitle={rootTitle}
            rootCount={messageList?.length ?? undefined}
            rootPctChg={graphRootPctChg}
            treeData={graphTreeData}
            scrollContainerRef={graphScrollRef}
          />
        </div>
      ),
    },
    {
      key: 'intro',
      label: '题材介绍',
      children: (
        <div className="theme-intro">
          {selectedIndustry ? (
            <>
              <h4 className="theme-intro-title">{selectedIndustry.category}</h4>
              <p className="theme-intro-desc">（暂无详细介绍，可后续补充）</p>
            </>
          ) : (
            <p className="theme-intro-empty">请从左侧选择题材</p>
          )}
        </div>
      ),
    },
  ];

  const industryColumns = [
    { title: '题材', dataIndex: 'category', key: 'category', width: 90, ellipsis: true, render: (v) => v || '—' },
    { title: '涨幅', dataIndex: 'pctChg', key: 'pctChg', width: 72, align: 'right', render: (v) => <PctCell value={v} /> },
    { title: '涨幅分布', dataIndex: 'pctdis', key: 'pctdis', width: 72, align: 'center', render: (v) => v || '—' },
    { title: '成交量', dataIndex: 'vol', key: 'vol', width: 72, align: 'right', render: (v) => fmtNum(v, 0) },
    { title: '成交额', dataIndex: 'amount', key: 'amount', width: 72, align: 'right', render: (v) => fmtAmount(v) },
  ];

  const expandable = {
    expandIconColumnIndex: 0,
    expandedRowKeys,
    onExpand: (expanded, record) => {
      if (expanded) {
        setExpandedRowKeys((prev) => [...prev, record.categoryCode]);
        if ((record.childCategory ?? 0) > 0 && !loadedChildren[record.categoryCode]) {
          loadChildren(record.categoryCode);
        }
      } else {
        setExpandedRowKeys((prev) => prev.filter((k) => k !== record.categoryCode));
      }
    },
    expandIcon: ({ expanded, onExpand, record }) => {
      const hasChild = (record.childCategory ?? 0) > 0;
      if (!hasChild) return <span className="industry-tree-expand-placeholder" />;
      return (
        <span
          className="industry-tree-expand-icon"
          onClick={(e) => {
            e.stopPropagation();
            onExpand(record, e);
          }}
          role="button"
          aria-label={expanded ? '收起' : '展开'}
        >
          {expanded ? <CaretDownOutlined /> : <CaretRightOutlined />}
        </span>
      );
    },
    expandedRowRender: (record) => {
      const children = loadedChildren[record.categoryCode];
      const loading = loadingChildCode === record.categoryCode;
      if (loading && (!children || children.length === 0)) {
        return <div className="industry-tree-children-loading">加载中...</div>;
      }
      if (!children || children.length === 0) return null;
      return (
        <Table
          size="small"
          showHeader={false}
          dataSource={children}
          rowKey="categoryCode"
          pagination={false}
          columns={industryColumns}
          className="industry-tree-nested-table"
          onRow={(row) => ({
            onClick: () => onSelectIndustry(row),
            className: selectedIndustry?.categoryCode === row.categoryCode ? 'industry-row-active' : '',
          })}
        />
      );
    },
  };

  return (
    <div className="content-inner content-inner-industry">
      <div className="content-panel content-panel-industry-tree">
        <div ref={treeWrapRef} className="industry-tree-table-wrap">
          <Table
            className="industry-tree-table in-content"
            size="small"
            dataSource={industryList}
            rowKey="categoryCode"
            columns={industryColumns}
            pagination={false}
            scroll={{ y: treeScrollY }}
            expandable={expandable}
            onRow={(record) => ({
              onClick: () => onSelectIndustry(record),
              className: selectedIndustry?.categoryCode === record.categoryCode ? 'industry-row-active' : '',
            })}
          />
        </div>
      </div>
      <div className="content-body">
        <Tabs
          activeKey={innerTab}
          onChange={setInnerTab}
          type="card"
          className="theme-detail-tabs"
          destroyInactiveTabPane
          items={tabItems}
        />
      </div>
    </div>
  );
};

export default { IndustryMain };
