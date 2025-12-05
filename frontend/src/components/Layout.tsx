import { Outlet, useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import {
  AppBar,
  Box,
  Container,
  Toolbar,
  Typography,
  Button,
  Chip,
  Link,
  Stack,
} from '@mui/material';
import { Logout } from '@mui/icons-material';
import { logout } from '../services/api';

export default function Layout() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const handleLogout = async () => {
    try {
      await logout();
      queryClient.clear();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="static">
        <Toolbar>
          <Box
            component="img"
            src="/logo-white.svg"
            alt="LF DataView"
            sx={{
              height: 28,
              cursor: 'pointer',
            }}
            onClick={() => navigate('/')}
          />
          <Chip
            label="Community Edition"
            size="small"
            sx={{
              ml: 1,
              backgroundColor: 'rgba(255, 255, 255, 0.15)',
              color: 'white',
            }}
          />
          <Box sx={{ flexGrow: 1 }} />
          <Button
            color="inherit"
            startIcon={<Logout />}
            onClick={handleLogout}
          >
            Logout
          </Button>
        </Toolbar>
      </AppBar>
      <Container component="main" sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
        <Outlet />
      </Container>
      <Box
        component="footer"
        sx={{
          py: 3,
          px: 2,
          mt: 'auto',
          backgroundColor: (theme) => theme.palette.grey[900],
          color: 'white',
        }}
      >
        <Container maxWidth="lg">
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            justifyContent="space-between"
            alignItems="center"
            spacing={2}
          >
            <Typography variant="body2" color="grey.400">
              &copy; {new Date().getFullYear()} LF DataView by{' '}
              <Link
                href="https://abevintegrations.com"
                target="_blank"
                rel="noopener"
                color="grey.400"
                underline="hover"
              >
                ABEV Integrations
              </Link>
              .
            </Typography>
            <Stack direction="row" spacing={3}>
              <Link
                href="https://github.com/ABEVIntegrations/lfdataview"
                target="_blank"
                rel="noopener"
                color="grey.400"
                underline="hover"
              >
                GitHub
              </Link>
              <Link
                href="mailto:support@lfdataview.com"
                color="grey.400"
                underline="hover"
              >
                Support
              </Link>
            </Stack>
          </Stack>
          <Typography
            variant="caption"
            color="grey.600"
            sx={{ display: 'block', mt: 2, textAlign: 'center' }}
          >
            Laserfiche is a registered trademark of Laserfiche. LF DataView is not affiliated with Laserfiche.
          </Typography>
        </Container>
      </Box>
    </Box>
  );
}
