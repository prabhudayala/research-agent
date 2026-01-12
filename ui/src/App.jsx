import { useState, useEffect } from 'react'
import axios from 'axios'
import './index.css'

// --- AUTH HOOK / HELPERS ---
const setToken = (token) => localStorage.setItem('token', token)
const getToken = () => localStorage.getItem('token')
const logout = () => {
    localStorage.removeItem('token')
    window.location.reload()
}

// Axios interceptor to add token
axios.interceptors.request.use(config => {
    const token = getToken()
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// --- COMPONENTS ---

const MarkdownView = ({ content }) => {
    if (!content) return null
    return (
        <div className="prose lg:prose-xl text-left mx-auto">
            {content.split('\n').map((line, i) => {
                if (line.startsWith('# ')) return <h1 key={i} className="text-2xl font-bold mt-4 mb-2">{line.replace('# ', '')}</h1>
                if (line.startsWith('## ')) return <h2 key={i} className="text-xl font-bold mt-3 mb-2">{line.replace('## ', '')}</h2>
                if (line.startsWith('### ')) return <h3 key={i} className="text-lg font-bold mt-2 mb-1">{line.replace('### ', '')}</h3>
                if (line.startsWith('- ')) return <li key={i} className="ml-4">{line.replace('- ', '')}</li>
                return <p key={i} className="mb-2">{line}</p>
            })}
        </div>
    )
}

const AuthScreen = ({ onLogin }) => {
    const [isRegister, setIsRegister] = useState(false)
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError('')
        try {
            if (isRegister) {
                await axios.post('/register', { username, password })
                // Auto login after register
                const formData = new FormData()
                formData.append('username', username)
                formData.append('password', password)
                const res = await axios.post('/token', formData)
                setToken(res.data.access_token)
                onLogin()
            } else {
                const formData = new FormData()
                formData.append('username', username)
                formData.append('password', password)
                const res = await axios.post('/token', formData)
                setToken(res.data.access_token)
                onLogin()
            }
        } catch (err) {
            console.error(err)
            setError(err.response?.data?.detail || 'Authentication failed')
        }
    }

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
            <div className="bg-white p-8 rounded-lg shadow-md w-96">
                <h2 className="text-2xl font-bold mb-6 text-center">{isRegister ? 'Sign Up' : 'Login'}</h2>
                {error && <p className="text-red-500 mb-4 text-sm">{error}</p>}
                <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                    <input
                        className="p-2 border rounded"
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={e => setUsername(e.target.value)}
                    />
                    <input
                        className="p-2 border rounded"
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                    />
                    <button className="bg-blue-600 text-white p-2 rounded hover:bg-blue-700" type="submit">
                        {isRegister ? 'Create Account' : 'Login'}
                    </button>
                </form>
                <p className="mt-4 text-sm text-center">
                    {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
                    <span
                        className="text-blue-500 cursor-pointer"
                        onClick={() => setIsRegister(!isRegister)}
                    >
                        {isRegister ? 'Login' : 'Sign Up'}
                    </span>
                </p>
            </div>
        </div>
    )
}

const HistoryView = ({ onViewReport, onBack }) => {
    const [history, setHistory] = useState([])

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const res = await axios.get('/history')
                setHistory(res.data)
            } catch (err) {
                console.error(err)
            }
        }
        fetchHistory()
    }, [])

    return (
        <div className="p-8">
            <button onClick={onBack} className="mb-4 text-blue-500 hover:underline">&larr; Back to Research</button>
            <h2 className="text-3xl font-bold mb-6">Your Research History</h2>
            <div className="grid gap-4">
                {history.map(report => (
                    <div key={report.report_id} className="bg-white p-4 rounded shadow flex justify-between items-center">
                        <div>
                            <h3 className="font-bold text-lg">{report.topic}</h3>
                            <span className={`text-sm px-2 py-1 rounded ${report.status === 'completed' ? 'bg-green-100 text-green-800' :
                                    report.status === 'processing' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100'
                                }`}>
                                {report.status}
                            </span>
                        </div>
                        <button
                            onClick={() => onViewReport(report)}
                            className="bg-blue-100 text-blue-700 px-4 py-2 rounded hover:bg-blue-200"
                        >
                            View
                        </button>
                    </div>
                ))}
                {history.length === 0 && <p>No history found.</p>}
            </div>
        </div>
    )
}

