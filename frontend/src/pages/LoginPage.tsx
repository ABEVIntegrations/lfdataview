import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Typography,
  Alert,
} from '@mui/material';
import { Login, TableChart } from '@mui/icons-material';
import { getAuthStatus, initiateLogin } from '../services/api';

export default function LoginPage() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  // Check if already authenticated
  const { data: authStatus, isLoading } = useQuery({
    queryKey: ['authStatus'],
    queryFn: getAuthStatus,
    retry: false,
  });

  // Redirect if already authenticated
  if (authStatus?.authenticated) {
    navigate('/', { replace: true });
    return null;
  }

  const handleLogin = async () => {
    setIsLoggingIn(true);
    setError(null);

    try {
      const { redirect_url } = await initiateLogin();
      window.location.href = redirect_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
      setIsLoggingIn(false);
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      sx={{ backgroundColor: '#f5f5f5' }}
    >
      <Card sx={{ maxWidth: 400, width: '100%', mx: 2 }}>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <TableChart sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
          <Typography variant="h4" component="h1" gutterBottom>
            Laserfiche Data View
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Sign in with your Laserfiche account to view and manage table data.
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Button
            variant="contained"
            size="large"
            startIcon={isLoggingIn ? <CircularProgress size={20} color="inherit" /> : <Login />}
            onClick={handleLogin}
            disabled={isLoggingIn}
            fullWidth
          >
            {isLoggingIn ? 'Redirecting...' : 'Sign in with Laserfiche'}
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
}
