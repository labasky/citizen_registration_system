import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, Row, Col, Statistic, Select, DatePicker, Spin, Alert } from 'antd';
import { UserOutlined, BriefcaseOutlined, HomeOutlined } from '@ant-design/icons';

const { Option } = Select;

const ExecutiveDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [states, setStates] = useState([]);
  const [selectedState, setSelectedState] = useState(null);
  const [reportDate, setReportDate] = useState(null);

  useEffect(() => {
    // Fetch states
    const fetchStates = async () => {
      try {
        const response = await axios.get('/api/location/states/');
        setStates(response.data);
      } catch (err) {
        console.error('Error fetching states:', err);
      }
    };

    fetchStates();
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    setLoading(true);
    setError(null);

    try {
      // Build query parameters
      const params = {};
      if (selectedState) params.state_id = selectedState;
      if (reportDate) params.report_date = reportDate.format('YYYY-MM-DD');

      const response = await axios.get('/api/reports/executive_dashboard/', { params });
      setDashboard(response.data);
    } catch (err) {
      setError('Failed to load dashboard data. Please try again later.');
      console.error('Error fetching dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStateChange = (value) => {
    setSelectedState(value);
  };

  const handleDateChange = (date) => {
    setReportDate(date);
  };

  const handleApplyFilters = () => {
    fetchDashboard();
  };

  const getIconForMetric = (iconName) => {
    switch (iconName) {
      case 'users':
        return <UserOutlined />;
      case 'briefcase':
        return <BriefcaseOutlined />;
      case 'home':
        return <HomeOutlined />;
      default:
        return null;
    }
  };

  return (
    <div className="executive-dashboard">
      <h1>Executive Dashboard</h1>
      
      <div className="dashboard-filters">
        <Row gutter={16} align="middle">
          <Col>
            <label>State:</label>
            <Select
              style={{ width: 200, marginLeft: 8 }}
              placeholder="Select State"
              allowClear
              onChange={handleStateChange}
              value={selectedState}
            >
              {states.map(state => (
                <Option key={state.id} value={state.id}>{state.name}</Option>
              ))}
            </Select>
          </Col>
          
          <Col>
            <label>Report Date:</label>
            <DatePicker
              style={{ marginLeft: 8 }}
              onChange={handleDateChange}
              value={reportDate}
            />
          </Col>
          
          <Col>
            <button
              className="btn-primary"
              onClick={handleApplyFilters}
            >
              Apply Filters
            </button>
          </Col>
        </Row>
      </div>
      
      {loading ? (
        <div className="loading-container">
          <Spin size="large" />
          <p>Loading dashboard data...</p>
        </div>
      ) : error ? (
        <Alert type="error" message={error} />
      ) : dashboard ? (
        <div className="dashboard-content">
          <Row gutter={16} className="metric-cards">
            {dashboard.metrics.map((metric, index) => (
              <Col span={8} key={index}>
                <Card>
                  <Statistic
                    title={metric.name}
                    value={metric.value}
                    prefix={getIconForMetric(metric.icon)}
                  />
                </Card>
              </Col>
            ))}
          </Row>
          
          <Row gutter={16} className="chart-cards">
            {dashboard.charts.map((chart, index) => (
              <Col span={12} key={index}>
                <Card title={chart.title}>
                  <img
                    src={`data:image/png;base64,${chart.image}`}
                    alt={chart.title}
                    style={{ width: '100%' }}
                  />
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      ) : (
        <Alert type="info" message="No dashboard data available. Please select filters and apply." />
      )}
    </div>
  );
};

export default ExecutiveDashboard;