const ResearchView = ({ onShowHistory }) => {
    const [topic, setTopic] = useState('')
    const [reportId, setReportId] = useState(null)
    const [status, setStatus] = useState(null)
    const [reportData, setReportData] = useState(null)
    const [loading, setLoading] = useState(false)

    const startResearch = async () => {
        if (!topic) return
        setLoading(true)
        setReportData(null)
        setStatus('starting')
        try {
            const res = await axios.post('/research', { topic })
            setReportId(res.data.report_id)
            setStatus('processing')
        } catch (err) {
            console.error(err)
            if (err.response?.status === 401) logout()
            setStatus('error')
            setLoading(false)
        }
    }

    useEffect(() => {
        let interval
        if (reportId && status === 'processing') {
            interval = setInterval(async () => {
                try {
                    const res = await axios.get(`/research/${reportId}`)
                    if (res.data.status === 'completed') {
                        setStatus('completed')
                        setReportData(res.data.data)
                        setLoading(false)
                        clearInterval(interval)
                    } else if (res.data.status === 'failed') {
                        setStatus('failed')
                        setLoading(false)
                        clearInterval(interval)
                    }
                } catch (err) {
                    console.error(err)
                    if (err.response?.status === 401) logout()
                }
            }, 2000)
        }
        return () => clearInterval(interval)
    }, [reportId, status])

    return (
        <div className="max-w-4xl mx-auto bg-white shadow-lg rounded-lg p-8 mt-10">
            <div className="flex justify-between items-center mb-8">
                <h2 className="text-2xl font-bold">New Research</h2>
                <button onClick={onShowHistory} className="text-blue-600 font-semibold hover:underline">
                    View History
                </button>
            </div>

            {!reportData && (
                <div className="mb-8">
                    <input
                        type="text"
                        placeholder="Enter a research topic..."
                        className="w-full p-4 border border-gray-300 rounded-lg text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        disabled={loading}
                    />
                    <button
                        onClick={startResearch}
                        disabled={loading || !topic}
                        className={`mt-4 w-full py-3 rounded-lg text-white font-bold text-lg transition-colors ${loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
                            }`}
                    >
                        {loading ? 'Agents are working...' : 'Start Research'}
                    </button>
                </div>
            )}

            {status === 'processing' && (
                <div className="flex flex-col items-center justify-center py-10">
                    <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mb-4"></div>
                    <p className="text-gray-600 animate-pulse">Researching, Drafting, Reviewing...</p>
                </div>
            )}

            {reportData && (
                <div className="text-left animate-fade-in">
                    <h2 className="text-3xl font-bold mb-6 border-b pb-4">{reportData.topic}</h2>
                    {reportData.sections.map((section, idx) => (
                        <div key={idx} className="mb-8">
                            <h3 className="text-2xl font-semibold text-gray-800 mb-3">{section.title}</h3>
                            <div className="bg-gray-50 p-6 rounded-lg border border-gray-200 text-gray-700 leading-relaxed whitespace-pre-wrap">
                                {section.content}
                            </div>
                        </div>
                    ))}
                    <button
                        onClick={() => {
                            setReportData(null)
                            setTopic('')
                            setStatus(null)
                            setReportId(null)
                        }}
                        className="mt-8 px-6 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
                    >
                        Start New Research
                    </button>
                </div>
            )}
        </div>
    )
}

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(!!getToken())
    const [view, setView] = useState('research') // 'research' or 'history'
    const [selectedReport, setSelectedReport] = useState(null)

    const handleLogin = () => setIsAuthenticated(true)

    if (!isAuthenticated) {
        return <AuthScreen onLogin={handleLogin} />
    }

    const handleLogout = () => logout()

    let Content
    if (selectedReport) {
        // Re-use logic to show report data
        Content = (
            <div className="max-w-4xl mx-auto bg-white shadow-lg rounded-lg p-8 mt-10">
                <button onClick={() => setSelectedReport(null)} className="mb-4 text-blue-500 hover:underline">&larr; Back</button>
                <h2 className="text-3xl font-bold mb-6 border-b pb-4">{selectedReport.topic}</h2>
                {/* If content is stringified JSON, parse it again or handle it. 
                 History API returns it as string usually if stored that way. 
                 In our case get_history returns it as is (string or dict). 
                 Wait, in main.py get_history, if sqlmodel returns 'content' as string, we need to parse it if we want to map over sections.
                 Actually Report model has content: Optional[str]. We store JSON string.
                 So we need to parse it. 
             */}
                {(() => {
                    try {
                        const sections = JSON.parse(selectedReport.content).sections
                        return sections.map((section, idx) => (
                            <div key={idx} className="mb-8 text-left">
                                <h3 className="text-2xl font-semibold text-gray-800 mb-3">{section.title}</h3>
                                <div className="bg-gray-50 p-6 rounded-lg border border-gray-200 text-gray-700 leading-relaxed whitespace-pre-wrap">
                                    {section.content}
                                </div>
                            </div>
                        ))
                    } catch (e) { return <p>Error parsing report content.</p> }
                })()}
            </div>
        )
    } else if (view === 'history') {
        Content = <HistoryView onViewReport={setSelectedReport} onBack={() => setView('research')} />
    } else {
        Content = <ResearchView onShowHistory={() => setView('history')} />
    }

    return (
        <div className="min-h-screen bg-gray-100 p-8 text-center font-sans">
            <header className="flex justify-between items-center mb-10 max-w-6xl mx-auto">
                <div>
                    <h1 className="text-4xl font-extrabold text-blue-600 mb-2">Research Agent AI</h1>
                    <p className="text-gray-600">Your autonomous research assistant team.</p>
                </div>
                <button onClick={handleLogout} className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
                    Logout
                </button>
            </header>
            {Content}
        </div>
    )
}

export default App
