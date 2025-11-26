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
  LinearProgress,
  RadioGroup,
  FormControlLabel,
  Radio,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Refresh,
  ArrowBack,
  Download,
  HelpOutline,
  Upload,
} from '@mui/icons-material';
import {
  fetchTableRows,
  createTableRow,
  updateTableRow,
  deleteTableRow,
  fetchTableSchema,
  replaceAllRows,
  batchCreateRows,
} from '../services/api';
import { ReplaceAllResponse, BatchCreateResponse } from '../types';

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

  // Filter state
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [helpOpen, setHelpOpen] = useState(false);

  // CSV upload state
  const [uploadOpen, setUploadOpen] = useState(false);
  const [csvData, setCsvData] = useState<Record<string, string>[]>([]);
  const [csvColumns, setCsvColumns] = useState<string[]>([]);
  const [uploadErrors, setUploadErrors] = useState<string[]>([]);
  const [uploadWarnings, setUploadWarnings] = useState<string[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadConfirmOpen, setUploadConfirmOpen] = useState(false);
  const [uploadResult, setUploadResult] = useState<ReplaceAllResponse | BatchCreateResponse | null>(null);
  const [resultOpen, setResultOpen] = useState(false);
  const [uploadMode, setUploadMode] = useState<'append' | 'replace'>('append');

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

  // Get columns from first row, with _key always first
  const rows = rowsResponse?.rows || [];
  const primaryKey = '_key';
  const columns = rows.length > 0
    ? [primaryKey, ...Object.keys(rows[0]).filter(col => col !== primaryKey)]
    : [];

  // Filter rows based on filter values
  // Supports wildcards: * for any characters
  // Examples: "2" = exact, "*2*" = contains, "2*" = starts with, "*2" = ends with
  const filteredRows = rows.filter((row) => {
    return Object.entries(filters).every(([column, filterValue]) => {
      if (!filterValue) return true;
      const cellValue = String(row[column] ?? '').toLowerCase();
      const filter = filterValue.toLowerCase();

      // Check for wildcard patterns
      if (filter.includes('*')) {
        // Convert wildcard pattern to regex
        const regexPattern = filter
          .replace(/[.+?^${}()|[\]\\]/g, '\\$&') // Escape special regex chars except *
          .replace(/\*/g, '.*'); // Convert * to .*
        const regex = new RegExp(`^${regexPattern}$`);
        return regex.test(cellValue);
      }

      // Default: exact match
      return cellValue === filter;
    });
  });

  // Handle filter change
  const handleFilterChange = (column: string, value: string) => {
    setFilters((prev) => ({ ...prev, [column]: value }));
  };

  // Download CSV (excludes _key for Laserfiche compatibility)
  const handleDownloadCsv = () => {
    if (filteredRows.length === 0) return;

    // Exclude _key column from download
    const downloadColumns = columns.filter(col => col !== '_key');

    const csvContent = [
      // Header row
      downloadColumns.join(','),
      // Data rows
      ...filteredRows.map((row) =>
        downloadColumns
          .map((col) => {
            const value = String(row[col] ?? '');
            // Escape quotes and wrap in quotes if contains comma or quote
            if (value.includes(',') || value.includes('"') || value.includes('\n')) {
              return `"${value.replace(/"/g, '""')}"`;
            }
            return value;
          })
          .join(',')
      ),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${tableName}_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    URL.revokeObjectURL(link.href);
  };

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

  // CSV parsing function
  const parseCSV = (text: string): { columns: string[]; rows: Record<string, string>[] } => {
    const lines = text.trim().split('\n');
    if (lines.length === 0) return { columns: [], rows: [] };

    // Parse header
    const columns = lines[0].split(',').map(col => col.trim().replace(/^"|"$/g, ''));

    // Parse rows
    const rows: Record<string, string>[] = [];
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(val => val.trim().replace(/^"|"$/g, ''));
      const row: Record<string, string> = {};
      columns.forEach((col, idx) => {
        row[col] = values[idx] || '';
      });
      rows.push(row);
    }

    return { columns, rows };
  };

  // Validate CSV against table schema
  const validateCSV = async (csvColumns: string[], csvRows: Record<string, string>[]): Promise<{ errors: string[]; warnings: string[] }> => {
    const errors: string[] = [];
    const warnings: string[] = [];

    try {
      const schema = await fetchTableSchema(tableName!);
      const tableColumns = schema.columns.map(c => c.name);

      // Check for _key column (will be stripped automatically)
      if (csvColumns.includes('_key')) {
        warnings.push('Note: "_key" column will be ignored (auto-generated by Laserfiche)');
      }

      // Check for unknown columns
      const unknownCols = csvColumns.filter(col => col !== '_key' && !tableColumns.includes(col));
      if (unknownCols.length > 0) {
        errors.push(`Unknown columns: ${unknownCols.join(', ')}`);
      }

      // Check for empty rows
      if (csvRows.length === 0) {
        errors.push('CSV file is empty (no data rows)');
      }

    } catch (err) {
      errors.push(`Failed to fetch table schema: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }

    return { errors, warnings };
  };

  // Handle file selection
  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Reset state
    setCsvData([]);
    setCsvColumns([]);
    setUploadErrors([]);
    setUploadWarnings([]);

    const reader = new FileReader();
    reader.onload = async (e) => {
      const text = e.target?.result as string;
      const { columns, rows } = parseCSV(text);

      setCsvColumns(columns);
      setCsvData(rows);

      // Validate
      const { errors, warnings } = await validateCSV(columns, rows);
      setUploadErrors(errors);
      setUploadWarnings(warnings);

      // Open dialog
      setUploadOpen(true);
    };
    reader.readAsText(file);

    // Reset input so same file can be selected again
    event.target.value = '';
  };

  // Show upload confirmation dialog
  const handleShowUploadConfirm = () => {
    setUploadOpen(false);
    setUploadConfirmOpen(true);
  };

  // Handle upload execution (append or replace)
  const handleUploadConfirm = async () => {
    if (csvData.length === 0) return;

    setUploadConfirmOpen(false);
    setIsUploading(true);
    setUploadOpen(true);

    try {
      // Strip _key from rows before uploading (it's auto-generated)
      const rowsToUpload = csvData.map(row => {
        const { _key, ...rest } = row;
        return rest;
      });

      if (uploadMode === 'append') {
        const result = await batchCreateRows(tableName!, rowsToUpload);
        setUploadResult(result);
        setUploadOpen(false);
        setResultOpen(true);

        // Refresh table data
        queryClient.invalidateQueries({ queryKey: ['tableRows', tableName] });

        if (result.failed === 0) {
          setSnackbar({ open: true, message: `Successfully added ${result.succeeded} rows`, severity: 'success' });
        } else {
          setSnackbar({ open: true, message: `Added ${result.succeeded} rows, ${result.failed} failed`, severity: 'error' });
        }
      } else {
        const result = await replaceAllRows(tableName!, rowsToUpload);
        setUploadResult(result);
        setUploadOpen(false);
        setResultOpen(true);

        // Refresh table data
        queryClient.invalidateQueries({ queryKey: ['tableRows', tableName] });

        if (result.success) {
          setSnackbar({ open: true, message: `Successfully replaced table with ${result.rows_replaced} rows`, severity: 'success' });
        } else {
          setSnackbar({ open: true, message: result.error || 'Replace operation failed', severity: 'error' });
        }
      }
    } catch (err) {
      setSnackbar({ open: true, message: err instanceof Error ? err.message : 'Upload failed', severity: 'error' });
    } finally {
      setIsUploading(false);
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
          <IconButton onClick={() => setHelpOpen(true)} sx={{ ml: 1 }} size="small" color="primary">
            <HelpOutline />
          </IconButton>
        </Box>
        <Box>
          <Button startIcon={<Refresh />} onClick={() => refetch()} sx={{ mr: 1 }}>
            Refresh
          </Button>
          <Button startIcon={<Download />} onClick={handleDownloadCsv} sx={{ mr: 1 }} disabled={filteredRows.length === 0}>
            Download CSV
          </Button>
          <Button
            component="label"
            startIcon={<Upload />}
            sx={{ mr: 1 }}
          >
            Upload CSV
            <input
              type="file"
              accept=".csv"
              hidden
              onChange={handleFileSelect}
            />
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
            <TableRow>
              {columns.map((column) => (
                <TableCell key={`filter-${column}`} sx={{ p: 1 }}>
                  {column !== primaryKey && (
                    <TextField
                      size="small"
                      placeholder={`Use * for wildcard`}
                      value={filters[column] || ''}
                      onChange={(e) => handleFilterChange(column, e.target.value)}
                      fullWidth
                      variant="outlined"
                      sx={{ '& .MuiInputBase-input': { py: 0.5, fontSize: '0.875rem' } }}
                    />
                  )}
                </TableCell>
              ))}
              <TableCell />
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredRows.length === 0 ? (
              <TableRow>
                <TableCell colSpan={columns.length + 1} align="center">
                  {rows.length === 0 ? 'No rows found' : 'No rows match the filter'}
                </TableCell>
              </TableRow>
            ) : (
              filteredRows.map((row, index) => (
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
          count={rowsResponse?.total === -1 ? -1 : (rowsResponse?.total || 0)}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          slotProps={{
            actions: {
              nextButton: {
                disabled: rows.length < rowsPerPage,
              },
            },
          }}
        />
      </TableContainer>

      {/* Create Dialog */}
      <Dialog open={createOpen} onClose={() => setCreateOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Row</DialogTitle>
        <DialogContent>
          {columns.filter(col => col !== primaryKey).map((column) => (
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
      <Dialog open={deleteOpen} onClose={() => setDeleteOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Delete Row</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this row? This action cannot be undone.
          </Typography>
          {selectedRow && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1, maxHeight: 300, overflow: 'auto' }}>
              {columns.map((column) => (
                <Typography key={column} variant="body2" sx={{ mb: 0.5 }}>
                  <strong>{column}:</strong> {String(selectedRow[column] ?? '')}
                </Typography>
              ))}
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

      {/* Help Dialog */}
      <Dialog open={helpOpen} onClose={() => setHelpOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>How to Use Filters</DialogTitle>
        <DialogContent>
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', mt: 1 }}>
            Exact Match (Default)
          </Typography>
          <Typography variant="body2" paragraph>
            Type a value to find exact matches. For example, typing <code>2</code> will only match "2", not "12" or "102".
          </Typography>

          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
            Wildcard Matching
          </Typography>
          <Typography variant="body2" paragraph>
            Use <code>*</code> as a wildcard to match any characters:
          </Typography>
          <Box component="ul" sx={{ pl: 2, mt: 0 }}>
            <Typography component="li" variant="body2"><code>*2*</code> — contains "2" (matches "2", "12", "102")</Typography>
            <Typography component="li" variant="body2"><code>2*</code> — starts with "2" (matches "2", "20", "200")</Typography>
            <Typography component="li" variant="body2"><code>*2</code> — ends with "2" (matches "2", "12", "102")</Typography>
            <Typography component="li" variant="body2"><code>test*value</code> — starts with "test" and ends with "value"</Typography>
          </Box>

          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', mt: 2 }}>
            Additional Notes
          </Typography>
          <Box component="ul" sx={{ pl: 2, mt: 0 }}>
            <Typography component="li" variant="body2">Filters are case-insensitive</Typography>
            <Typography component="li" variant="body2">Multiple column filters use AND logic</Typography>
            <Typography component="li" variant="body2">CSV export includes only filtered rows</Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setHelpOpen(false)} variant="contained">
            Got it
          </Button>
        </DialogActions>
      </Dialog>

      {/* Upload Preview Dialog */}
      <Dialog open={uploadOpen} onClose={() => !isUploading && setUploadOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Upload CSV - Preview</DialogTitle>
        <DialogContent>
          {uploadErrors.length > 0 && (
            <Alert severity="error" sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>Validation Errors:</Typography>
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                {uploadErrors.map((err, idx) => (
                  <li key={idx}>{err}</li>
                ))}
              </ul>
            </Alert>
          )}

          {uploadWarnings.length > 0 && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              {uploadWarnings.map((warn, idx) => (
                <Typography key={idx} variant="body2">{warn}</Typography>
              ))}
            </Alert>
          )}

          <Typography variant="body2" sx={{ mb: 2 }}>
            <strong>Columns:</strong> {csvColumns.filter(c => c !== '_key').join(', ')}
          </Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            <strong>Rows to upload:</strong> {csvData.length}
          </Typography>

          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>Upload Mode:</Typography>
            <RadioGroup
              row
              value={uploadMode}
              onChange={(e) => setUploadMode(e.target.value as 'append' | 'replace')}
            >
              <FormControlLabel
                value="append"
                control={<Radio />}
                label="Append rows (add to existing data)"
              />
              <FormControlLabel
                value="replace"
                control={<Radio />}
                label="Replace all (delete existing & insert new)"
              />
            </RadioGroup>
          </Box>

          {csvData.length > 0 && (
            <Box sx={{ maxHeight: 300, overflow: 'auto', border: 1, borderColor: 'divider', borderRadius: 1 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    {csvColumns.map((col) => (
                      <TableCell key={col} sx={{ fontWeight: 'bold' }}>{col}</TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {csvData.slice(0, 5).map((row, idx) => (
                    <TableRow key={idx}>
                      {csvColumns.map((col) => (
                        <TableCell key={col}>{row[col]}</TableCell>
                      ))}
                    </TableRow>
                  ))}
                  {csvData.length > 5 && (
                    <TableRow>
                      <TableCell colSpan={csvColumns.length} align="center" sx={{ fontStyle: 'italic' }}>
                        ... and {csvData.length - 5} more rows
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </Box>
          )}

          {isUploading && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress />
              <Typography variant="body2" align="center" sx={{ mt: 1 }}>
                Uploading rows...
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadOpen(false)} disabled={isUploading}>
            Cancel
          </Button>
          <Button
            onClick={handleShowUploadConfirm}
            variant="contained"
            color={uploadMode === 'replace' ? 'warning' : 'primary'}
            disabled={isUploading || uploadErrors.length > 0 || csvData.length === 0}
          >
            {isUploading
              ? 'Uploading...'
              : uploadMode === 'append'
                ? `Add ${csvData.length} Rows`
                : `Replace Table with ${csvData.length} Rows`}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Upload Confirmation Dialog */}
      <Dialog open={uploadConfirmOpen} onClose={() => setUploadConfirmOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {uploadMode === 'append' ? 'Confirm Add Rows' : 'Confirm Replace All Rows'}
        </DialogTitle>
        <DialogContent>
          {uploadMode === 'replace' ? (
            <>
              <Alert severity="warning" sx={{ mb: 2 }}>
                <Typography variant="body1" fontWeight="bold">
                  This will DELETE ALL existing rows in the table!
                </Typography>
              </Alert>
              <Typography variant="body2" paragraph>
                You are about to replace all data in <strong>{tableName}</strong> with {csvData.length} rows from your CSV file.
              </Typography>
              <Typography variant="body2" paragraph>
                This operation:
              </Typography>
              <Box component="ul" sx={{ pl: 2, mt: 0 }}>
                <Typography component="li" variant="body2">Deletes all existing rows in the table</Typography>
                <Typography component="li" variant="body2">Inserts {csvData.length} new rows from your CSV</Typography>
                <Typography component="li" variant="body2">Cannot be undone</Typography>
              </Box>
            </>
          ) : (
            <>
              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="body1">
                  Adding {csvData.length} new rows to the table
                </Typography>
              </Alert>
              <Typography variant="body2" paragraph>
                You are about to add {csvData.length} new rows to <strong>{tableName}</strong> from your CSV file.
              </Typography>
              <Typography variant="body2" paragraph>
                Existing data will not be modified.
              </Typography>
            </>
          )}
          <Typography variant="body2" sx={{ mt: 2 }}>
            Are you sure you want to continue?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadConfirmOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleUploadConfirm}
            variant="contained"
            color={uploadMode === 'replace' ? 'error' : 'primary'}
          >
            {uploadMode === 'append' ? `Yes, Add ${csvData.length} Rows` : 'Yes, Replace All Rows'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Upload Results Dialog */}
      <Dialog open={resultOpen} onClose={() => setResultOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Results</DialogTitle>
        <DialogContent>
          {uploadResult && (
            <>
              {'success' in uploadResult ? (
                // ReplaceAllResponse
                uploadResult.success ? (
                  <Alert severity="success" sx={{ mb: 2 }}>
                    Successfully replaced table with {uploadResult.rows_replaced} rows
                  </Alert>
                ) : (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {uploadResult.error || 'Replace operation failed'}
                  </Alert>
                )
              ) : (
                // BatchCreateResponse
                <>
                  {uploadResult.failed === 0 ? (
                    <Alert severity="success" sx={{ mb: 2 }}>
                      Successfully added {uploadResult.succeeded} rows
                    </Alert>
                  ) : (
                    <Alert severity="warning" sx={{ mb: 2 }}>
                      Added {uploadResult.succeeded} of {uploadResult.total} rows ({uploadResult.failed} failed)
                    </Alert>
                  )}
                  {uploadResult.failed > 0 && uploadResult.results && (
                    <Box sx={{ mt: 2, maxHeight: 200, overflow: 'auto' }}>
                      <Typography variant="subtitle2" gutterBottom>Failed rows:</Typography>
                      {uploadResult.results
                        .filter(r => !r.success)
                        .map((r, idx) => (
                          <Typography key={idx} variant="body2" color="error">
                            Row {r.index + 1}: {r.error}
                          </Typography>
                        ))}
                    </Box>
                  )}
                </>
              )}
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResultOpen(false)} variant="contained">
            Close
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
