import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Button,
  CircularProgress,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Typography,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Snackbar,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Refresh,
  ArrowBack,
} from '@mui/icons-material';
import {
  fetchTableRows,
  createTableRow,
  updateTableRow,
  deleteTableRow,
} from '../services/api';

export default function TableDetailPage() {
  const { tableName } = useParams<{ tableName: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Pagination state
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(50);

  // Modal state
  const [createOpen, setCreateOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [selectedRow, setSelectedRow] = useState<Record<string, unknown> | null>(null);
  const [formData, setFormData] = useState<Record<string, string>>({});

  // Snackbar state
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });

  // Fetch table rows
  const {
    data: rowsResponse,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['tableRows', tableName, page, rowsPerPage],
    queryFn: () => fetchTableRows(tableName!, rowsPerPage, page * rowsPerPage),
    enabled: !!tableName,
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => createTableRow(tableName!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tableRows', tableName] });
      setCreateOpen(false);
      setFormData({});
      setSnackbar({ open: true, message: 'Row created successfully', severity: 'success' });
    },
    onError: (err) => {
      setSnackbar({ open: true, message: err instanceof Error ? err.message : 'Failed to create row', severity: 'error' });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ key, data }: { key: string; data: Record<string, unknown> }) =>
      updateTableRow(tableName!, key, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tableRows', tableName] });
      setEditOpen(false);
      setSelectedRow(null);
      setFormData({});
      setSnackbar({ open: true, message: 'Row updated successfully', severity: 'success' });
    },
    onError: (err) => {
      setSnackbar({ open: true, message: err instanceof Error ? err.message : 'Failed to update row', severity: 'error' });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (key: string) => deleteTableRow(tableName!, key),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tableRows', tableName] });
      setDeleteOpen(false);
      setSelectedRow(null);
      setSnackbar({ open: true, message: 'Row deleted successfully', severity: 'success' });
    },
    onError: (err) => {
      setSnackbar({ open: true, message: err instanceof Error ? err.message : 'Failed to delete row', severity: 'error' });
    },
  });

  // Get columns from first row
  const rows = rowsResponse?.rows || [];
  const columns = rows.length > 0 ? Object.keys(rows[0]) : [];
  const primaryKey = columns[0] || 'id'; // Assume first column is primary key

  // Handlers
  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleCreate = () => {
    setFormData({});
    setCreateOpen(true);
  };

  const handleEdit = (row: Record<string, unknown>) => {
    setSelectedRow(row);
    const data: Record<string, string> = {};
    Object.entries(row).forEach(([key, value]) => {
      data[key] = String(value ?? '');
    });
    setFormData(data);
    setEditOpen(true);
  };

  const handleDelete = (row: Record<string, unknown>) => {
    setSelectedRow(row);
    setDeleteOpen(true);
  };

  const handleFormChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleCreateSubmit = () => {
    createMutation.mutate(formData);
  };

  const handleEditSubmit = () => {
    if (selectedRow) {
      const key = String(selectedRow[primaryKey]);
      updateMutation.mutate({ key, data: formData });
    }
  };

  const handleDeleteConfirm = () => {
    if (selectedRow) {
      const key = String(selectedRow[primaryKey]);
      deleteMutation.mutate(key);
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" py={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Button startIcon={<ArrowBack />} onClick={() => navigate('/')} sx={{ mb: 2 }}>
          Back to Tables
        </Button>
        <Alert severity="error">
          {error instanceof Error ? error.message : 'Failed to load table data'}
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
        <Box display="flex" alignItems="center">
          <IconButton onClick={() => navigate('/')} sx={{ mr: 1 }}>
            <ArrowBack />
          </IconButton>
          <Typography variant="h4" component="h1">
            {tableName}
          </Typography>
        </Box>
        <Box>
          <Button startIcon={<Refresh />} onClick={() => refetch()} sx={{ mr: 1 }}>
            Refresh
          </Button>
          <Button variant="contained" startIcon={<Add />} onClick={handleCreate}>
            Add Row
          </Button>
        </Box>
      </Box>

      {/* Table */}
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              {columns.map((column) => (
                <TableCell key={column} sx={{ fontWeight: 'bold' }}>
                  {column}
                </TableCell>
              ))}
              <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.length === 0 ? (
              <TableRow>
                <TableCell colSpan={columns.length + 1} align="center">
                  No rows found
                </TableCell>
              </TableRow>
            ) : (
              rows.map((row, index) => (
                <TableRow key={index} hover>
                  {columns.map((column) => (
                    <TableCell key={column}>
                      {String(row[column] ?? '')}
                    </TableCell>
                  ))}
                  <TableCell>
                    <IconButton size="small" onClick={() => handleEdit(row)}>
                      <Edit fontSize="small" />
                    </IconButton>
                    <IconButton size="small" onClick={() => handleDelete(row)} color="error">
                      <Delete fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[10, 25, 50, 100]}
          component="div"
          count={rowsResponse?.total || 0}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>

      {/* Create Dialog */}
      <Dialog open={createOpen} onClose={() => setCreateOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Row</DialogTitle>
        <DialogContent>
          {columns.map((column) => (
            <TextField
              key={column}
              label={column}
              value={formData[column] || ''}
              onChange={(e) => handleFormChange(column, e.target.value)}
              fullWidth
              margin="normal"
              size="small"
            />
          ))}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateOpen(false)}>Cancel</Button>
          <Button
            onClick={handleCreateSubmit}
            variant="contained"
            disabled={createMutation.isPending}
          >
            {createMutation.isPending ? 'Creating...' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={editOpen} onClose={() => setEditOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Row</DialogTitle>
        <DialogContent>
          {columns.map((column) => (
            <TextField
              key={column}
              label={column}
              value={formData[column] || ''}
              onChange={(e) => handleFormChange(column, e.target.value)}
              fullWidth
              margin="normal"
              size="small"
              disabled={column === primaryKey}
            />
          ))}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditOpen(false)}>Cancel</Button>
          <Button
            onClick={handleEditSubmit}
            variant="contained"
            disabled={updateMutation.isPending}
          >
            {updateMutation.isPending ? 'Saving...' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteOpen} onClose={() => setDeleteOpen(false)}>
        <DialogTitle>Delete Row</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this row? This action cannot be undone.
          </Typography>
          {selectedRow && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
              <Typography variant="body2">
                <strong>{primaryKey}:</strong> {String(selectedRow[primaryKey])}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteOpen(false)}>Cancel</Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
            disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar((prev) => ({ ...prev, open: false }))}
      >
        <Alert
          onClose={() => setSnackbar((prev) => ({ ...prev, open: false }))}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
