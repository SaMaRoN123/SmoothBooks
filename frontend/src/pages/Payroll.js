import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  Chip,
  Tabs,
  Tab
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Payment,
  Schedule
} from '@mui/icons-material';
import axios from '../config/axios';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`payroll-tabpanel-${index}`}
      aria-labelledby={`payroll-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

function Payroll() {
  const [tabValue, setTabValue] = useState(0);
  const [employees, setEmployees] = useState([]);
  const [payrollRecords, setPayrollRecords] = useState([]);
  const [timeEntries, setTimeEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Employee dialog state
  const [openEmployeeDialog, setOpenEmployeeDialog] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState(null);
  const [employeeForm, setEmployeeForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    position: '',
    hourly_rate: '',
    hire_date: '',
    status: 'active'
  });

  // Time entry dialog state
  const [openTimeDialog, setOpenTimeDialog] = useState(false);
  const [editingTimeEntry, setEditingTimeEntry] = useState(null);
  const [timeForm, setTimeForm] = useState({
    employee_id: '',
    date: '',
    start_time: '',
    end_time: '',
    notes: ''
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [employeesRes, payrollRes, timeRes] = await Promise.all([
        axios.get('/api/payroll/employees'),
        axios.get('/api/payroll/records'),
        axios.get('/api/payroll/time-entries')
      ]);
      
      setEmployees(employeesRes.data.employees);
      setPayrollRecords(payrollRes.data.payroll_records);
      setTimeEntries(timeRes.data.time_entries);
    } catch (err) {
      setError('Failed to load payroll data');
      console.error('Error fetching payroll data:', err);
    } finally {
      setLoading(false);
    }
  };

  // Employee management functions
  const handleOpenEmployeeDialog = (employee = null) => {
    if (employee) {
      setEditingEmployee(employee);
      setEmployeeForm({
        first_name: employee.first_name,
        last_name: employee.last_name,
        email: employee.email,
        position: employee.position,
        salary: employee.salary,
        hourly_rate: employee.hourly_rate,
        hire_date: employee.hire_date,
        status: employee.status
      });
    } else {
      setEditingEmployee(null);
      setEmployeeForm({
        first_name: '',
        last_name: '',
        email: '',
        position: '',
        salary: '',
        hourly_rate: '',
        hire_date: new Date().toISOString().split('T')[0],
        status: 'active'
      });
    }
    setOpenEmployeeDialog(true);
  };

  const handleCloseEmployeeDialog = () => {
    setOpenEmployeeDialog(false);
    setEditingEmployee(null);
  };

  const handleEmployeeSubmit = async () => {
    // Clear previous errors
    setError('');
    
    try {
      // Validate required fields
      if (!employeeForm.first_name) {
        setError('First name is required');
        return;
      }
      
      if (!employeeForm.last_name) {
        setError('Last name is required');
        return;
      }
      
      if (!employeeForm.email) {
        setError('Email is required');
        return;
      }
      
      if (!employeeForm.salary) {
        setError('Salary is required');
        return;
      }
      
      if (!employeeForm.hire_date) {
        setError('Hire date is required');
        return;
      }
      
      // Log the data being sent for debugging
      console.log('Sending employee data:', employeeForm);
      
      if (editingEmployee) {
        await axios.put(`/api/payroll/employees/${editingEmployee.id}`, employeeForm);
      } else {
        await axios.post('/api/payroll/employees', employeeForm);
      }
      fetchData();
      handleCloseEmployeeDialog();
    } catch (err) {
      console.error('Error saving employee:', err);
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError('Failed to save employee');
      }
    }
  };

  const handleDeleteEmployee = async (id) => {
    if (window.confirm('Are you sure you want to delete this employee?')) {
      try {
        await axios.delete(`/api/payroll/employees/${id}`);
        fetchData();
      } catch (err) {
        setError('Failed to delete employee');
        console.error('Error deleting employee:', err);
      }
    }
  };

  // Time entry functions
  const handleOpenTimeDialog = (entry = null) => {
    if (entry) {
      setEditingTimeEntry(entry);
      setTimeForm({
        employee_id: entry.employee_id,
        date: entry.date,
        start_time: entry.start_time,
        end_time: entry.end_time,
        notes: entry.notes || ''
      });
    } else {
      setEditingTimeEntry(null);
      setTimeForm({
        employee_id: '',
        date: new Date().toISOString().split('T')[0],
        start_time: '',
        end_time: '',
        notes: ''
      });
    }
    setOpenTimeDialog(true);
  };

  const handleCloseTimeDialog = () => {
    setOpenTimeDialog(false);
    setEditingTimeEntry(null);
  };

  const handleTimeSubmit = async () => {
    // Clear previous errors
    setError('');
    
    try {
      // Validate required fields
      if (!timeForm.employee_id) {
        setError('Employee is required');
        return;
      }
      
      if (!timeForm.date) {
        setError('Date is required');
        return;
      }
      
      if (!timeForm.start_time) {
        setError('Start time is required');
        return;
      }
      
      if (!timeForm.end_time) {
        setError('End time is required');
        return;
      }
      
      // Validate that end time is after start time
      if (timeForm.start_time >= timeForm.end_time) {
        setError('End time must be after start time');
        return;
      }
      
      if (editingTimeEntry) {
        await axios.put(`/api/payroll/time-entries/${editingTimeEntry.id}`, timeForm);
      } else {
        await axios.post('/api/payroll/time-entries', timeForm);
      }
      fetchData();
      handleCloseTimeDialog();
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError('Failed to save time entry');
      }
      console.error('Error saving time entry:', err);
    }
  };

  const handleDeleteTimeEntry = async (id) => {
    if (window.confirm('Are you sure you want to delete this time entry?')) {
      try {
        await axios.delete(`/api/payroll/time-entries/${id}`);
        fetchData();
      } catch (err) {
        setError('Failed to delete time entry');
        console.error('Error deleting time entry:', err);
      }
    }
  };

  // Payroll processing
  const processPayroll = async () => {
    try {
      await axios.post('/api/payroll/process');
      fetchData();
    } catch (err) {
      setError('Failed to process payroll');
      console.error('Error processing payroll:', err);
    }
  };

  const getEmployeeName = (employeeId) => {
    const employee = employees.find(emp => emp.id === employeeId);
    return employee ? `${employee.first_name} ${employee.last_name}` : 'Unknown';
  };

  const getTotalPayroll = () => {
    return payrollRecords.reduce((sum, record) => sum + parseFloat(record.gross_pay), 0);
  };

  const getActiveEmployees = () => {
    return employees.filter(emp => emp.status === 'active').length;
  };

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
          Payroll Management
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Add />}
            onClick={() => handleOpenEmployeeDialog()}
            sx={{ mr: 1 }}
          >
            Add Employee
          </Button>
          <Button
            variant="outlined"
            startIcon={<Schedule />}
            onClick={() => handleOpenTimeDialog()}
            sx={{ mr: 1 }}
          >
            Add Time Entry
          </Button>
          <Button
            variant="contained"
            startIcon={<Payment />}
            onClick={processPayroll}
          >
            Process Payroll
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Employees
              </Typography>
              <Typography variant="h4">
                {employees.length}
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
                {getActiveEmployees()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Payroll
              </Typography>
              <Typography variant="h4">
                ${getTotalPayroll().toLocaleString()}
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
                {payrollRecords.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ width: '100%' }}>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Employees" />
          <Tab label="Time Entries" />
          <Tab label="Payroll Records" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Position</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Hourly Rate</TableCell>
                  <TableCell>Hire Date</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {employees.map((employee) => (
                  <TableRow key={employee.id}>
                    <TableCell>{`${employee.first_name} ${employee.last_name}`}</TableCell>
                    <TableCell>{employee.position}</TableCell>
                    <TableCell>{employee.email}</TableCell>
                    <TableCell>${employee.hourly_rate}/hr</TableCell>
                    <TableCell>{new Date(employee.hire_date).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <Chip
                        label={employee.status}
                        color={employee.status === 'active' ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton size="small" onClick={() => handleOpenEmployeeDialog(employee)}>
                        <Edit />
                      </IconButton>
                      <IconButton size="small" onClick={() => handleDeleteEmployee(employee.id)}>
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <TableContainer>
            <Table>
                             <TableHead>
                 <TableRow>
                   <TableCell>Employee</TableCell>
                   <TableCell>Date</TableCell>
                   <TableCell>Hours</TableCell>
                   <TableCell>Notes</TableCell>
                   <TableCell>Actions</TableCell>
                 </TableRow>
               </TableHead>
              <TableBody>
                                 {timeEntries.map((entry) => (
                   <TableRow key={entry.id}>
                     <TableCell>{getEmployeeName(entry.employee_id)}</TableCell>
                     <TableCell>{new Date(entry.date).toLocaleDateString()}</TableCell>
                     <TableCell>{entry.hours_worked}</TableCell>
                     <TableCell>{entry.notes || '-'}</TableCell>
                     <TableCell>
                       <IconButton size="small" onClick={() => handleOpenTimeDialog(entry)}>
                         <Edit />
                       </IconButton>
                       <IconButton size="small" onClick={() => handleDeleteTimeEntry(entry.id)}>
                         <Delete />
                       </IconButton>
                     </TableCell>
                   </TableRow>
                 ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <TableContainer>
            <Table>
                             <TableHead>
                 <TableRow>
                   <TableCell>Employee</TableCell>
                   <TableCell>Pay Period Start</TableCell>
                   <TableCell>Hours</TableCell>
                   <TableCell>Gross Pay</TableCell>
                   <TableCell>Net Pay</TableCell>
                   <TableCell>Status</TableCell>
                 </TableRow>
               </TableHead>
              <TableBody>
                                 {payrollRecords.map((record) => (
                   <TableRow key={record.id}>
                     <TableCell>{getEmployeeName(record.employee_id)}</TableCell>
                     <TableCell>{new Date(record.pay_period_start).toLocaleDateString()}</TableCell>
                     <TableCell>{parseFloat(record.regular_hours) + parseFloat(record.overtime_hours)}</TableCell>
                     <TableCell>${parseFloat(record.gross_pay).toLocaleString()}</TableCell>
                     <TableCell>${parseFloat(record.net_pay).toLocaleString()}</TableCell>
                     <TableCell>
                       <Chip
                         label={record.status}
                         color={record.status === 'paid' ? 'success' : 'warning'}
                         size="small"
                       />
                     </TableCell>
                   </TableRow>
                 ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>
      </Paper>

      {/* Employee Dialog */}
      <Dialog open={openEmployeeDialog} onClose={handleCloseEmployeeDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingEmployee ? 'Edit Employee' : 'Add New Employee'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="First Name"
                value={employeeForm.first_name}
                onChange={(e) => setEmployeeForm(prev => ({ ...prev, first_name: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Last Name"
                value={employeeForm.last_name}
                onChange={(e) => setEmployeeForm(prev => ({ ...prev, last_name: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={employeeForm.email}
                onChange={(e) => setEmployeeForm(prev => ({ ...prev, email: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Position"
                value={employeeForm.position}
                onChange={(e) => setEmployeeForm(prev => ({ ...prev, position: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Salary"
                type="number"
                value={employeeForm.salary}
                onChange={(e) => setEmployeeForm(prev => ({ ...prev, salary: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Hourly Rate"
                type="number"
                value={employeeForm.hourly_rate}
                onChange={(e) => setEmployeeForm(prev => ({ ...prev, hourly_rate: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Hire Date"
                type="date"
                value={employeeForm.hire_date}
                onChange={(e) => setEmployeeForm(prev => ({ ...prev, hire_date: e.target.value }))}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={employeeForm.status}
                  label="Status"
                  onChange={(e) => setEmployeeForm(prev => ({ ...prev, status: e.target.value }))}
                >
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="inactive">Inactive</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseEmployeeDialog}>Cancel</Button>
          <Button onClick={handleEmployeeSubmit} variant="contained">
            {editingEmployee ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Time Entry Dialog */}
      <Dialog open={openTimeDialog} onClose={handleCloseTimeDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingTimeEntry ? 'Edit Time Entry' : 'Add Time Entry'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth required>
                <InputLabel>Employee</InputLabel>
                <Select
                  value={timeForm.employee_id}
                  label="Employee"
                  onChange={(e) => setTimeForm(prev => ({ ...prev, employee_id: e.target.value }))}
                >
                  {employees.filter(emp => emp.status === 'active').map((employee) => (
                    <MenuItem key={employee.id} value={employee.id}>
                      {employee.first_name} {employee.last_name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Date"
                type="date"
                value={timeForm.date}
                onChange={(e) => setTimeForm(prev => ({ ...prev, date: e.target.value }))}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Start Time"
                type="time"
                value={timeForm.start_time}
                onChange={(e) => setTimeForm(prev => ({ ...prev, start_time: e.target.value }))}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="End Time"
                type="time"
                value={timeForm.end_time}
                onChange={(e) => setTimeForm(prev => ({ ...prev, end_time: e.target.value }))}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Notes"
                multiline
                rows={3}
                value={timeForm.notes}
                onChange={(e) => setTimeForm(prev => ({ ...prev, notes: e.target.value }))}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseTimeDialog}>Cancel</Button>
          <Button onClick={handleTimeSubmit} variant="contained">
            {editingTimeEntry ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Payroll; 