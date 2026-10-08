// Routes: the level list at "/", and each level at "/levels/:levelId".

import { createBrowserRouter, RouterProvider, useParams } from 'react-router'
import { api } from './api/client'
import { LevelPlay } from './pages/LevelPlay'
import { LevelSelect } from './pages/LevelSelect'

function LevelRoute() {
  const levelId = Number(useParams().levelId)
  // key: a different level gets a fresh page, not the previous level's state.
  return <LevelPlay key={levelId} levelId={levelId} api={api} />
}

const router = createBrowserRouter([
  { path: '/', element: <LevelSelect api={api} /> },
  { path: '/levels/:levelId', element: <LevelRoute /> },
])

export default function App() {
  return <RouterProvider router={router} />
}
