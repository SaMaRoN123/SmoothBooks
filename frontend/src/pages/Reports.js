import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Download
} from '@mui/icons-material';
import axios from '../config/axios';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

function Reports() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [reportType, setReportType] = useState('financial');
  const [dateRange, setDateRange] = useState('month');
  
  // Report data
  const [financialData, setFinancialData] = useState(null);
  const [revenueData, setRevenueData] = useState([]);
  const [expenseData, setExpenseData] = useState([]);
  const [invoiceData, setInvoiceData] = useState([]);
  const [payrollData, setPayrollData] = useState(null);

  const fetchReportData = useCallback(async () => {
    try {
      setLoading(true);
      setError('');
      
      if (reportType === 'financial') {
        const [financialRes, revenueRes, expenseRes] = await Promise.all([
          axios.get(`/api/reports/financial?range=${dateRange}`),
          axios.get(`/api/reports/revenue?range=${dateRange}`),
          axios.get(`/api/reports/expenses?range=${dateRange}`)
        ]);
        
        console.log('Financial data received:', financialRes.data);
        console.log('Revenue data received:', revenueRes.data);
        console.log('Expense data received:', expenseRes.data);
        
        setFinancialData(financialRes.data);
        setRevenueData(revenueRes.data.data);
        setExpenseData(expenseRes.data.data);
      } else if (reportType === 'invoices') {
        const response = await axios.get(`/api/reports/invoice-report?range=${dateRange}`);
        setInvoiceData(response.data.invoices);
      } else if (reportType === 'payroll') {
        const response = await axios.get(`/api/reports/payroll?range=${dateRange}`);
        setPayrollData(response.data);
      }
    } catch (err) {
      console.error('Error fetching report data:', err);
      if (err.response && err.response.data && err.response.data.error) {
        setError(`Failed to load report data: ${err.response.data.error}`);
      } else {
        setError('Failed to load report data. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  }, [reportType, dateRange]);

  useEffect(() => {
    fetchReportData();
  }, [fetchReportData]);

  const handleExport = async (type) => {
    try {
      const response = await axios.get(`/api/reports/export/csv?type=${type}&range=${dateRange}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${type}_report_${dateRange}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError('Failed to export report');
      console.error('Error exporting report:', err);
    }
  };

  const renderFinancialReport = () => (
    <Grid container spacing={3}>
      {/* Summary Cards */}
      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Total Revenue
            </Typography>
            <Typography variant="h4" color="success.main">
              ${financialData?.total_revenue?.toLocaleString() || '0'}
            </Typography>
            <Box display="flex" alignItems="center" mt={1}>
              {financialData?.revenue_growth > 0 ? (
                <TrendingUp color="success" fontSize="small" />
              ) : (
                <TrendingDown color="error" fontSize="small" />
              )}
              <Typography
                variant="body2"
                color={financialData?.revenue_growth > 0 ? 'success.main' : 'error.main'}
                ml={0.5}
              >
                {financialData?.revenue_growth?.toFixed(1)}%
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Total Expenses
            </Typography>
            <Typography variant="h4" color="error.main">
              ${financialData?.total_expenses?.toLocaleString() || '0'}
            </Typography>
            <Box display="flex" alignItems="center" mt={1}>
              {financialData?.expense_growth < 0 ? (
                <TrendingUp color="success" fontSize="small" />
              ) : (
                <TrendingDown color="error" fontSize="small" />
              )}
              <Typography
                variant="body2"
                color={financialData?.expense_growth < 0 ? 'success.main' : 'error.main'}
                ml={0.5}
              >
                {financialData?.expense_growth?.toFixed(1)}%
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Net Profit
            </Typography>
            <Typography variant="h4" color="primary.main">
              ${financialData?.net_profit?.toLocaleString() || '0'}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Profit Margin: {financialData?.profit_margin?.toFixed(1)}%
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Outstanding
            </Typography>
            <Typography variant="h4" color="warning.main">
              ${financialData?.outstanding_amount?.toLocaleString() || '0'}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {financialData?.outstanding_count || 0} invoices
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* Charts */}
      <Grid item xs={12} md={8}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Revenue vs Expenses Trend
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={revenueData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip 
                formatter={(value, name) => [`$${value.toLocaleString()}`, name]}
                contentStyle={{
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: '1px solid #ccc',
                  borderRadius: '4px',
                  padding: '8px'
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#8884d8"
                name="Revenue"
                strokeWidth={2}
              />
              <Line
                type="monotone"
                dataKey="expenses"
                stroke="#82ca9d"
                name="Expenses"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>

      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Expense Breakdown
          </Typography>
          {expenseData && expenseData.length > 0 ? (
            <ResponsiveContainer width="100%" height={350}>
              <PieChart>
                <Pie
                  data={expenseData}
                  cx="50%"
                  cy="45%"
                  labelLine={false}
                  label={false}
                  outerRadius={70}
                  innerRadius={25}
                  fill="#8884d8"
                  dataKey="amount"
                  paddingAngle={3}
                >
                  {expenseData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value, name) => [`$${value.toLocaleString()}`, name]}
                  labelFormatter={(label) => `${label}`}
                  contentStyle={{
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    border: '1px solid #ccc',
                    borderRadius: '4px',
                    padding: '8px'
                  }}
                />
                <Legend 
                  verticalAlign="bottom" 
                  height={60}
                  iconType="circle"
                  formatter={(value, entry) => (
                    <span style={{ color: entry.color, fontSize: '11px', fontWeight: '500' }}>
                      {value} (${entry.payload.amount.toLocaleString()})
                    </span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <Box display="flex" justifyContent="center" alignItems="center" height={200}>
              <Typography color="textSecondary">
                No expense data available
              </Typography>
            </Box>
          )}
        </Paper>
      </Grid>
    </Grid>
  );

  const renderInvoiceReport = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Invoice Status Report
            </Typography>
            <Button
              variant="outlined"
              startIcon={<Download />}
              onClick={() => handleExport('invoices')}
            >
              Export
            </Button>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Invoice #</TableCell>
                  <TableCell>Client</TableCell>
                  <TableCell>Issue Date</TableCell>
                  <TableCell>Due Date</TableCell>
                  <TableCell>Amount</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Days Overdue</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {invoiceData.map((invoice) => (
                  <TableRow key={invoice.id}>
                    <TableCell>{invoice.invoice_number}</TableCell>
                    <TableCell>{invoice.client_name}</TableCell>
                    <TableCell>{new Date(invoice.issue_date).toLocaleDateString()}</TableCell>
                    <TableCell>{new Date(invoice.due_date).toLocaleDateString()}</TableCell>
                    <TableCell>${parseFloat(invoice.total_amount).toLocaleString()}</TableCell>
                    <TableCell>
                      <Chip
                        label={invoice.status}
                        color={
                          invoice.status === 'paid' ? 'success' :
                          invoice.status === 'overdue' ? 'error' :
                          invoice.status === 'sent' ? 'primary' : 'default'
                        }
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {invoice.status === 'overdue' ? 
                        Math.floor((new Date() - new Date(invoice.due_date)) / (1000 * 60 * 60 * 24)) : 
                        '-'
                      }
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </Grid>
    </Grid>
  );

  const renderPayrollReport = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Total Payroll
            </Typography>
            <Typography variant="h4">
              ${payrollData?.total_payroll?.toLocaleString() || '0'}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Active Employees
            </Typography>
            <Typography variant="h4" color="success.main">
              {payrollData?.active_employees || 0}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Average Salary
            </Typography>
            <Typography variant="h4">
              ${payrollData?.average_salary?.toLocaleString() || '0'}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Typography color="textSecondary" gutterBottom>
              Payroll Records
            </Typography>
            <Typography variant="h4">
              {payrollData?.payroll_records?.length || 0}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Payroll Summary
            </Typography>
            <Button
              variant="outlined"
              startIcon={<Download />}
              onClick={() => handleExport('payroll')}
            >
              Export
            </Button>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Employee</TableCell>
                  <TableCell>Position</TableCell>
                  <TableCell>Hours Worked</TableCell>
                  <TableCell>Gross Pay</TableCell>
                  <TableCell>Net Pay</TableCell>
                  <TableCell>Pay Date</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {payrollData?.payroll_records?.map((record) => (
                  <TableRow key={record.id}>
                    <TableCell>{record.employee_name}</TableCell>
                    <TableCell>{record.position}</TableCell>
                    <TableCell>{record.hours_worked}</TableCell>
                    <TableCell>${parseFloat(record.gross_pay).toLocaleString()}</TableCell>
                    <TableCell>${parseFloat(record.net_pay).toLocaleString()}</TableCell>
                    <TableCell>{new Date(record.pay_date).toLocaleDateString()}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </Grid>
    </Grid>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Reports & Analytics
        </Typography>
        <Box>
          <FormControl sx={{ minWidth: 120, mr: 2 }}>
            <InputLabel>Report Type</InputLabel>
            <Select
              value={reportType}
              label="Report Type"
              onChange={(e) => setReportType(e.target.value)}
            >
              <MenuItem value="financial">Financial</MenuItem>
              <MenuItem value="invoices">Invoices</MenuItem>
              <MenuItem value="payroll">Payroll</MenuItem>
            </Select>
          </FormControl>
          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel>Date Range</InputLabel>
            <Select
              value={dateRange}
              label="Date Range"
              onChange={(e) => setDateRange(e.target.value)}
            >
              <MenuItem value="week">This Week</MenuItem>
              <MenuItem value="month">This Month</MenuItem>
              <MenuItem value="quarter">This Quarter</MenuItem>
              <MenuItem value="year">This Year</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {reportType === 'financial' && renderFinancialReport()}
      {reportType === 'invoices' && renderInvoiceReport()}
      {reportType === 'payroll' && renderPayrollReport()}
    </Box>
  );
}

export default Reports; 