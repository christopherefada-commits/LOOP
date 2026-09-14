import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { LoopProvider } from './context/LoopContext'
import { Dashboard } from './screens/Dashboard'
import { ApprovalView } from './screens/ApprovalView'
import { ActivityTimeline } from './screens/ActivityTimeline'
import { Settings } from './screens/Settings'

export default function App() {
  return (
    <LoopProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<Dashboard filter="all" />} />
            <Route path="money" element={<Dashboard filter="money" />} />
            <Route path="deadlines" element={<Dashboard filter="deadlines" />} />
            <Route path="documents" element={<Dashboard filter="documents" />} />
            <Route path="approvals" element={<Dashboard filter="approvals" />} />
            <Route path="activity" element={<ActivityTimeline />} />
            <Route path="approval/:id" element={<ApprovalView />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </LoopProvider>
  )
}
