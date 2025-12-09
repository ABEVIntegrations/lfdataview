import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
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
  LinearProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  Refresh,
  ArrowBack,
  Download,
  HelpOutline,
  Search,
  Clear,
} from '@mui/icons-material';
import {
  fetchTableRows,
  fetchTableRowCount,
} from '../services/api';

export default function TableDetailPage() {
  const { tableName } = useParams<{ tableName: string }>();
  const navigate = useNavigate();

  // Pagination state
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(50);

  // Client-side column filters (local filtering only, no API call)
  const [columnFilters, setColumnFilters] = useState<Record<string, string>>({});
  const [helpOpen, setHelpOpen] = useState(false);

  // Server-side search state (triggers API calls)
  const [serverFilters, setServerFilters] = useState<Record<string, string>>({});
  const [debouncedServerFilters, setDebouncedServerFilters] = useState<Record<string, string>>({});
  const [serverFilterMode, setServerFilterMode] = useState<'and' | 'or'>('and');

  // Search bar UI state
  const [searchColumn, setSearchColumn] = useState<string>('');
  const [searchValue, setSearchValue] = useState('');

  // Debounce server filter changes (500ms delay) - only for server-side search
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedServerFilters(serverFilters);
      setPage(0); // Reset to first page when server filters change
    }, 500);
    return () => clearTimeout(timer);
  }, [serverFilters]);

  // Fetch table rows with server-side filtering (search bar only)
  const {
    data: rowsResponse,
    isLoading,
    isFetching,
    error,
    refetch,
  } = useQuery({
    queryKey: ['tableRows', tableName, page, rowsPerPage, debouncedServerFilters, serverFilterMode],
    queryFn: () => fetchTableRows(tableName!, rowsPerPage, page * rowsPerPage, debouncedServerFilters, serverFilterMode),
    enabled: !!tableName,
  });

  // Fetch total row count for the table (separate from paginated rows)
  const { data: countResponse } = useQuery({
    queryKey: ['tableRowCount', tableName],
    queryFn: () => fetchTableRowCount(tableName!),
    enabled: !!tableName,
    staleTime: 30000, // Cache for 30 seconds
  });

  // Get columns from first row, with _key always first (for internal use)
  const apiRows = rowsResponse?.rows || [];
  const primaryKey = '_key';
  const columns = apiRows.length > 0
    ? [primaryKey, ...Object.keys(apiRows[0]).filter(col => col !== primaryKey)]
    : [];
  // Display columns exclude _key (internal system field not meaningful to users)
  const displayColumns = columns.filter(col => col !== primaryKey);

  // Client-side filtering: filter apiRows based on columnFilters (partial match, case-insensitive)
  const rows = useMemo(() => {
    // If no column filters active, return all rows
    const hasActiveFilters = Object.values(columnFilters).some(v => v && v.trim());
    if (!hasActiveFilters) {
      return apiRows;
    }

    return apiRows.filter(row => {
      return Object.entries(columnFilters).every(([column, filterValue]) => {
        if (!filterValue || !filterValue.trim()) return true;
        const cellValue = String(row[column] ?? '').toLowerCase();
        return cellValue.includes(filterValue.toLowerCase().trim());
      });
    });
  }, [apiRows, columnFilters]);

  // Handle column filter change (client-side only, no API call)
  const handleColumnFilterChange = (column: string, value: string) => {
    setColumnFilters((prev) => ({ ...prev, [column]: value }));
  };

  // Handle search (triggers server-side API call)
  const handleSearch = () => {
    if (!searchValue.trim()) return;

    // Clear client-side column filters when doing a new search
    setColumnFilters({});

    if (searchColumn) {
      // Search specific column - use AND mode (single filter anyway)
      setServerFilterMode('and');
      setServerFilters({ [searchColumn]: searchValue.trim() });
    } else {
      // Search all columns - create filter for each column with same value (OR mode)
      setServerFilterMode('or');
      const allColumnFilters: Record<string, string> = {};
      displayColumns.forEach((col) => {
        allColumnFilters[col] = searchValue.trim();
      });
      setServerFilters(allColumnFilters);
    }
  };

  // Clear search and all filters (both client-side and server-side)
  const handleClearSearch = () => {
    setSearchColumn('');
    setSearchValue('');
    setServerFilters({});
    setServerFilterMode('and');
    setColumnFilters({});
  };

  // Download CSV (excludes _key for Laserfiche compatibility)
  // Note: Downloads only the current page of filtered results
  const handleDownloadCsv = () => {
    if (rows.length === 0) return;

    // Exclude _key column from download
    const downloadColumns = columns.filter(col => col !== '_key');

    const csvContent = [
      // Header row
      downloadColumns.join(','),
      // Data rows
      ...rows.map((row) =>
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
          <Box>
            <Typography variant="h4" component="h1">
              {tableName}
            </Typography>
            {countResponse?.row_count !== undefined && (
              <Typography variant="body2" color="text.secondary">
                {countResponse.row_count.toLocaleString()} total rows
              </Typography>
            )}
          </Box>
          <IconButton onClick={() => setHelpOpen(true)} sx={{ ml: 1 }} size="small" color="primary">
            <HelpOutline />
          </IconButton>
        </Box>
        <Box>
          <Button startIcon={<Refresh />} onClick={() => refetch()} sx={{ mr: 1 }}>
            Refresh
          </Button>
          <Button startIcon={<Download />} onClick={handleDownloadCsv} disabled={rows.length === 0}>
            Download CSV
          </Button>
        </Box>
      </Box>

      {/* Loading indicator for filtering */}
      {isFetching && !isLoading && <LinearProgress sx={{ mb: 1 }} />}

      {/* Search Bar */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box display="flex" alignItems="center" gap={2} flexWrap="wrap">
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Column</InputLabel>
            <Select
              value={searchColumn}
              label="Column"
              onChange={(e) => setSearchColumn(e.target.value)}
            >
              <MenuItem value="">
                <em>All Columns</em>
              </MenuItem>
              {displayColumns.map((col) => (
                <MenuItem key={col} value={col}>
                  {col}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            size="small"
            placeholder="Search value..."
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            sx={{ minWidth: 250 }}
          />
          <Button
            variant="contained"
            startIcon={<Search />}
            onClick={handleSearch}
            disabled={!searchValue.trim()}
          >
            Search
          </Button>
          <Button
            variant="outlined"
            startIcon={<Clear />}
            onClick={handleClearSearch}
            disabled={Object.keys(serverFilters).length === 0 && Object.keys(columnFilters).every(k => !columnFilters[k]) && !searchValue && !searchColumn}
          >
            Clear
          </Button>
        </Box>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
          Exact match search (case-insensitive). Use per-column filters below for partial/wildcard matching on displayed rows.
        </Typography>
      </Paper>

      {/* Table */}
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              {displayColumns.map((column) => (
                <TableCell key={column} sx={{ fontWeight: 'bold' }}>
                  {column}
                </TableCell>
              ))}
            </TableRow>
            <TableRow>
              {displayColumns.map((column) => (
                <TableCell key={`filter-${column}`} sx={{ p: 1 }}>
                  <TextField
                    size="small"
                    placeholder="Filter..."
                    value={columnFilters[column] || ''}
                    onChange={(e) => handleColumnFilterChange(column, e.target.value)}
                    fullWidth
                    variant="outlined"
                    sx={{ '& .MuiInputBase-input': { py: 0.5, fontSize: '0.875rem' } }}
                  />
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.length === 0 ? (
              <TableRow>
                <TableCell colSpan={displayColumns.length} align="center">
                  No rows found
                </TableCell>
              </TableRow>
            ) : (
              rows.map((row, index) => (
                <TableRow key={index} hover>
                  {displayColumns.map((column) => (
                    <TableCell key={column}>
                      {String(row[column] ?? '')}
                    </TableCell>
                  ))}
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

      {/* Help Dialog */}
      <Dialog open={helpOpen} onClose={() => setHelpOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>How to Use Search & Filters</DialogTitle>
        <DialogContent>
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', mt: 1 }}>
            Search Bar (Server-Side)
          </Typography>
          <Typography variant="body2" paragraph>
            Use the search bar above for exact match searches. This queries Laserfiche directly and is best for finding specific records. Select a column or search all columns at once.
          </Typography>

          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', mt: 2 }}>
            Column Filters (Client-Side)
          </Typography>
          <Typography variant="body2" paragraph>
            The filter fields below each column header filter the currently displayed rows. These support partial matching - typing <code>smith</code> will match "Smith", "Smithson", "Blacksmith", etc.
          </Typography>

          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', mt: 2 }}>
            Notes
          </Typography>
          <Box component="ul" sx={{ pl: 2, mt: 0 }}>
            <Typography component="li" variant="body2">Both filters are case-insensitive</Typography>
            <Typography component="li" variant="body2">Column filters use AND logic (all must match)</Typography>
            <Typography component="li" variant="body2">Column filters only work on currently loaded rows</Typography>
            <Typography component="li" variant="body2">CSV export includes only the current filtered results</Typography>
          </Box>

          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>LFDataView Community Edition</strong> is read-only. For write capabilities (add, edit, delete rows), check out <strong>LFDataView Managed</strong>.
            </Typography>
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setHelpOpen(false)} variant="contained">
            Got it
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
