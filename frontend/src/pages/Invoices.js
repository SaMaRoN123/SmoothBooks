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
  Chip,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Send
} from '@mui/icons-material';
import axios from '../config/axios';

const statusColors = {
  draft: 'default',
  sent: 'primary',
  paid: 'success',
  overdue: 'error',
  cancelled: 'error'
};

function Invoices() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingInvoice, setEditingInvoice] = useState(null);
  const [formData, setFormData] = useState({
    client_name: '',
    client_email: '',
    issue_date: '',
    due_date: '',
    status: 'draft',
    items: [{ description: '', quantity: 1, unit_price: 0 }],
    notes: ''
  });

  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/invoices');
      setInvoices(response.data.invoices);
    } catch (err) {
      setError('Failed to load invoices');
      console.error('Error fetching invoices:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (invoice = null) => {
    if (invoice) {
      setEditingInvoice(invoice);
      setFormData({
        client_name: invoice.client_name,
        client_email: invoice.client_email,
        issue_date: invoice.issue_date,
        due_date: invoice.due_date,
        status: invoice.status,
        items: invoice.items || [{ description: '', quantity: 1, unit_price: 0 }],
        notes: invoice.notes || ''
      });
    } else {
      setEditingInvoice(null);
      setFormData({
        client_name: '',
        client_email: '',
        issue_date: new Date().toISOString().split('T')[0],
        due_date: '',
        status: 'draft',
        items: [{ description: '', quantity: 1, unit_price: 0 }],
        notes: ''
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingInvoice(null);
    setFormData({
      client_name: '',
      client_email: '',
      issue_date: '',
      due_date: '',
      status: 'draft',
      items: [{ description: '', quantity: 1, unit_price: 0 }],
      notes: ''
    });
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleItemChange = (index, field, value) => {
    const newItems = [...formData.items];
    newItems[index] = { ...newItems[index], [field]: value };
    setFormData(prev => ({ ...prev, items: newItems }));
  };

  const addItem = () => {
    setFormData(prev => ({
      ...prev,
      items: [...prev.items, { description: '', quantity: 1, unit_price: 0 }]
    }));
  };

  const removeItem = (index) => {
    if (formData.items.length > 1) {
      const newItems = formData.items.filter((_, i) => i !== index);
      setFormData(prev => ({ ...prev, items: newItems }));
    }
  };

  const calculateTotal = () => {
    return formData.items.reduce((total, item) => {
      return total + (item.quantity * item.unit_price);
    }, 0);
  };

  const handleSubmit = async () => {
    // Clear previous errors
    setError('');
    
    try {
      // Validate required fields
      if (!formData.client_name.trim()) {
        setError('Client name is required');
        return;
      }
      
      if (!formData.issue_date) {
        setError('Issue date is required');
        return;
      }
      
      if (!formData.due_date) {
        setError('Due date is required');
        return;
      }
      
      // Validate items
      const validItems = formData.items.filter(item => 
        item.description.trim() && 
        item.quantity > 0 && 
        item.unit_price > 0
      );
      
      if (validItems.length === 0) {
        setError('At least one valid item is required');
        return;
      }
      
      const invoiceData = {
        ...formData,
        items: validItems,
        total_amount: calculateTotal()
      };

      if (editingInvoice) {
        await axios.put(`/api/invoices/${editingInvoice.id}`, invoiceData);
      } else {
        await axios.post('/api/invoices', invoiceData);
      }

      fetchInvoices();
      handleCloseDialog();
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError('Failed to save invoice');
      }
      console.error('Error saving invoice:', err);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this invoice?')) {
      try {
        await axios.delete(`/api/invoices/${id}`);
        fetchInvoices();
      } catch (err) {
        setError('Failed to delete invoice');
        console.error('Error deleting invoice:', err);
      }
    }
  };

  const handleSendInvoice = async (id) => {
    try {
      await axios.post(`/api/invoices/${id}/send`);
      fetchInvoices();
    } catch (err) {
      setError('Failed to send invoice');
      console.error('Error sending invoice:', err);
    }
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
          Invoices
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => handleOpenDialog()}
        >
          New Invoice
        </Button>
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
                Total Invoices
              </Typography>
              <Typography variant="h4">
                {invoices.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Paid
              </Typography>
              <Typography variant="h4" color="success.main">
                {invoices.filter(inv => inv.status === 'paid').length}
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
                {invoices.filter(inv => ['sent', 'overdue'].includes(inv.status)).length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Amount
              </Typography>
              <Typography variant="h4">
                ${invoices.reduce((sum, inv) => sum + parseFloat(inv.total_amount || 0), 0).toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Invoices Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Invoice #</TableCell>
              <TableCell>Client</TableCell>
              <TableCell>Issue Date</TableCell>
              <TableCell>Due Date</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {invoices.map((invoice) => (
              <TableRow key={invoice.id}>
                <TableCell>{invoice.invoice_number}</TableCell>
                <TableCell>{invoice.client_name}</TableCell>
                <TableCell>{new Date(invoice.issue_date).toLocaleDateString()}</TableCell>
                <TableCell>{new Date(invoice.due_date).toLocaleDateString()}</TableCell>
                <TableCell>${parseFloat(invoice.total_amount).toLocaleString()}</TableCell>
                <TableCell>
                  <Chip
                    label={invoice.status}
                    color={statusColors[invoice.status]}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <IconButton size="small" onClick={() => handleOpenDialog(invoice)}>
                    <Edit />
                  </IconButton>
                  <IconButton size="small" onClick={() => handleDelete(invoice.id)}>
                    <Delete />
                  </IconButton>
                  {invoice.status === 'draft' && (
                    <IconButton size="small" onClick={() => handleSendInvoice(invoice.id)}>
                      <Send />
                    </IconButton>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Create/Edit Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingInvoice ? 'Edit Invoice' : 'Create New Invoice'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                required
                label="Client Name"
                value={formData.client_name}
                onChange={(e) => handleInputChange('client_name', e.target.value)}
                error={!formData.client_name.trim()}
                helperText={!formData.client_name.trim() ? 'Client name is required' : ''}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Client Email"
                type="email"
                value={formData.client_email}
                onChange={(e) => handleInputChange('client_email', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                required
                label="Issue Date"
                type="date"
                value={formData.issue_date}
                onChange={(e) => handleInputChange('issue_date', e.target.value)}
                InputLabelProps={{ shrink: true }}
                error={!formData.issue_date}
                helperText={!formData.issue_date ? 'Issue date is required' : ''}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                required
                label="Due Date"
                type="date"
                value={formData.due_date}
                onChange={(e) => handleInputChange('due_date', e.target.value)}
                InputLabelProps={{ shrink: true }}
                error={!formData.due_date}
                helperText={!formData.due_date ? 'Due date is required' : ''}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={formData.status}
                  label="Status"
                  onChange={(e) => handleInputChange('status', e.target.value)}
                >
                  <MenuItem value="draft">Draft</MenuItem>
                  <MenuItem value="sent">Sent</MenuItem>
                  <MenuItem value="paid">Paid</MenuItem>
                  <MenuItem value="overdue">Overdue</MenuItem>
                  <MenuItem value="cancelled">Cancelled</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Invoice Items
              </Typography>
              {formData.items.map((item, index) => (
                <Box key={index} sx={{ display: 'flex', gap: 2, mb: 2 }}>
                  <TextField
                    required
                    label="Description"
                    value={item.description}
                    onChange={(e) => handleItemChange(index, 'description', e.target.value)}
                    sx={{ flexGrow: 1 }}
                    error={!item.description.trim()}
                    helperText={!item.description.trim() ? 'Description is required' : ''}
                  />
                  <TextField
                    required
                    label="Quantity"
                    type="number"
                    value={item.quantity}
                    onChange={(e) => handleItemChange(index, 'quantity', parseFloat(e.target.value) || 0)}
                    sx={{ width: 100 }}
                    error={item.quantity <= 0}
                    helperText={item.quantity <= 0 ? 'Quantity must be > 0' : ''}
                  />
                  <TextField
                    required
                    label="Unit Price"
                    type="number"
                    value={item.unit_price}
                    onChange={(e) => handleItemChange(index, 'unit_price', parseFloat(e.target.value) || 0)}
                    sx={{ width: 120 }}
                    error={item.unit_price <= 0}
                    helperText={item.unit_price <= 0 ? 'Unit price must be > 0' : ''}
                  />
                  <IconButton onClick={() => removeItem(index)} disabled={formData.items.length === 1}>
                    <Delete />
                  </IconButton>
                </Box>
              ))}
              <Button onClick={addItem} variant="outlined" size="small">
                Add Item
              </Button>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Notes"
                multiline
                rows={3}
                value={formData.notes}
                onChange={(e) => handleInputChange('notes', e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="h6" align="right">
                Total: ${calculateTotal().toLocaleString()}
              </Typography>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingInvoice ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Invoices; 