import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, Row, Col, Select, DatePicker, Spin, Alert, Table, Button } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';

const { Option } = Select;

const DemographicReport = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [report, setReport] = useState(null);
  const [states, setStates] = useState([]);
  const [lgas, setLgas] = useState([]);
  const [selectedState, setSelectedState] = useState(null);
  const [selectedLga, setSelectedLga] = useState(null);
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
    fetchReport();
  }, []);

  useEffect(() => {
    // Fetch LGAs when state changes
    if (selectedState) {
      const fetchLgas = async () => {
        try {
          const response = await axios.get(`/api/location/lgas/?state_id=${selectedState}`);
          setLgas(response.data);
        } catch (err) {
          console.error('Error fetching LGAs:', err);
        }
      };

      fetchLgas();
      setSelectedLga(null);
    } else {
      setLgas([]);
      setSelectedLga(null);
    }
  }, [selectedState]);

  const fetchReport = async () => {
    setLoading(true);
    setError(null);

    try {
      // Build query parameters
      const params = {};
      if (selectedState) params.state_id = selectedState;
      if (selectedLga) params.lga_id = selectedLga;
      if (reportDate) params.report_date = reportDate.format('YYYY-MM-DD');

      const response = await axios.get('/api/reports/demographic/', { params });
      setReport(response.data);
    } catch (err) {
      setError('Failed to load report data. Please try again later.');
      console.error('Error fetching report:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStateChange = (value) => {
    setSelectedState(value);
  };

  const handleLgaChange = (value) => {
    setSelectedLga(value);
  };

  const handleDateChange = (date) => {
    setReportDate(date);
  };

  const handleApplyFilters = () => {
    fetchReport();
  };

  const handleExportCsv = () => {
    // Build query parameters
    const params = {};
    if (selectedState) params.state_id = selectedState;
    if (selectedLga) params.lga_id = selectedLga;
    if (reportDate) params.report_date = reportDate.format('YYYY-MM-DD');
    
    // Add report type
    params.type = 'demographic';
    
    // Generate URL with query parameters
    const queryString = Object.keys(params)
      .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
      .join('&');
    
    // Open export URL in new tab
    window.open(`/api/reports/export_csv/?${queryString}`, '_blank');
  };

  return (
    <div className="demographic-report">
      <h1>Demographic Report</h1>
      
      <div className="report-filters">
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
            <label>LGA:</label>
            <Select
              style={{ width: 200, marginLeft: 8 }}
              placeholder="Select LGA"
              allowClear
              disabled={!selectedState}
              onChange={handleLgaChange}
              value={selectedLga}
            >
              {lgas.map(lga => (
                <Option key={lga.id} value={lga.id}>{lga.name}</Option>
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
            <Button
              type="primary"
              onClick={handleApplyFilters}
            >
              Apply Filters
            </Button>
          </Col>
          
          <Col>
            <Button
              icon={<DownloadOutlined />}
              onClick={handleExportCsv}
              disabled={!report}
            >
              Export CSV
            </Button>
          </Col>
        </Row>
      </div>
      
      {loading ? (
        <div className="loading-container">
          <Spin size="large" />
          <p>Loading report data...</p>
        </div>
      ) : error ? (
        <Alert type="error" message={error} />
      ) : report ? (
        <div className="report-content">
          {report.sections.map((section, index) => (
            <Card title={section.title} key={index} className="report-section">
              <Row gutter={16}>
                <Col span={12}>
                  <img
                    src={`data:image/png;base64,${section.chart}`}
                    alt={section.title}
                    style={{ width: '100%' }}
                  />
                </Col>
                <Col span={12}>
                  <Table
                    dataSource={section.data}
                    rowKey={(record, index) => index}
                    pagination={false}
                    size="small"
                    columns={Object.keys(section.data[0]).map(key => ({
                      title: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                      dataIndex: key,
                      key: key,
                      render: (text, record) => {
                        if (key === 'avg_percentage') {
                          return `${parseFloat(text).toFixed(2)}%`;
                        }
                        return text;
                      }
                    }))}
                  />
                </Col>
              </Row>
            </Card>
          ))}
        </div>
      ) : (
        <Alert type="info" message="No report data available. Please select filters and apply." />
      )}
    </div>
  );
};

export default DemographicReport;
