import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { SearchPage } from './pages/SearchPage';
import { PlayerProfilePage } from './pages/PlayerProfilePage';
import { TransitionSimulatorPage } from './pages/TransitionSimulatorPage';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Navigate to="/search" replace /> },
      { path: 'search', element: <SearchPage /> },
      { path: 'players/:id', element: <PlayerProfilePage /> },
      { path: 'players/:id/simulate', element: <TransitionSimulatorPage /> },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
