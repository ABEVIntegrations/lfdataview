import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { Box, CircularProgress, Typography } from '@mui/material';

export default function CallbackPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const queryClient = useQueryClient();

  useEffect(() => {
    // The backend handles the OAuth callback at /auth/callback
    // We just need to redirect the user after the backend processes it
    const error = searchParams.get('error');

    if (error) {
      // OAuth error occurred
      navigate('/login', {
        replace: true,
        state: { error: `Authentication failed: ${error}` }
      });
      return;
    }

    // Clear any cached auth state and redirect to home
    queryClient.invalidateQueries({ queryKey: ['authStatus'] });

    // Small delay to ensure backend has processed the callback
    setTimeout(() => {
      navigate('/', { replace: true });
    }, 500);
  }, [navigate, searchParams, queryClient]);

  return (
    <Box
      display="flex"
      flexDirection="column"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
    >
      <CircularProgress size={48} />
      <Typography variant="h6" sx={{ mt: 2 }}>
        Completing sign in...
      </Typography>
    </Box>
  );
}
