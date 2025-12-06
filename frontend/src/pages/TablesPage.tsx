import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardActionArea,
  CardContent,
  CircularProgress,
  Grid,
  Typography,
  Alert,
  Skeleton,
} from '@mui/material';
import { TableChart, Refresh } from '@mui/icons-material';
import { fetchTables, fetchTableRowCount } from '../services/api';
import { TableInfo } from '../types';

// Separate component for each table card to enable lazy row count loading
function TableCard({ table }: { table: TableInfo }) {
  const navigate = useNavigate();

  // Fetch row count lazily for this specific table
  const { data: countResponse, isLoading: countLoading } = useQuery({
    queryKey: ['tableRowCount', table.name],
    queryFn: () => fetchTableRowCount(table.name),
    staleTime: 60000, // Cache for 1 minute
  });

  return (
    <Card>
      <CardActionArea onClick={() => navigate(`/tables/${table.name}`)}>
        <CardContent>
          <Box display="flex" alignItems="center" mb={1}>
            <TableChart color="primary" sx={{ mr: 1 }} />
            <Typography variant="h6" component="h2">
              {table.displayName || table.name}
            </Typography>
          </Box>
          {table.description && (
            <Typography variant="body2" color="text.secondary">
              {table.description}
            </Typography>
          )}
          <Box display="flex" justifyContent="space-between" alignItems="center" mt={1}>
            <Typography variant="caption" color="text.secondary">
              {table.name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {countLoading ? (
                <Skeleton width={50} />
              ) : (
                `${countResponse?.row_count ?? '?'} rows`
              )}
            </Typography>
          </Box>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}

export default function TablesPage() {
  const {
    data: tablesResponse,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['tables'],
    queryFn: fetchTables,
  });

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
        <Alert
          severity="error"
          action={
            <Box
              component="span"
              sx={{ cursor: 'pointer' }}
              onClick={() => refetch()}
            >
              <Refresh />
            </Box>
          }
        >
          {error instanceof Error ? error.message : 'Failed to load tables'}
        </Alert>
      </Box>
    );
  }

  const tables = tablesResponse?.tables || [];

  if (tables.length === 0) {
    return (
      <Box textAlign="center" py={4}>
        <TableChart sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h5" gutterBottom>
          No Tables Found
        </Typography>
        <Typography variant="body1" color="text.secondary">
          No lookup tables are available in your Laserfiche account.
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Tables
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Select a table to view and manage its data.
      </Typography>

      <Grid container spacing={3}>
        {tables.map((table) => (
          <Grid item xs={12} sm={6} md={4} key={table.name}>
            <TableCard table={table} />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
